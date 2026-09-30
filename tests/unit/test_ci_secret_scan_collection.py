"""Real collector, source coverage, parity and fault-injection specifications.

These tests run only after separate execution authorization. No supplied report is
accepted by the production CLI; mutations below exercise the pure Gate A boundary.
"""
from __future__ import annotations

import copy
import importlib.util
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("secret_collection_tests", ROOT / "scripts/ci/check_secret_scan.py")
assert SPEC is not None and SPEC.loader is not None
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)
COL: Any = None


@pytest.fixture(scope="module", autouse=True)
def initialize_verified_collection():
    """Load the exact committed collector only after the validator binds its bytes."""
    global COL
    GATE.initialize_collection(ROOT)
    COL = GATE.collection


def repository(path, files):
    path.mkdir(exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    for name, raw in files.items():
        target = path / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    subprocess.run(["git", "-C", str(path), "-c", "core.autocrlf=false", "add", "."], check=True)
    subprocess.run(["git", "-C", str(path), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"], check=True)
    return path


def collect_child(root, nonce="a" * 32, *, utf8_env=None):
    # Isolated algorithm fixture: this deliberately does not qualify production
    # bootstrap/worker acceptance. The full-head CLI test below covers that path.
    command = [sys.executable, "-X", "utf8", str(ROOT / "scripts/ci/collect_secret_scan.py"), "--root", str(root), "--nonce", nonce]
    if utf8_env is None:
        return COL.parse(GATE.supervised(command, root))
    result = subprocess.run(command, cwd=root, env=utf8_env, capture_output=True, timeout=120, check=False)
    assert result.returncode == 0 and not result.stderr
    return COL.parse(result.stdout)


@pytest.fixture
def complete(tmp_path):
    root = repository(tmp_path, {"hello.txt": b"Hello world\n", "empty.txt": b""})
    receipt = collect_child(root)
    source, blobs = COL.snapshot(root)
    config = COL.configuration(); config["utf8_mode"] = 1
    return receipt, source, blobs, config, "a" * 32


def test_real_clean_zero_findings_has_complete_gate_a(complete):
    assert GATE.gate_a(*complete) == []
    assert GATE.classify([], complete[2]) == (0, 0)
    assert len(complete[0]["processed_inputs"]) == 2


@pytest.mark.parametrize("case", ["empty_report", "missing", "duplicate", "not_processed", "boolean_size", "nonce", "tree", "blob", "config", "completion", "detector", "calls", "mapping", "pass", "extra_field"])
def test_gate_a_rejects_missing_or_forged_completion(complete, case):
    receipt, source, blobs, config, nonce = copy.deepcopy(complete)
    if case == "empty_report": receipt = {"results": {}}
    elif case == "missing": receipt["processed_inputs"].pop()
    elif case == "duplicate": receipt["processed_inputs"][1] = receipt["processed_inputs"][0]
    elif case == "not_processed": receipt["processed_inputs"][0]["input_status"] = "READABLE"
    elif case == "boolean_size": receipt["processed_inputs"][0]["byte_length"] = False
    elif case == "nonce": receipt["run_nonce"] = "b" * 32
    elif case == "tree": receipt["source"]["tree"] = "0" * 40
    elif case == "blob": receipt["processed_inputs"][0]["blob_oid"] = "0" * 40
    elif case == "config": receipt["config"]["filters"] = ["unexpected"]
    elif case == "completion": receipt["completion"] = "STARTED"
    elif case == "detector": receipt["processed_inputs"][0]["required_detectors"].pop()
    elif case == "calls": receipt["processed_inputs"][0]["passes"][0]["detectors"][0]["calls"] = 0
    elif case == "mapping": receipt["processed_inputs"][0]["passes"][0]["line_numbers"].append(1)
    elif case == "pass": receipt["processed_inputs"][0]["passes"] = []
    elif case == "extra_field": receipt["unexpected"] = "value"
    with pytest.raises((ValueError, TypeError)):
        GATE.gate_a(receipt, source, blobs, config, nonce)


def test_real_detector_records_repeated_locations_without_secret_values():
    value = "synthetic" + "-only-" + "candidate"
    raw = ('password = "' + value + '"\n') * 2
    with COL.engine() as (plugins, transforms):
        _, results = COL.scan_text("fixture.py", raw.encode(), plugins, transforms)
    keywords = [r for r in results if r["type"] == "Secret Keyword"]
    assert {r["line"] for r in keywords} == {1, 2}
    assert len({r["fingerprint"] for r in keywords}) == 1
    assert value.encode() not in COL.canonical(results)


def test_every_real_plugin_is_invoked_for_each_line(monkeypatch):
    with COL.engine() as (plugins, _):
        counts = {}
        for plugin in plugins:
            name = type(plugin).__name__; original = plugin.analyze_line
            def spy(*args, _name=name, _original=original, **kwargs):
                counts[_name] = counts.get(_name, 0) + 1
                return _original(*args, **kwargs)
            monkeypatch.setattr(plugin, "analyze_line", spy)
        row, _ = COL.scan_text("hello.txt", b"Hello\nworld\n", plugins, [])
        assert len(counts) == 27 and set(counts.values()) == {2}
        assert len(row["passes"][0]["detectors"]) == 27


def test_detector_iterator_failure_never_returns_completion():
    class Broken:
        secret_type = "Syn" + "thetic"
        def analyze_line(self, **kwargs):
            yield from ()
            raise RuntimeError("private synthetic payload must not escape")
    with pytest.raises(RuntimeError):
        COL.scan_text("hello.txt", b"Hello\n", [Broken()], [])


@pytest.mark.parametrize("raw", [b"\xff", b"a\0b"])
def test_decode_and_binary_fail_closed(tmp_path, raw):
    root = repository(tmp_path, {"bad.txt": raw})
    with pytest.raises(ValueError): COL.snapshot(root)


def test_missing_read_and_dirty_source_fail(tmp_path):
    root = repository(tmp_path, {"hello.txt": b"Hello\n"})
    (root / "hello.txt").unlink()
    with pytest.raises(ValueError): COL.snapshot(root)


def test_working_file_read_error_after_clean_inventory_fails(tmp_path, monkeypatch):
    root = repository(tmp_path, {"hello.txt": b"Hello\n"})
    real_open = Path.open
    calls = []
    def fail_read(path, *args, **kwargs):
        if path == root / "hello.txt":
            calls.append(path)
            raise OSError("synthetic working read failure")
        return real_open(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", fail_read)
    with pytest.raises(OSError):
        COL.snapshot(root)
    assert calls == [root / "hello.txt"]


def test_tracked_new_file_is_not_silently_omitted(tmp_path):
    root = repository(tmp_path, {"hello.txt": b"Hello\n"})
    before, _ = COL.snapshot(root)
    (root / "later.txt").write_text("Later\n")
    subprocess.run(["git", "-C", str(root), "add", "later.txt"], check=True)
    with pytest.raises(ValueError): COL.snapshot(root)
    assert {x["path"] for x in before["inputs"]} == {"hello.txt"}


@pytest.mark.parametrize("path", ["../x", "x/../y", "/x", "x\\y", "C:x", "x//y", "x\n"])
def test_path_aliases_fail(path):
    with pytest.raises(ValueError): COL.safe_path(path)


@pytest.mark.parametrize("code,timeout,limit", [("import time; time.sleep(5)", 0.1, 1024), ("raise SystemExit(7)", 10, 1024), ("import sys; sys.stdout.write('x'*50000)", 10, 1024), ("import sys; sys.stderr.write('x'*50000)", 10, 1024)])
def test_supervisor_faults(tmp_path, code, timeout, limit):
    with pytest.raises(ValueError):
        GATE.supervised([sys.executable, "-c", code], tmp_path, timeout=timeout, limit=limit)


def test_collector_cli_sanitizes_internal_error(tmp_path):
    root = repository(tmp_path, {"bad.txt": b"\xff"})
    result = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/ci/collect_secret_scan.py"), "--root", str(root), "--nonce", "a" * 32], capture_output=True, check=False)
    assert result.returncode != 0
    assert result.stdout == b'{"error":"COLLECTION_FAILED"}' and not result.stderr


def test_explicit_utf8_beats_locale_environment(tmp_path):
    import os
    root = repository(tmp_path, {"hello.txt": "Halo dunia — evidence\n".encode()})
    env = os.environ.copy(); env.update(PYTHONUTF8="0", PYTHONIOENCODING="cp1252")
    first = collect_child(root)
    second = collect_child(root, utf8_env=env)
    assert first == second


@pytest.mark.parametrize("filename", ["fixture.py", "fixture.yaml", "fixture.ini"])
def test_adapter_covers_upstream_no_verify_fixture(tmp_path, filename):
    from detect_secrets.core.scan import scan_file
    value = "synthetic" + "-only-" + "candidate"
    text = ('password: "' + value + '"\n') if filename.endswith("yaml") else ('password = "' + value + '"\n')
    target = tmp_path / filename; target.write_text(text, encoding="utf-8")
    with COL.engine() as (plugins, transforms):
        _, ours = COL.scan_text(filename, text.encode(), plugins, transforms)
        theirs = list(scan_file(str(target)))
    our_keys = {(r["line"], r["type"], r["fingerprint"]) for r in ours}
    assert theirs
    assert {(r.line_number, r.type, r.secret_hash) for r in theirs} <= our_keys


def test_pragma_and_lockfile_suppression_is_not_implicit():
    value = "synthetic" + "-only-" + "candidate"
    text = ('password = "' + value + '" # pragma: allowlist secret\n').encode()
    with COL.engine() as (plugins, transforms):
        _, rows = COL.scan_text("fixture.lock", text, plugins, transforms)
    assert rows and GATE.classify(rows, {"fixture.lock": text})[1] > 0


def test_final_line_sentinel_is_drained():
    from detect_secrets.core.potential_secret import PotentialSecret
    calls = []
    class Sentinel:
        secret_type = "Syn" + "thetic"
        def analyze_line(self, filename, line, line_number, **kwargs):
            calls.append(line_number)
            if line_number == 3:
                yield PotentialSecret(type=self.secret_type, filename=filename, secret="E" + "ND", line_number=3)
    row, found = COL.scan_text("sentinel.txt", b"start\nmiddle\nEND\n", [Sentinel()], [])
    assert calls == [1, 2, 3]
    assert row["passes"][0]["detectors"][0]["calls"] == 3
    assert found[0]["line"] == 3


def test_unreadable_blob_fails_not_excluded(tmp_path, monkeypatch):
    root = repository(tmp_path, {"hello.txt": b"Hello\n"})
    def broken(root, oids):
        raise COL.ScanError("GIT_BATCH_READ_FAILURE")
    monkeypatch.setattr(COL, "git_blobs", broken)
    with pytest.raises(COL.ScanError, match="GIT_BATCH_READ_FAILURE"):
        COL.snapshot(root)


@pytest.mark.parametrize("mode", ["120000", "160000"])
def test_unsupported_git_modes_fail(tmp_path, monkeypatch, mode):
    root = repository(tmp_path, {"hello.txt": b"Hello\n"})
    real = COL.git
    def altered(root, *args):
        result = real(root, *args)
        if args and args[0] == "ls-tree":
            return result.replace(b"100644 blob", (mode + " " + ("commit" if mode == "160000" else "blob")).encode(), 1)
        return result
    monkeypatch.setattr(COL, "git", altered)
    with pytest.raises(ValueError, match="UNSUPPORTED_GIT_MODE"): COL.snapshot(root)


def test_case_collisions_fail(tmp_path, monkeypatch):
    root = repository(tmp_path, {"hello.txt": b"Hello\n"})
    real = COL.git
    def duplicate(root, *args):
        result = real(root, *args)
        if args and args[0] == "ls-tree":
            return result + result.replace(b"hello.txt", b"HELLO.txt")
        return result
    monkeypatch.setattr(COL, "git", duplicate)
    with pytest.raises(ValueError, match="DUPLICATE_PATH"): COL.snapshot(root)


def test_changed_plugin_config_is_rejected(monkeypatch):
    changed = copy.deepcopy(COL.PLUGIN_CONFIG)
    changed[0]["name"] = "UnknownDetector"
    monkeypatch.setattr(COL, "PLUGIN_CONFIG", changed)
    with pytest.raises(TypeError), COL.engine():
        pytest.fail("unknown detector cannot complete")


def test_candidates_in_child_stdout_stderr_never_render(tmp_path, capsys):
    marker = "private" + "-synthetic-" + "candidate"
    code = "import sys; sys.stdout.write(" + repr(marker) + "); sys.stderr.write(" + repr(marker) + "); raise SystemExit(2)"
    with pytest.raises(ValueError):
        GATE.supervised([sys.executable, "-c", code], tmp_path)
    captured = capsys.readouterr()
    assert marker not in captured.out + captured.err


def test_source_drift_between_inventory_and_end_fails(tmp_path, monkeypatch):
    root = repository(tmp_path, {"hello.txt": b"Hello\n"})
    real = COL.git
    calls = 0
    def drift(root, *args):
        nonlocal calls
        result = real(root, *args)
        if args == ("rev-parse", "HEAD"):
            calls += 1
            if calls == 2: return b"0" * 40 + b"\n"
        return result
    monkeypatch.setattr(COL, "git", drift)
    with pytest.raises(ValueError, match="SNAPSHOT_DRIFT"): COL.snapshot(root)


@pytest.mark.parametrize("dimension", ["source", "config"])
def test_worker_collector_binding_rejects_independent_drift(complete, dimension):
    """A completed S1 receipt cannot satisfy a different independently bound S0."""
    receipt, source, blobs, config, nonce = complete
    worker_source = copy.deepcopy(source)
    worker_config = copy.deepcopy(config)
    if dimension == "source":
        worker_source["head"] = "0" * 40
    else:
        worker_config["filters"] = ["unexpected"]
    category = "SOURCE_MISMATCH" if dimension == "source" else "CONFIG_MISMATCH"
    with pytest.raises(COL.ScanError, match=category):
        GATE.gate_a(receipt, worker_source, blobs, worker_config, nonce)


@pytest.mark.parametrize("dimension", ["source", "config"])
def test_collector_rejects_post_detection_drift_before_completion(tmp_path, monkeypatch, dimension):
    """Inject different fresh S2/config observations after the real fixture scan."""
    root = repository(tmp_path, {"hello.txt": b"Hello\n"})
    source, blobs = COL.snapshot(root)
    config = COL.configuration()
    config["utf8_mode"] = 1
    after = copy.deepcopy(source)
    after_config = copy.deepcopy(config)
    if dimension == "source":
        after["tree"] = "0" * 40
    else:
        after_config["filters"] = ["unexpected"]
    snapshots = iter([(source, blobs), (after, blobs)])
    configurations = iter([config, after_config])
    observed = []
    def next_snapshot(bound_root):
        assert bound_root == root
        observed.append("snapshot")
        return next(snapshots)
    monkeypatch.setattr(COL, "snapshot", next_snapshot)
    monkeypatch.setattr(COL, "configuration", lambda: next(configurations))
    monkeypatch.setattr(COL, "sys", SimpleNamespace(flags=SimpleNamespace(utf8_mode=1)))
    with pytest.raises(COL.ScanError, match="COLLECTION_DRIFT"):
        COL.collect(root, "a" * 32)
    assert observed == ["snapshot", "snapshot"]


@pytest.mark.parametrize("dimension", ["source", "config"])
def test_worker_rejects_final_drift_before_returning_acceptance(monkeypatch, dimension):
    """Isolate the S3 guard; mocked child/Gate A are not full-scan evidence."""
    source, blobs = COL.snapshot(ROOT)
    config = COL.configuration()
    config["utf8_mode"] = 1
    after = copy.deepcopy(source)
    after_config = copy.deepcopy(config)
    if dimension == "source":
        after["tree"] = "0" * 40
    else:
        after_config["filters"] = ["unexpected"]
    snapshots = iter([(source, blobs), (after, blobs)])
    configurations = iter([config, after_config])
    stages = []
    def next_snapshot(bound_root):
        assert bound_root == ROOT
        stages.append("snapshot")
        return next(snapshots)
    def completed_child(*args, **kwargs):
        stages.append("collector")
        return b"{}"
    def completed_gate_a(*args, **kwargs):
        stages.append("gate_a")
        return []
    monkeypatch.setattr(COL, "snapshot", next_snapshot)
    monkeypatch.setattr(COL, "configuration", lambda: next(configurations))
    monkeypatch.setattr(GATE, "supervised", completed_child)
    monkeypatch.setattr(GATE, "gate_a", completed_gate_a)
    monkeypatch.setattr(GATE, "sys", SimpleNamespace(flags=SimpleNamespace(utf8_mode=1), executable=sys.executable))
    with pytest.raises(COL.ScanError, match="SOURCE_OR_CONFIG_DRIFT"):
        GATE.execute_scan(ROOT, enforce_frozen=False)
    assert stages == ["snapshot", "collector", "gate_a", "snapshot"]


def test_json_and_yaml_views_are_accounted():
    for name, text in [("fixture.json", '{"message":"Hello"}\n'), ("fixture.yaml", 'message: "Hello"\n')]:
        with COL.engine() as (plugins, transformers):
            row, _ = COL.scan_text(name, text.encode(), plugins, transformers)
        assert row["required_passes"][0] == "raw"
        assert {x["name"] for x in row["transform_attempts"]} == set(COL.TRANSFORMS)
        assert len(row["passes"]) == len(row["required_passes"])


@pytest.mark.parametrize("suffix", ["", "# unrelated following line\n"])
def test_yaml_inline_mapping_preserves_shared_source_line(suffix):
    text = "{first: hello, second: world}\n" + suffix
    with COL.engine() as (plugins, transformers):
        row, found = COL.scan_text("fixture.yaml", text.encode(), plugins, transformers)
    assert found == []
    yaml_pass = next(item for item in row["passes"] if item["name"] == "YAMLTransformer")
    assert yaml_pass["line_numbers"] == [1, 1]
    assert {item["calls"] for item in yaml_pass["detectors"]} == {2}


def test_yaml_second_inline_candidate_has_physical_line():
    value = "synthetic" + "-only-" + "candidate"
    text = '{first: hello, password: "' + value + '"}\n# unrelated following line\n'
    with COL.engine() as (plugins, transformers):
        _, found = COL.scan_text("fixture.yaml", text.encode(), plugins, transformers)
    keywords = [item for item in found if item["type"] == "Secret Keyword"]
    assert keywords and {item["line"] for item in keywords} == {1}
    assert GATE.classify(found, {"fixture.yaml": text.encode()})[1] > 0


def test_yaml_distinct_candidates_on_shared_line_remain_distinct():
    import hashlib

    values = ["synthetic" + "-first-candidate", "synthetic" + "-second-candidate"]
    text = '{password: "' + values[0] + '", api_key: "' + values[1] + '"}\n'
    with COL.engine() as (plugins, transformers):
        _, found = COL.scan_text("fixture.yaml", text.encode(), plugins, transformers)
    keywords = [item for item in found if item["type"] == "Secret Keyword"]
    assert {item["fingerprint"] for item in keywords} == {
        hashlib.sha1(value.encode()).hexdigest() for value in values
    }
    assert {item["line"] for item in keywords} == {1}


def test_yaml_later_scalar_uses_source_line_after_inline_expansion():
    value = "synthetic" + "-only-" + "candidate"
    text = 'inline: {first: hello, second: world}\npassword: "' + value + '"\n'
    with COL.engine() as (plugins, transformers):
        row, found = COL.scan_text("fixture.yaml", text.encode(), plugins, transformers)
    yaml_pass = next(item for item in row["passes"] if item["name"] == "YAMLTransformer")
    assert yaml_pass["line_numbers"] == [1, 1, 2]
    keywords = [item for item in found if item["type"] == "Secret Keyword"]
    assert keywords and {item["line"] for item in keywords} == {2}


def test_yaml_decoded_candidate_without_exact_source_binding_fails():
    key = 'pass' + 'word'
    text = (key + ': "synthetic\\x2donly\\x2dcandidate"\n').encode()
    with COL.engine() as (plugins, transformers), pytest.raises(COL.ScanError, match="TRANSFORM_LOCATION_UNPROVEN"):
        COL.scan_text("fixture.yaml", text, plugins, transformers)


def test_real_corrective_head_cli_requires_all_gates():
    # Required qualification test, intentionally fails for dirty or uncommitted candidate code.
    # Run only when application/execution and an exact committed candidate are authorized.
    import hashlib
    import json

    def git(*args):
        return subprocess.check_output(["git", "-C", str(ROOT), *args])

    before_head = git("rev-parse", "HEAD").decode().strip()
    before_tree = git("rev-parse", "HEAD^{tree}").decode().strip()
    before_index = git("ls-files", "--stage", "-z")
    paths = git("ls-files", "-z").decode().rstrip("\0").split("\0")
    before_bytes = {p: hashlib.sha256((ROOT / p).read_bytes()).digest() for p in paths}
    assert git("status", "--porcelain=v1", "--untracked-files=no") == b""
    target = ROOT / "secret-scan-receipt.json"
    assert git("ls-files", "--", target.name) == b""
    assert not target.is_symlink()
    target.write_text(json.dumps({"status": "PASS", "worker_nonce": "stale"}), encoding="utf-8")
    result = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/ci/check_secret_scan.py"), "--scan", "--receipt", "secret-scan-receipt.json"], cwd=ROOT, capture_output=True, timeout=150, check=False)
    assert git("rev-parse", "HEAD").decode().strip() == before_head
    assert git("ls-files", "--stage", "-z") == before_index
    assert {p: hashlib.sha256((ROOT / p).read_bytes()).digest() for p in paths} == before_bytes
    assert git("status", "--porcelain=v1", "--untracked-files=no") == b""
    assert not list(ROOT.glob(".secret-scan-*.tmp"))
    assert result.returncode == 0, "full corrective HEAD has not passed collection/classification/integrity"
    receipt = COL.parse((ROOT / "secret-scan-receipt.json").read_bytes())
    assert receipt["worker_nonce"] != "stale"
    assert receipt["collection"]["source"]["head"] == before_head
    assert receipt["collection"]["source"]["tree"] == before_tree
    assert receipt["status"] == "PASS" and receipt["production_frozen_integrity"] == "PASS"
    assert receipt["gate_a"] == receipt["gate_b"] == "PASS"
    assert receipt["parent_observed_worker_exit"] == receipt["parent_observed_collector_exit"] == 0


def process_live(pid):
    import os
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        api = ctypes.WinDLL("kernel32", use_last_error=True)
        api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        api.OpenProcess.restype = wintypes.HANDLE
        api.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        api.GetExitCodeProcess.restype = wintypes.BOOL
        api.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = api.OpenProcess(0x1000, False, pid)
        if not handle: return False
        try:
            status = wintypes.DWORD()
            assert api.GetExitCodeProcess(handle, ctypes.byref(status))
            return status.value == 259
        finally: api.CloseHandle(handle)
    stat = Path('/proc') / str(pid) / 'stat'
    if stat.exists() and stat.read_text().split(') ', 1)[1].startswith('Z '): return False
    try: os.kill(pid, 0)
    except ProcessLookupError: return False
    return True


@pytest.mark.parametrize("root_exit", [0, 7])
def test_descendant_terminated_after_root_exits(tmp_path, root_exit):
    import time
    marker = tmp_path / 'descendant.pid'
    ready = tmp_path / 'root-ready-to-exit'
    descendant = "import os,pathlib,time; pathlib.Path(" + repr(str(marker)) + ").write_text(str(os.getpid())); time.sleep(60)"
    command = (
        "import pathlib,subprocess,sys,time\n"
        "subprocess.Popen([sys.executable,'-c'," + repr(descendant) + "])\n"
        "marker=pathlib.Path(" + repr(str(marker)) + ")\n"
        "deadline=time.monotonic()+5\n"
        "while not marker.exists() and time.monotonic()<deadline: time.sleep(0.01)\n"
        "if not marker.exists(): sys.exit(125)\n"
        "pathlib.Path(" + repr(str(ready)) + ").write_text('ready')\n"
        "sys.exit(" + str(root_exit) + ")\n"
    )
    try:
        with pytest.raises(ValueError):
            GATE.supervised([sys.executable, '-c', command], tmp_path, timeout=10)
        assert marker.exists(), "fixture descendant was never started"
        assert ready.exists(), "fixture root did not observe descendant readiness before exiting"
        pid = int(marker.read_text())
        deadline = time.monotonic() + 5
        while process_live(pid) and time.monotonic() < deadline: time.sleep(0.02)
        assert not process_live(pid), "descendant remained after failure"
    finally:
        if marker.exists() and process_live(int(marker.read_text())):
            import os
            import signal
            os.kill(int(marker.read_text()), signal.SIGTERM)


def test_known_plus_new_collected_from_tracked_fixture(tmp_path):
    path = GATE.EXCEPTIONS[0][0]
    raw = subprocess.check_output(['git','-C',str(ROOT),'show','HEAD:'+path])
    token = 'synthetic' + '-only-' + 'new-value'
    root = repository(tmp_path, {path: raw, 'new.py': ('password = "'+token+'"\n').encode()})
    receipt = collect_child(root)
    source, blobs = COL.snapshot(root); config = COL.configuration(); config['utf8_mode'] = 1
    rows = GATE.gate_a(receipt, source, blobs, config, 'a'*32)
    allowed, denied = GATE.classify(rows, blobs)
    assert allowed > 0 and denied > 0
    assert any(row['path'] == 'new.py' for row in rows)


@pytest.mark.parametrize('case', ['comment','unicode','json','repeated','empty'])
def test_extended_parity_and_conservative_policy(case, tmp_path):
    from detect_secrets.core.scan import scan_file
    from detect_secrets.settings import default_settings
    value = 'synthetic' + '-only-' + 'candidate'
    name='fixture.py'; text='password = "'+value+'"\n'
    if case=='comment': text += '# password = "'+value+'" # pragma: allowlist secret\n'
    elif case=='unicode': text = '# Bukti — tidak terukur\n'+text
    elif case=='json': name='fixture.json'; text='{"password":"'+value+'"}\n'
    elif case=='repeated': text *= 2
    elif case=='empty': text=''
    target=tmp_path/name; target.write_text(text,encoding='utf-8')
    with default_settings() as settings:
        settings.disable_filters('detect_secrets.filters.common.is_ignored_due_to_verification_policies')
        former=list(scan_file(str(target)))
    with COL.engine() as (plugins,transforms):
        row,ours=COL.scan_text(name,text.encode(),plugins,transforms)
    ourkeys={(r['line'],r['type'],r['fingerprint']) for r in ours}
    assert {(r.line_number,r.type,r.secret_hash) for r in former} <= ourkeys
    assert row['filter_decisions']==[]
    if case=='comment': assert any(r['line']==2 for r in ours)
    if case=='repeated': assert {r['line'] for r in ours} >= {1,2}
    if case=='empty': assert not ours and row['passes'][0]['detectors'][0]['calls']==1


class UnexpectedPrivateFailure(Exception):
    """Synthetic failure outside the known operational exception classes."""


@pytest.mark.parametrize("failure", [OSError("private-canary"), ValueError("private-canary"),
                                    RuntimeError("private-canary"), UnexpectedPrivateFailure("private-canary")])
def test_controlled_errors_translate_unexpected_failure(failure, capsys):
    with pytest.raises(COL.ScanError, match="^UNEXPECTED_OPERATION_FAILURE$") as caught, COL.controlled_errors():
        raise failure
    assert caught.value.args == ("UNEXPECTED_OPERATION_FAILURE",)
    assert caught.value.__cause__ is None and caught.value.__suppress_context__
    output = capsys.readouterr()
    assert output.out == output.err == ""


def test_controlled_errors_preserve_existing_domain_error_identity():
    failure = COL.ScanError("COVERAGE_NOT_PROVEN")
    with pytest.raises(COL.ScanError) as caught, COL.controlled_errors():
        raise failure
    assert caught.value is failure
    assert type(caught.value) is COL.ScanError
    assert caught.value.args == ("COVERAGE_NOT_PROVEN",)


@pytest.mark.parametrize("failure", [KeyboardInterrupt(), SystemExit(9), GeneratorExit()])
def test_controlled_errors_do_not_translate_base_exceptions(failure):
    with pytest.raises(type(failure)) as caught, COL.controlled_errors():
        raise failure
    assert caught.value is failure


@pytest.mark.parametrize("entrypoint", ["git", "supervised"])
def test_reader_unexpected_failure_signals_and_closes(monkeypatch, tmp_path, capsys, entrypoint):
    class Pipe:
        def __init__(self, fail):
            self.fail = fail
            self.closed = False

        def read(self, size):
            if self.fail:
                raise UnexpectedPrivateFailure("private-reader-canary")
            return b""

        def close(self):
            self.closed = True

    class Child:
        def __init__(self):
            self.stdin = None
            self.stdout = Pipe(True)
            self.stderr = Pipe(False)
            self.returncode = 0
            self.waits = 0

        def wait(self, timeout):
            self.waits += 1
            return 0

        def poll(self):
            return 0

    child = Child()
    monkeypatch.setattr(COL.subprocess, "Popen", lambda *args, **kwargs: child)
    category = "GIT_OUTPUT_FAILURE" if entrypoint == "git" else "COLLECTOR_(OUTPUT_LIMIT|READ_FAILURE)"
    with pytest.raises(COL.ScanError, match=category):
        if entrypoint == "git":
            COL.git(tmp_path, "status")
        else:
            GATE.supervised(["synthetic-child"], tmp_path, own_group=False)
    assert child.stdout.closed and child.waits >= 1
    if entrypoint == "supervised":
        assert child.stderr.closed
    output = capsys.readouterr()
    assert "private-reader-canary" not in output.out + output.err


def test_collector_unexpected_failure_is_sanitized(monkeypatch, tmp_path, capsys):
    def fail(*args, **kwargs):
        raise UnexpectedPrivateFailure("private-collector-canary")

    monkeypatch.setattr(sys, "argv", ["collector", "--root", str(tmp_path), "--nonce", "a" * 32])
    monkeypatch.setattr(COL, "collect", fail)
    assert COL.main() == 1
    output = capsys.readouterr()
    assert output.out == '{"error":"COLLECTION_FAILED"}'
    assert output.err == ""


def test_controlled_errors_normal_exit_preserves_enter_value():
    entered = []
    with COL.controlled_errors() as value:
        entered.append(value)
    assert entered == [None]


def test_controlled_errors_nested_boundaries_preserve_domain_identity():
    failure = COL.ScanError("COVERAGE_NOT_PROVEN")
    with pytest.raises(COL.ScanError) as caught, COL.controlled_errors(), COL.controlled_errors():
        raise failure
    assert caught.value is failure


def test_controlled_errors_exception_group_has_sanitized_traceback():
    import traceback

    failure = ExceptionGroup("private-group-canary", [UnexpectedPrivateFailure("private-child-canary")])
    with pytest.raises(COL.ScanError) as caught, COL.controlled_errors():
        raise failure
    rendered = "".join(traceback.format_exception(caught.value))
    assert "private-group-canary" not in rendered
    assert "private-child-canary" not in rendered
    assert caught.value.__cause__ is None and caught.value.__suppress_context__


def test_controlled_errors_runs_body_cleanup_before_translation():
    events = []
    with pytest.raises(COL.ScanError), COL.controlled_errors():
        try:
            raise UnexpectedPrivateFailure("private-cleanup-canary")
        finally:
            events.append("cleanup")
    assert events == ["cleanup"]


def test_controlled_errors_use_actual_exception_type_despite_spoofed_class():
    class SpoofedFailure(Exception):
        @property
        def __class__(self):
            return COL.ScanError

        @__class__.setter
        def __class__(self, value: type) -> None:
            raise TypeError("synthetic class reassignment forbidden")

    with pytest.raises(COL.ScanError) as caught, COL.controlled_errors():
        raise SpoofedFailure("private-type-canary")
    assert type(caught.value) is COL.ScanError
    assert caught.value.args == ("UNEXPECTED_OPERATION_FAILURE",)
    assert caught.value.__cause__ is None and caught.value.__suppress_context__


def test_controlled_errors_preserve_actual_base_exception_type():
    class SpoofedControl(BaseException):
        @property
        def __class__(self):
            return Exception

        @__class__.setter
        def __class__(self, value: type) -> None:
            raise TypeError("synthetic class reassignment forbidden")

    failure = SpoofedControl("private-control-canary")
    with pytest.raises(SpoofedControl) as caught, COL.controlled_errors():
        raise failure
    assert caught.value is failure


def test_controlled_errors_never_read_exception_class_property():
    accessed = []

    class ExplosiveClass(Exception):
        @property
        def __class__(self):
            accessed.append(True)
            raise RuntimeError("private-getter-canary")

        @__class__.setter
        def __class__(self, value: type) -> None:
            raise TypeError("synthetic class reassignment forbidden")

    with pytest.raises(COL.ScanError) as caught, COL.controlled_errors():
        raise ExplosiveClass("private-exception-canary")
    assert accessed == []
    assert caught.value.args == ("UNEXPECTED_OPERATION_FAILURE",)
