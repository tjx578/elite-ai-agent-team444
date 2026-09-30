"""Source-only loader regressions; these tests are distinct from scan acceptance."""
from __future__ import annotations

import builtins
import hashlib
import importlib.util
import os
import py_compile
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = "scripts/ci/check_secret_scan.py"
COLLECTOR = "scripts/ci/collect_secret_scan.py"
TRUSTED_SOURCE = b"BOOTSTRAP_MARKER = 'SOURCE00'\n"
POISON_SOURCE = b"BOOTSTRAP_MARKER = 'CACHEBAD'\n"


def git(root: Path, *arguments: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *arguments], stderr=subprocess.DEVNULL)


def load_validator(path: Path) -> ModuleType:
    # The test harness explicitly supplies the trusted entrypoint, source-only.
    module = ModuleType("bootstrap_fixture_validator")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)  # noqa: S102 -- load exact test-subject bytes without bytecode cache
    return module


@pytest.fixture
def repository(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "fixture@example.invalid")
    git(repo, "config", "user.name", "Bootstrap fixture")
    (repo / "scripts/ci").mkdir(parents=True)
    (repo / VALIDATOR).write_bytes((ROOT / VALIDATOR).read_bytes())
    (repo / COLLECTOR).write_bytes(TRUSTED_SOURCE)
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "trusted fixture")
    return repo, load_validator(repo / VALIDATOR), git(repo, "rev-parse", "HEAD").decode().strip()


def test_import_has_no_collector_or_git_side_effect(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Git must not run while importing the validator")
    monkeypatch.setattr(subprocess, "Popen", denied)
    gate = load_validator(ROOT / VALIDATOR)
    assert gate.collection is None
    assert gate._bootstrap_binding == {}


@pytest.mark.parametrize("mode", [py_compile.PycInvalidationMode.TIMESTAMP,
                                   py_compile.PycInvalidationMode.UNCHECKED_HASH])
def test_valid_cache_cannot_replace_verified_source(repository, tmp_path, monkeypatch, mode):
    repo, gate, head = repository
    target = repo / COLLECTOR
    poisoned = tmp_path / "poison.py"
    poisoned.write_bytes(POISON_SOURCE)
    # Equal lengths and timestamps make the alternate code a valid timestamp
    # cache; unchecked-hash mode independently covers the permissive hash case.
    assert len(TRUSTED_SOURCE) == len(POISON_SOURCE)
    stat = target.stat()
    os.utime(poisoned, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    cache = Path(importlib.util.cache_from_source(str(target)))
    cache.parent.mkdir(exist_ok=True)
    py_compile.compile(str(poisoned), cfile=str(cache), doraise=True, invalidation_mode=mode)
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    binding = gate.initialize_collection(repo, head)
    assert gate.collection.BOOTSTRAP_MARKER == "SOURCE00"
    assert binding["sources"][COLLECTOR]["raw_sha256"] == hashlib.sha256(TRUSTED_SOURCE).hexdigest()
    assert cache.exists()


@pytest.mark.parametrize("path", [VALIDATOR, COLLECTOR])
def test_modified_source_rejected_before_helper(repository, path):
    repo, gate, head = repository
    with (repo / path).open("ab") as stream:
        stream.write(b"# unreviewed change\n")
    with pytest.raises(gate.BootstrapError, match="BOOTSTRAP_DIRTY_TREE"):
        gate.initialize_collection(repo, head)
    assert gate.collection is None


def test_wrong_expected_commit_rejected_before_helper(repository):
    repo, gate, _ = repository
    with pytest.raises(gate.BootstrapError, match="BOOTSTRAP_HEAD_MISMATCH"):
        gate.initialize_collection(repo, "0" * 40)
    assert gate.collection is None


def test_final_head_drift_rejected_before_helper(repository, monkeypatch):
    repo, gate, head = repository
    actual = gate._bootstrap_git
    reads = 0
    def drifting(root, args, deadline, limit=gate.BOOTSTRAP_MAX_SOURCE_BYTES, *, own_group=True):
        nonlocal reads
        if args == ("rev-parse", "HEAD"):
            reads += 1
            if reads == 2:
                return b"0" * len(head) + b"\n"
        return actual(root, args, deadline, limit, own_group=own_group)
    monkeypatch.setattr(gate, "_bootstrap_git", drifting)
    with pytest.raises(gate.BootstrapError, match="BOOTSTRAP_HEAD_DRIFT"):
        gate.initialize_collection(repo, head)
    assert gate.collection is None


def test_git_body_must_match_full_blob_oid(repository, monkeypatch):
    repo, gate, head = repository
    actual = gate._bootstrap_git
    def corrupted(root, args, deadline, limit=gate.BOOTSTRAP_MAX_SOURCE_BYTES, *, own_group=True):
        raw = actual(root, args, deadline, limit, own_group=own_group)
        if args[:2] == ("cat-file", "blob") and raw == TRUSTED_SOURCE:
            return POISON_SOURCE
        return raw
    monkeypatch.setattr(gate, "_bootstrap_git", corrupted)
    with pytest.raises(gate.BootstrapError, match="BOOTSTRAP_BLOB_MISMATCH"):
        gate.initialize_collection(repo, head)
    assert gate.collection is None


def test_path_replacement_after_verification_cannot_change_compiled_buffer(repository, monkeypatch):
    repo, gate, head = repository
    def swap_before_compile(source, filename, mode, *args, **kwargs):
        if filename == str(repo / COLLECTOR):
            (repo / COLLECTOR).write_bytes(POISON_SOURCE)
        return builtins.compile(source, filename, mode, *args, **kwargs)
    monkeypatch.setattr(gate, "compile", swap_before_compile, raising=False)
    gate.initialize_collection(repo, head)
    assert (repo / COLLECTOR).read_bytes() == POISON_SOURCE
    assert gate.collection.BOOTSTRAP_MARKER == "SOURCE00"
    assert gate._verified_sources[COLLECTOR] == TRUSTED_SOURCE
    # A subsequent bootstrap/snapshot must reject the changed checkout.
    with pytest.raises(gate.BootstrapError, match="BOOTSTRAP_DIRTY_TREE"):
        gate.initialize_collection(repo, head)


def test_crlf_worktree_preserves_raw_git_buffer_binding(repository):
    repo, gate, head = repository
    git(repo, "config", "core.autocrlf", "true")
    for path in (VALIDATOR, COLLECTOR):
        raw = (repo / path).read_bytes()
        (repo / path).write_bytes(raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    binding = gate.initialize_collection(repo, head)
    assert gate._verified_sources[COLLECTOR] == TRUSTED_SOURCE
    assert binding["sources"][COLLECTOR]["byte_length"] == len(TRUSTED_SOURCE)
    assert binding["validator_trust"] == "CALLER_TRUSTED_ENTRYPOINT"


def test_bootstrap_failure_removes_stale_receipt(repository, monkeypatch, capsys):
    repo, gate, _ = repository
    stale = repo / "secret-scan-receipt.json"
    stale.write_text('{"status":"PASS"}', encoding="utf-8")
    (repo / COLLECTOR).write_bytes(POISON_SOURCE)
    monkeypatch.chdir(repo)
    assert gate.main(["--scan"]) == 1
    assert not stale.exists()
    output = capsys.readouterr()
    assert "SOURCE00" not in output.out + output.err
    assert "CACHEBAD" not in output.out + output.err
    assert output.err == ""


def replace_git_with_python(command, script):
    # Preserve the Windows job-assignment trampoline; replace only its Git leaf.
    git_index = command.index("git")
    return [*command[:git_index], sys.executable, "-c", script]


def test_bootstrap_output_limit_terminates_child(repository, monkeypatch):
    repo, gate, _ = repository
    popen = subprocess.Popen
    children = []
    def oversized(command, **kwargs):
        child = popen(replace_git_with_python(command, "import sys,time; sys.stdout.buffer.write(b'x'*8192); sys.stdout.flush(); time.sleep(30)"), **kwargs)
        children.append(child)
        return child
    monkeypatch.setattr(gate.subprocess, "Popen", oversized)
    with pytest.raises(gate.BootstrapError, match="BOOTSTRAP_GIT_OUTPUT"):
        gate._bootstrap_git(repo, ("rev-parse", "HEAD"), time.monotonic() + 2, limit=16)
    assert len(children) == 1 and children[0].poll() is not None


def test_bootstrap_timeout_terminates_child(repository, monkeypatch):
    repo, gate, _ = repository
    popen = subprocess.Popen
    children = []
    def stalled(command, **kwargs):
        child = popen(replace_git_with_python(command, "import time; time.sleep(30)"), **kwargs)
        children.append(child)
        return child
    monkeypatch.setattr(gate.subprocess, "Popen", stalled)
    with pytest.raises(gate.BootstrapError, match="BOOTSTRAP_TIMEOUT"):
        gate._bootstrap_git(repo, ("rev-parse", "HEAD"), time.monotonic() + 0.1)
    assert len(children) == 1 and children[0].poll() is not None


def test_reader_start_failure_terminates_owned_process(repository, monkeypatch):
    repo, gate, _ = repository
    popen = subprocess.Popen
    children = []
    def stalled(command, **kwargs):
        child = popen(replace_git_with_python(command, "import time; time.sleep(30)"), **kwargs)
        children.append(child)
        return child
    def cannot_start(self):
        raise RuntimeError("PRIVATE_START_FAILURE")
    monkeypatch.setattr(gate.subprocess, "Popen", stalled)
    monkeypatch.setattr(threading.Thread, "start", cannot_start)
    with pytest.raises(gate.BootstrapError, match="^BOOTSTRAP_GIT_FAILURE$"):
        gate._bootstrap_git(repo, ("rev-parse", "HEAD"), time.monotonic() + 2)
    assert len(children) == 1 and children[0].poll() is not None
    assert children[0].stdout.closed


@pytest.mark.skipif(os.name == "nt", reason="POSIX process-group inheritance contract")
def test_internal_bootstrap_inherits_outer_process_group(repository, monkeypatch):
    repo, gate, _ = repository
    popen = subprocess.Popen
    observed = []
    def report_group(command, **kwargs):
        observed.append(kwargs["start_new_session"])
        return popen(replace_git_with_python(command, "import os; print(os.getpgrp())"), **kwargs)
    monkeypatch.setattr(gate.subprocess, "Popen", report_group)
    raw = gate._bootstrap_git(repo, ("rev-parse", "HEAD"), time.monotonic() + 2, own_group=False)
    assert observed == [False]
    assert int(raw) == os.getpgrp()


@pytest.mark.skipif(os.name == "nt", reason="POSIX parent group termination proof")
def test_parent_bootstrap_terminates_descendant(repository, monkeypatch, tmp_path):
    repo, gate, _ = repository
    marker = tmp_path / "descendant.pid"
    popen = subprocess.Popen
    children = []
    script = ("import subprocess,sys,time,pathlib; "
              "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); "
              f"pathlib.Path({str(marker)!r}).write_text(str(p.pid)); time.sleep(30)")
    def descendant(command, **kwargs):
        child = popen(replace_git_with_python(command, script), **kwargs)
        children.append(child)
        return child
    monkeypatch.setattr(gate.subprocess, "Popen", descendant)
    with pytest.raises(gate.BootstrapError, match="BOOTSTRAP_TIMEOUT"):
        gate._bootstrap_git(repo, ("rev-parse", "HEAD"), time.monotonic() + 2)
    assert marker.exists(), "fixture descendant must have started before timeout"
    assert children[0].poll() is not None
    descendant_pid = int(marker.read_text())
    # Linux orphan zombies have exited but await their adopter's reap. Other
    # POSIX systems should remove the PID promptly; neither may remain running.
    deadline = time.monotonic() + 1
    while time.monotonic() < deadline:
        try:
            os.kill(descendant_pid, 0)
        except ProcessLookupError:
            return
        status = Path(f"/proc/{descendant_pid}/stat")
        if status.exists() and status.read_text().rsplit(")", 1)[1].split()[0] == "Z":
            return
        time.sleep(0.01)
    pytest.fail("bootstrap descendant remained live after parent cleanup")


@pytest.mark.skipif(os.name != "nt", reason="Windows parent job termination proof")
def test_parent_bootstrap_job_terminates_descendant(repository, monkeypatch, tmp_path):
    repo, gate, _ = repository
    marker = tmp_path / "descendant.pid"
    popen = subprocess.Popen
    job_type = gate.WindowsJob
    active_counts = []
    class ObservedJob(job_type):
        def active(self):
            count = super().active()
            active_counts.append(count)
            return count
    script = ("import subprocess,sys,time,pathlib; "
              "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); "
              f"pathlib.Path({str(marker)!r}).write_text(str(p.pid)); time.sleep(30)")
    def descendant(command, **kwargs):
        return popen(replace_git_with_python(command, script), **kwargs)
    monkeypatch.setattr(gate, "WindowsJob", ObservedJob)
    monkeypatch.setattr(gate.subprocess, "Popen", descendant)
    with pytest.raises(gate.BootstrapError, match="BOOTSTRAP_TIMEOUT"):
        gate._bootstrap_git(repo, ("rev-parse", "HEAD"), time.monotonic() + 3)
    assert marker.exists(), "fixture descendant must have started inside the job"
    assert active_counts and active_counts[-1] == 0
