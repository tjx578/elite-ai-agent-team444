"""Supervisor setup faults must retain deadline and descendant ownership."""
from __future__ import annotations

import io
import types
from pathlib import Path
from typing import Any

import pytest
from scanner_buffer_loader import load_subject

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def subject() -> Any:
    modules = []
    for name in ("collect_secret_scan", "check_secret_scan"):
        path = ROOT / "scripts/ci" / (name + ".py")
        module = load_subject(path, name)
        modules.append(module)
    modules[1].collection = modules[0]
    return modules[1]


class Process:
    pid = 12345

    def __init__(self) -> None:
        self.stdin = io.BytesIO()
        self.stdout: Any = io.BytesIO(b"result")
        self.stderr: Any = io.BytesIO()
        self.returncode: int | None = None
        self.killed = False
        self.reaped = False

    def poll(self) -> int | None:
        return self.returncode

    def kill(self) -> None:
        self.killed = True
        self.returncode = -9

    def wait(self, timeout: float) -> int:
        assert self.returncode is not None
        self.reaped = True
        return self.returncode


class Thread:
    """Synchronous pipe drain isolates setup ordering without OS timing noise."""

    def __init__(self, target: Any, args: Any, daemon: bool) -> None:
        self.target, self.args = target, args
        self.started = False
        self.joined = False

    def start(self) -> None:
        self.started = True
        self.target(*self.args)

    def is_alive(self) -> bool:
        return False

    def join(self, timeout: float) -> None:
        assert self.started
        self.joined = True


@pytest.fixture
def harness(subject: Any, monkeypatch: Any) -> Any:
    process = Process()
    killed_groups = []
    threads = []

    def thread(**kwargs: Any) -> Thread:
        item = Thread(**kwargs)
        threads.append(item)
        return item

    monkeypatch.setattr(subject, "subprocess", types.SimpleNamespace(
        Popen=lambda *args, **kwargs: process, PIPE=-1, DEVNULL=-3))
    monkeypatch.setattr(subject, "os", types.SimpleNamespace(
        name="posix", killpg=lambda pid, sig: killed_groups.append(pid)))
    # This fixture models POSIX even when hosted on Windows, whose signal
    # module has no SIGKILL. Bind the modeled signal alongside modeled os.
    monkeypatch.setattr(subject, "signal", types.SimpleNamespace(SIGKILL=9))
    monkeypatch.setattr(subject, "threading", types.SimpleNamespace(
        Thread=thread, Event=subject.threading.Event))
    return subject, process, threads, killed_groups


@pytest.mark.parametrize("failed_start", [1, 2])
def test_thread_start_failure_cleans_child_and_started_readers(harness: Any, monkeypatch: Any, failed_start: int) -> None:
    gate, child, threads, groups = harness
    original = Thread.start
    calls = 0

    def start(self: Thread) -> None:
        nonlocal calls
        calls += 1
        if calls == failed_start:
            raise RuntimeError("synthetic thread capacity failure")
        original(self)

    monkeypatch.setattr(Thread, "start", start)
    with pytest.raises(RuntimeError, match="synthetic thread capacity failure"):
        gate.supervised(["fixture"], ROOT)
    assert groups == [child.pid] and child.killed and child.reaped
    assert all(item.joined for item in threads if item.started)
    assert child.stdin.closed and child.stdout.closed and child.stderr.closed


@pytest.mark.parametrize("pipe", ["stdout", "stderr"])
def test_missing_pipe_cleans_child(harness: Any, pipe: str) -> None:
    gate, child, _, groups = harness
    getattr(child, pipe).close()
    setattr(child, pipe, None)
    with pytest.raises(gate.collection.ScanError, match="^CHILD_PIPE$"):
        gate.supervised(["fixture"], ROOT)
    assert groups == [child.pid] and child.killed and child.reaped
    assert child.stdin.closed


@pytest.mark.parametrize("phase", ["spawn", "complete"])
def test_deadline_includes_spawn_and_completed_output(harness: Any, monkeypatch: Any, phase: str) -> None:
    gate, child, _, groups = harness
    child.returncode = 0
    clock = iter([0.0, 120.0] if phase == "spawn" else [0.0, 0.5, 120.0])
    monkeypatch.setattr(gate, "time", types.SimpleNamespace(monotonic=lambda: next(clock)))
    with pytest.raises(gate.collection.ScanError, match="^COLLECTOR_TIMEOUT$"):
        gate.supervised(["fixture"], ROOT, timeout=120.0)
    assert groups == [child.pid] and child.reaped
    assert child.stdout.closed and child.stderr.closed


@pytest.mark.parametrize("fault", ["assignment", "stdin", "spawn"])
def test_windows_setup_failure_closes_job(harness: Any, monkeypatch: Any, fault: str) -> None:
    gate, child, _, _ = harness
    closed = []

    class Job:
        def assign(self, pid: int) -> None:
            if fault == "assignment":
                raise RuntimeError("synthetic assignment failure")

        def close(self) -> None:
            closed.append(True)

    monkeypatch.setattr(gate, "os", types.SimpleNamespace(name="nt"))
    monkeypatch.setattr(gate, "WindowsJob", Job)
    if fault == "stdin":
        child.stdin.close()
        child.stdin = None
    if fault == "spawn":
        def fail_spawn(*args: Any, **kwargs: Any) -> None:
            raise RuntimeError("synthetic spawn failure")
        monkeypatch.setattr(gate.subprocess, "Popen", fail_spawn)
    with pytest.raises((RuntimeError, gate.collection.ScanError)):
        gate.supervised(["fixture"], ROOT)
    assert closed == [True]
    if fault != "spawn":
        assert child.killed and child.reaped and child.stdout.closed and child.stderr.closed


def test_success_preserves_output_and_cleanup(harness: Any) -> None:
    gate, child, threads, groups = harness
    child.returncode = 0
    assert gate.supervised(["fixture"], ROOT) == b"result"
    assert groups == [child.pid] and child.reaped
    assert all(item.joined for item in threads)
    assert child.stdin.closed and child.stdout.closed and child.stderr.closed


@pytest.mark.parametrize("fault", ["group", "join", "stdin"])
def test_cleanup_failure_still_attempts_remaining_cleanup(harness: Any, monkeypatch: Any, fault: str) -> None:
    gate, child, threads, _ = harness
    child.returncode = 0

    class UnprintableFailure(Exception):
        def __str__(self) -> str:
            raise AssertionError("cleanup error must not be formatted")

    def fail(*args: Any, **kwargs: Any) -> None:
        raise UnprintableFailure()

    if fault == "group":
        monkeypatch.setattr(gate.os, "killpg", fail)
    elif fault == "join":
        original = Thread.join

        def join(self: Thread, timeout: float) -> None:
            original(self, timeout)
            if self is threads[0]:
                fail()

        monkeypatch.setattr(Thread, "join", join)
    else:
        monkeypatch.setattr(child.stdin, "close", fail)
    with pytest.raises(gate.collection.ScanError, match="^PROCESS_PIPE_TERMINATION_UNPROVEN$"):
        gate.supervised(["fixture"], ROOT)
    assert child.reaped
    assert all(item.joined for item in threads)
    assert child.stdout.closed and child.stderr.closed
