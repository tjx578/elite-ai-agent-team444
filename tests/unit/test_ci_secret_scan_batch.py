"""Fault witnesses for the bounded object transport (execution is a separate gate)."""
from __future__ import annotations

import hashlib
import io
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

import pytest
from scanner_buffer_loader import load_subject

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def col() -> Any:
    path = ROOT / "scripts/ci/collect_secret_scan.py"
    return load_subject(path, "batch_test_subject")


def object_oid(raw: bytes, algorithm: str = "sha1") -> str:
    return hashlib.new(algorithm, b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def frame(raw: bytes, algorithm: str = "sha1") -> bytes:
    return object_oid(raw, algorithm).encode() + b" blob " + str(len(raw)).encode() + b"\n" + raw + b"\n"


def parse_frame(col: Any, data: bytes, raw: bytes, remaining: int | None = None,
                algorithm: str = "sha1") -> bytes:
    reader = col._BatchReader(io.BytesIO(data), col.MAX_TOTAL_BYTES + col.MAX_BATCH_HEADER_BYTES + 1)
    actual = col._read_batch_frame(reader, object_oid(raw, algorithm),
                                   col.MAX_TOTAL_BYTES if remaining is None else remaining)
    reader.eof()
    return actual


@pytest.mark.parametrize("raw", [b"", b"ordinary\n", b"first\nsecond\n", b"embedded\0protocol-byte"])
@pytest.mark.parametrize("algorithm", ["sha1", "sha256"])
def test_length_framing_preserves_arbitrary_payload(col: Any, raw: bytes, algorithm: str) -> None:
    # snapshot still rejects NUL input; the wire parser must not confuse it with framing.
    assert parse_frame(col, frame(raw, algorithm), raw, algorithm=algorithm) == raw


@pytest.mark.parametrize(("replacement", "code"), [
    (b"missing\n", "GIT_BATCH_HEADER"),
    (b"0" * 40 + b" blob 3\n", "GIT_BATCH_OID"),
    (b"{oid} tree 3\n", "GIT_BATCH_TYPE"),
    (b"{oid} blob -1\n", "GIT_BATCH_SIZE"),
    (b"{oid} blob 03\n", "GIT_BATCH_SIZE"),
    (b"{oid} blob x\n", "GIT_BATCH_SIZE"),
    (b"{oid} blob 9999999\n", "INPUT_SIZE_LIMIT"),
])
def test_invalid_response_header_fails_closed(col: Any, replacement: bytes, code: str) -> None:
    raw = b"abc"
    header = replacement.replace(b"{oid}", object_oid(raw).encode())
    with pytest.raises(col.ScanError, match=f"^{code}$"):
        parse_frame(col, header + raw + b"\n", raw)


@pytest.mark.parametrize(("suffix", "code"), [
    (b"a", "GIT_BATCH_TRUNCATED"),
    (b"abc", "GIT_BATCH_TRUNCATED"),
    (b"abc!", "GIT_BATCH_FRAMING"),
    (b"xyz\n", "GIT_BATCH_OBJECT_HASH"),
    (b"abc\nextra", "GIT_BATCH_TRAILING_DATA"),
])
def test_payload_hash_delimiter_truncation_and_eof(col: Any, suffix: bytes, code: str) -> None:
    raw = b"abc"
    with pytest.raises(col.ScanError, match=f"^{code}$"):
        parse_frame(col, object_oid(raw).encode() + b" blob 3\n" + suffix, raw)


def test_header_and_wire_budgets_are_explicit(col: Any) -> None:
    with pytest.raises(col.ScanError, match="^GIT_BATCH_HEADER$"):
        col._BatchReader(io.BytesIO(b"x" * (col.MAX_BATCH_HEADER_BYTES + 2)), 1000).header()
    with pytest.raises(col.ScanError, match="^GIT_BATCH_WIRE_LIMIT$"):
        col._BatchReader(io.BytesIO(b"abc"), 2).exact(3)


def test_payload_budget_rejects_before_body_read(col: Any) -> None:
    raw = b"abc"
    stream = io.BytesIO(frame(raw))
    reader = col._BatchReader(stream, 1000)
    with pytest.raises(col.ScanError, match="^SCOPE_LIMIT$"):
        col._read_batch_frame(reader, object_oid(raw), 2)
    assert stream.read() == raw + b"\n"


def test_maximum_payload_does_not_lose_budget_to_framing(col: Any) -> None:
    raw = b"x" * col.MAX_FILE_BYTES
    count = col.MAX_TOTAL_BYTES // len(raw)
    reader = col._BatchReader(io.BytesIO(frame(raw) * count),
                             col.MAX_TOTAL_BYTES + count * (col.MAX_BATCH_HEADER_BYTES + 1))
    total = 0
    for _ in range(count):
        actual = col._read_batch_frame(reader, object_oid(raw), col.MAX_TOTAL_BYTES - total)
        total += len(actual)
    reader.eof()
    assert total == col.MAX_TOTAL_BYTES
    assert reader.consumed > col.MAX_TOTAL_BYTES


class RecordingSink(io.BytesIO):
    def __init__(self) -> None:
        super().__init__()
        self.requests = b""

    def close(self) -> None:
        if not self.closed:
            self.requests = self.getvalue()
        super().close()


class StubProcess:
    def __init__(self, data: bytes, exit_code: int = 0) -> None:
        self.stdin = RecordingSink()
        self.stdout: Any = io.BytesIO(data)
        self.returncode: int | None = exit_code
        self.kill_called = False
        self.wait_called = False

    def poll(self) -> int | None:
        return self.returncode

    def kill(self) -> None:
        self.kill_called = True
        self.returncode = -9

    def wait(self, timeout: float | None = None) -> int:
        self.wait_called = True
        if self.returncode is None:
            raise subprocess.TimeoutExpired("stub", 0 if timeout is None else timeout)
        return self.returncode


def test_repeated_requested_oid_is_valid_and_counted(col: Any, monkeypatch: Any, tmp_path: Path) -> None:
    raw = b"same contents\n"
    oid = object_oid(raw)
    process = StubProcess(frame(raw) * 2)
    calls: list[tuple[Any, dict[str, Any]]] = []

    def spawn(argv: Any, **kwargs: Any) -> StubProcess:
        calls.append((argv, kwargs))
        return process

    monkeypatch.setattr(col.subprocess, "Popen", spawn)
    assert col.git_blobs(tmp_path, [oid, oid]) == [raw, raw]
    assert process.stdin.requests == (oid.encode() + b"\n") * 2
    assert process.wait_called and process.stdout.closed and process.stdin.closed
    assert len(calls) == 1 and calls[0][0][-2:] == ["cat-file", "--batch"]
    assert calls[0][1]["env"]["GIT_NO_REPLACE_OBJECTS"] == "1"
    assert calls[0][1]["env"]["GIT_NO_LAZY_FETCH"] == "1"
    assert calls[0][1]["env"]["GIT_TERMINAL_PROMPT"] == "0"
    assert calls[0][1]["env"]["GIT_OPTIONAL_LOCKS"] == "0"
    assert calls[0][1]["shell"] is False
    assert not calls[0][1].get("start_new_session", False)


def test_repeated_oid_cannot_evade_aggregate_payload_limit(col: Any, monkeypatch: Any, tmp_path: Path) -> None:
    raw = b"ab"
    process = StubProcess(frame(raw) * 2)
    monkeypatch.setattr(col, "MAX_TOTAL_BYTES", 3)
    monkeypatch.setattr(col.subprocess, "Popen", lambda *args, **kwargs: process)
    with pytest.raises(col.ScanError, match="^SCOPE_LIMIT$"):
        col.git_blobs(tmp_path, [object_oid(raw)] * 2)
    assert process.wait_called


@pytest.mark.parametrize("case", ["short", "long", "expression", "mixed", "count"])
def test_invalid_requests_never_spawn(col: Any, monkeypatch: Any, tmp_path: Path, case: str) -> None:
    requests = {"short": ["0" * 39], "long": ["0" * 65], "expression": ["HEAD:a"],
                "mixed": ["0" * 40, "0" * 64], "count": ["0" * 40] * (col.MAX_FILES + 1)}

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("invalid request reached subprocess")

    monkeypatch.setattr(col.subprocess, "Popen", forbidden)
    with pytest.raises(col.ScanError):
        col.git_blobs(tmp_path, requests[case])


def test_nonzero_exit_rejected_after_valid_frames(col: Any, monkeypatch: Any, tmp_path: Path) -> None:
    raw = b"abc"
    process = StubProcess(frame(raw), exit_code=1)
    monkeypatch.setattr(col.subprocess, "Popen", lambda *args, **kwargs: process)
    with pytest.raises(col.ScanError, match="^GIT_BATCH_EXIT_FAILURE$"):
        col.git_blobs(tmp_path, [object_oid(raw)])


class BlockingStream(io.BytesIO):
    def __init__(self) -> None:
        super().__init__()
        self.release = threading.Event()

    def readline(self, size: int | None = -1) -> bytes:
        self.release.wait(2)
        return b""


def test_timeout_kills_reaps_and_joins_reader(col: Any, monkeypatch: Any, tmp_path: Path) -> None:
    process = StubProcess(b"")
    process.returncode = None
    blocking = BlockingStream()
    process.stdout = blocking
    original_kill = process.kill

    def kill() -> None:
        original_kill()
        blocking.release.set()

    monkeypatch.setattr(process, "kill", kill)
    monkeypatch.setattr(col, "GIT_TIMEOUT", 0.05)
    monkeypatch.setattr(col.subprocess, "Popen", lambda *args, **kwargs: process)
    start = time.monotonic()
    with pytest.raises(col.ScanError, match="^GIT_BATCH_TIMEOUT$"):
        col.git_blobs(tmp_path, [object_oid(b"abc")])
    assert time.monotonic() - start < 1.5
    assert process.kill_called and process.wait_called
    assert blocking.closed and process.stdin.closed


def test_reader_error_is_sanitized_and_child_cleaned(col: Any, monkeypatch: Any, tmp_path: Path) -> None:
    class FailedStream(io.BytesIO):
        def readline(self, size: int | None = -1) -> bytes:
            raise OSError("synthetic-private-content")

    process = StubProcess(b"")
    process.stdout = FailedStream()
    monkeypatch.setattr(col.subprocess, "Popen", lambda *args, **kwargs: process)
    with pytest.raises(col.ScanError, match="^UNEXPECTED_OPERATION_FAILURE$") as failure:
        col.git_blobs(tmp_path, [object_oid(b"abc")])
    assert "synthetic-private-content" not in str(failure.value)
    assert process.wait_called and process.stdout.closed


def test_spawn_error_never_leaks_exception_text(col: Any, monkeypatch: Any, tmp_path: Path) -> None:
    def failed_spawn(*args: Any, **kwargs: Any) -> Any:
        raise OSError("synthetic-private-path")

    monkeypatch.setattr(col.subprocess, "Popen", failed_spawn)
    with pytest.raises(col.ScanError, match="^GIT_BATCH_SPAWN_FAILURE$"):
        col.git_blobs(tmp_path, [object_oid(b"abc")])


def test_partial_request_write_rejected_and_reaped(col: Any, monkeypatch: Any, tmp_path: Path) -> None:
    process = StubProcess(frame(b"abc"))
    monkeypatch.setattr(process.stdin, "write", lambda data: len(data) - 1)
    monkeypatch.setattr(col.subprocess, "Popen", lambda *args, **kwargs: process)
    with pytest.raises(col.ScanError, match="^GIT_BATCH_WRITE$"):
        col.git_blobs(tmp_path, [object_oid(b"abc")])
    assert process.wait_called and process.stdin.closed and process.stdout.closed


@pytest.mark.parametrize("fault", ["unterminated", "interior_empty", "leading_empty", "extra_terminator",
                                   "head", "tree", "tree_width", "blob", "metadata_spaces"])
def test_snapshot_rejects_invalid_inventory_before_blob_reads(col: Any, monkeypatch: Any,
                                                             tmp_path: Path, fault: str) -> None:
    head = "a" * 40
    tree = "b" * 40
    row = b"100644 blob " + object_oid(b"data").encode() + b"\tfile.txt\0"
    payload = {
        "unterminated": row[:-1], "interior_empty": row + b"\0" + row,
        "leading_empty": b"\0" + row, "extra_terminator": row + b"\0",
        "blob": row.replace(object_oid(b"data").encode(), b"z" * 40),
        "metadata_spaces": row.replace(b"100644 blob", b"100644  blob"),
    }.get(fault, row)

    def fake_git(root: Path, *args: str) -> bytes:
        if args == ("rev-parse", "--show-toplevel"):
            return str(tmp_path).encode() + b"\n"
        if args[0] == "status":
            return b""
        if args == ("rev-parse", "HEAD"):
            return ("z" * 40 if fault == "head" else head).encode() + b"\n"
        if args[0] == "rev-parse" and args[1].endswith("^{tree}"):
            assert args[1] == head + "^{tree}"
            return ("z" * 40 if fault == "tree" else "b" * 64 if fault == "tree_width" else tree).encode() + b"\n"
        assert args == ("ls-tree", "-rz", "--full-tree", head)
        return payload

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("invalid inventory reached blob transport")

    monkeypatch.setattr(col, "git", fake_git)
    monkeypatch.setattr(col, "git_blobs", forbidden)
    code = ("SNAPSHOT_HEAD_FORMAT" if fault == "head" else "SNAPSHOT_TREE_FORMAT"
            if fault in {"tree", "tree_width"} else "GIT_BATCH_OBJECT_FORMAT"
            if fault == "blob" else "SNAPSHOT_INVENTORY_FRAMING")
    with pytest.raises(col.ScanError, match=f"^{code}$"):
        col.snapshot(tmp_path)


@pytest.mark.parametrize("width", [40, 64])
def test_snapshot_empty_tree_uses_captured_head(col: Any, monkeypatch: Any, tmp_path: Path, width: int) -> None:
    head, tree = "a" * width, "b" * width
    calls = []

    def fake_git(root: Path, *args: str) -> bytes:
        calls.append(args)
        if args == ("rev-parse", "--show-toplevel"):
            return str(tmp_path).encode() + b"\n"
        if args == ("rev-parse", "HEAD"):
            return head.encode() + b"\n"
        if args == ("rev-parse", head + "^{tree}"):
            return tree.encode() + b"\n"
        assert args[0] == "status" or args == ("ls-tree", "-rz", "--full-tree", head)
        return b""

    def empty_blobs(root: Path, oids: list[str]) -> list[bytes]:
        assert oids == []
        return []

    monkeypatch.setattr(col, "git", fake_git)
    monkeypatch.setattr(col, "git_blobs", empty_blobs)
    assert col.snapshot(tmp_path) == ({"head": head, "tree": tree, "inputs": []}, {})
    assert ("ls-tree", "-rz", "--full-tree", head) in calls
