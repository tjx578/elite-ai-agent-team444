"""Fail-closed batch cleanup retains every ordinary-error cleanup attempt."""
from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pytest
from test_ci_secret_scan_batch import StubProcess, col, frame, object_oid

__all__ = ["col"]


class UnformattableFailure(Exception):
    def __str__(self) -> str:
        raise AssertionError("operation failures must not be formatted")


@pytest.mark.parametrize("failure_type", [LookupError, UnformattableFailure])
def test_arbitrary_spawn_failure_has_fixed_public_code(
    col: Any, monkeypatch: Any, tmp_path: Path, failure_type: type[Exception],
) -> None:
    def spawn(*args: Any, **kwargs: Any) -> Any:
        raise failure_type("synthetic-private-content")

    monkeypatch.setattr(col.subprocess, "Popen", spawn)
    with pytest.raises(col.ScanError, match="^GIT_BATCH_SPAWN_FAILURE$") as error:
        col.git_blobs(tmp_path, [object_oid(b"abc")])
    assert error.value.__suppress_context__


def test_process_control_during_spawn_propagates(
    col: Any, monkeypatch: Any, tmp_path: Path,
) -> None:
    class StopRequested(BaseException):
        pass

    def spawn(*args: Any, **kwargs: Any) -> Any:
        raise StopRequested

    monkeypatch.setattr(col.subprocess, "Popen", spawn)
    with pytest.raises(StopRequested):
        col.git_blobs(tmp_path, [])


@pytest.mark.parametrize(("failure_on", "code"), [
    (1, "UNEXPECTED_OPERATION_FAILURE"), (2, "GIT_BATCH_CLOSE_FAILURE"),
])
def test_reader_close_failure_still_closes_other_pipe_and_reaps(
    col: Any, monkeypatch: Any, tmp_path: Path, failure_on: int, code: str,
) -> None:
    class FailedClose(io.BytesIO):
        calls = 0

        def close(self) -> None:
            self.calls += 1
            super().close()
            if self.calls >= failure_on:
                raise UnformattableFailure("synthetic-private-content")

    raw = b"abc"
    process = StubProcess(frame(raw))
    sink = FailedClose()
    monkeypatch.setattr(process, "stdin", sink)
    monkeypatch.setattr(col.subprocess, "Popen", lambda *args, **kwargs: process)
    with pytest.raises(col.ScanError, match=f"^{code}$"):
        col.git_blobs(tmp_path, [object_oid(raw)])
    assert sink.calls == 2  # Protocol close and finally cleanup both attempted.
    assert process.stdout.closed and process.wait_called


def test_unstarted_reader_close_failure_still_closes_other_pipe(
    col: Any, monkeypatch: Any, tmp_path: Path,
) -> None:
    process = StubProcess(b"")
    closes: list[str] = []

    def fail_close() -> None:
        closes.append("stdin")
        raise UnformattableFailure("synthetic-private-content")

    class UnstartedReader:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def start(self) -> None:
            raise LookupError("synthetic-start-failure")

        def join(self, timeout: float) -> None:
            raise AssertionError("cannot join an unstarted reader")

    monkeypatch.setattr(process.stdin, "close", fail_close)
    monkeypatch.setattr(col.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(col.threading, "Thread", UnstartedReader)
    with pytest.raises(col.ScanError, match="^GIT_BATCH_CLEANUP_FAILURE$"):
        col.git_blobs(tmp_path, [])
    assert closes == ["stdin"]
    assert process.stdout.closed and process.wait_called


def test_kill_failure_does_not_skip_reader_join(
    col: Any, monkeypatch: Any, tmp_path: Path,
) -> None:
    process = StubProcess(b"")
    process.returncode = None
    operations: list[str] = []

    def fail_kill() -> None:
        operations.append("kill")
        raise UnformattableFailure("synthetic-private-content")

    class StartedReader:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def start(self) -> None:
            operations.append("start")

        def join(self, timeout: float) -> None:
            operations.append("join")

        def is_alive(self) -> bool:
            return False

    monkeypatch.setattr(process, "kill", fail_kill)
    monkeypatch.setattr(col.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(col.threading, "Thread", StartedReader)
    monkeypatch.setattr(col, "GIT_TIMEOUT", 0)
    with pytest.raises(col.ScanError, match="^GIT_BATCH_CLEANUP_FAILURE$"):
        col.git_blobs(tmp_path, [])
    assert operations == ["start", "kill", "join"]
    process.stdin.close()
    process.stdout.close()
