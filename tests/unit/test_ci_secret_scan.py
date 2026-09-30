"""Exact exception and production-integrity regressions (no count-based coverage)."""
from __future__ import annotations

import copy
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("secret_gate_tests", ROOT / "scripts/ci/check_secret_scan.py")
assert SPEC is not None and SPEC.loader is not None
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


@pytest.fixture(scope="module", autouse=True)
def initialize_verified_collection():
    """Pure gate fixtures use collector code authenticated from this committed HEAD."""
    GATE.initialize_collection(ROOT)


@pytest.fixture(scope="module")
def evidence():
    return {p: subprocess.check_output(["git", "-C", str(ROOT), "show", "HEAD:" + p]) for p in {**GATE.FILE_DIGESTS, **GATE.ADDITIONAL_FILE_DIGESTS}}


def historical_frozen_blobs():
    paths = [GATE.HISTORICAL_FROZEN_PATHS.get(path, path) for path in GATE.FROZEN_DIGESTS]
    return {path: subprocess.check_output(["git", "-C", str(ROOT), "show", "HEAD:" + path]) for path in paths}


def finding(binding):
    path, line, kind, fp, _ = binding
    return {"path": path, "line": line, "type": kind, "fingerprint": bytes(fp).hex()}


@pytest.mark.parametrize("binding", (*GATE.EXCEPTIONS, *GATE.ADDITIONAL_EXCEPTIONS))
def test_individual_exact_evidence_binding(binding, evidence):
    assert GATE.classify([finding(binding)], evidence) == (1, 0)


def test_historical_bindings_are_preserved(evidence):
    # This tests Gate B only; 679 is never a coverage or whole-scan acceptance rule.
    rows = [finding(x) for x in GATE.EXCEPTIONS]
    assert len(rows) == 106 + 573
    assert GATE.classify(rows, evidence) == (679, 0)


def test_clean_input_needs_no_exception_files():
    assert GATE.classify([], {"hello.txt": b"Hello world\n"}) == (0, 0)


@pytest.mark.parametrize("mutation", ["path", "line", "type", "fingerprint"])
def test_exact_binding_mutations_rejected(mutation, evidence):
    row = finding(GATE.EXCEPTIONS[0]); blobs = dict(evidence)
    if mutation == "path":
        blobs["moved.txt"] = blobs[row["path"]]
        row["path"] = "moved.txt"
    elif mutation == "line":
        row["line"] += 1
    elif mutation == "type":
        row["type"] = "Secret Keyword"
    else:
        row["fingerprint"] = "0" * 40
    assert GATE.classify([row], blobs) == (0, 1)


@pytest.mark.parametrize("kind", ["Hex High Entropy String", "Secret Keyword", "GitHub Token"])
def test_unknown_hex_and_other_secret_types_fail(kind):
    row = {"path": "new.txt", "line": 1, "type": kind, "fingerprint": "1" * 40}
    assert GATE.classify([row], {"new.txt": b"synthetic content\n"}) == (0, 1)


def test_changed_whole_file_context_fails(evidence):
    row = finding(GATE.EXCEPTIONS[0]); blobs = dict(evidence)
    blobs[row["path"]] += b"\nchanged context\n"
    with pytest.raises(ValueError, match="EXCEPTION_CONTEXT_CHANGED"):
        GATE.classify([row], blobs)


def test_crlf_normalization_is_only_exception_context(evidence):
    rows = [finding(x) for x in GATE.EXCEPTIONS]
    crlf = {p: b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n") for p, b in evidence.items()}
    assert GATE.classify(rows, crlf) == (679, 0)


def test_duplicate_occurrence_is_malformed(evidence):
    row = finding(GATE.EXCEPTIONS[0])
    with pytest.raises(ValueError, match="DUPLICATE_FINDING"):
        GATE.classify([row, copy.deepcopy(row)], evidence)


@pytest.mark.parametrize("value", [None, {}, "", 0, True])
def test_malformed_finding_list(value):
    with pytest.raises((TypeError, ValueError)):
        GATE.classify(value, {})


@pytest.mark.parametrize("key,value", [("line", True), ("line", 0), ("fingerprint", "z" * 40), ("path", "../x")])
def test_malformed_item(key, value, evidence):
    row = finding(GATE.EXCEPTIONS[0]); row[key] = value
    with pytest.raises(ValueError):
        GATE.classify([row], evidence)


@pytest.mark.parametrize("raw", [b"{}", b"{", b'{"a":1,"a":2}', b'{"x":NaN}', b'\xff'])
def test_untrusted_reports_never_supply_gate_a(raw):
    with pytest.raises((TypeError, ValueError)):
        GATE.gate_a(GATE.collection.parse(raw), {}, {}, {}, "a" * 32)


def test_frozen_gate_fails_for_clean_fixture_without_production_artifacts():
    with pytest.raises(ValueError, match="FROZEN_ARTIFACT_MISSING"):
        GATE.frozen_integrity({"hello.txt": b"Hello\n"})


def test_every_frozen_pin_and_mutation():
    blobs = historical_frozen_blobs()
    assert len(blobs) == len(GATE.FROZEN_DIGESTS) == 36
    GATE.historical_frozen_integrity(blobs)
    for path in blobs:
        changed = dict(blobs); changed[path] += b"\n"
        with pytest.raises(ValueError, match="FROZEN_ARTIFACT_CHANGED"):
            GATE.historical_frozen_integrity(changed)


def test_legacy_cli_removes_stale_success_and_fails(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    report = tmp_path / "report.json"; report.write_text('{"results":{}}')
    stale = tmp_path / "secret-scan-receipt.json"; stale.write_text('{"status":"PASS"}')
    result = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/ci/check_secret_scan.py"), str(report)], cwd=tmp_path, capture_output=True, check=False)
    assert result.returncode != 0 and not stale.exists()
    assert b"COVERAGE_NOT_PROVEN" in result.stdout
    assert b"PASS" not in result.stdout
    assert result.stderr == b""


@pytest.mark.parametrize("failure_type", ["domain", "unexpected"])
def test_other_cli_error_never_echoes_candidate(tmp_path, monkeypatch, capsys, failure_type):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    monkeypatch.chdir(tmp_path)
    calls = []
    def fail_child(*args, **kwargs):
        calls.append(args)
        error = GATE.collection.ScanError if failure_type == "domain" else RuntimeError
        raise error("PRIVATE_SYNTHETIC_CANDIDATE")
    # This isolates public error formatting; bootstrap rejection has its own suite.
    monkeypatch.setattr(GATE, "initialize_collection", lambda *args, **kwargs: {})
    monkeypatch.setattr(GATE, "supervised", fail_child)
    assert GATE.main(["--scan"]) == 1
    assert len(calls) == 1
    output = capsys.readouterr()
    assert "PRIVATE_SYNTHETIC_CANDIDATE" not in output.out + output.err
    assert "COVERAGE_NOT_PROVEN" not in output.out + output.err


def test_receipt_cannot_overwrite_arbitrary_path(tmp_path):
    with pytest.raises(ValueError, match="RECEIPT_PATH_NOT_ALLOWED"):
        GATE.output_path(tmp_path, "README.md")


@pytest.mark.parametrize("family", ["Hex High Entropy String", "Secret Keyword"])
@pytest.mark.parametrize("dimension", ["path", "line", "type", "fingerprint", "field", "value"])
def test_both_exception_families_every_dimension(family, dimension, evidence):
    binding = next(x for x in GATE.EXCEPTIONS if x[2] == family)
    row = finding(binding); blobs = dict(evidence)
    if dimension == "path":
        blobs["another.txt"] = blobs[row["path"]]; row["path"] = "another.txt"
    elif dimension == "line": row["line"] += 1
    elif dimension == "type": row["type"] = "Synthetic Different Type"
    elif dimension == "fingerprint": row["fingerprint"] = "2" * 40
    else:
        lines = blobs[row["path"]].decode().splitlines(keepends=True)
        lines[row["line"] - 1] = ('changed_field: value\n' if dimension == "field" else binding[4] + ': changed_value\n')
        blobs[row["path"]] = ''.join(lines).encode()
        with pytest.raises(ValueError, match="EXCEPTION_CONTEXT_CHANGED"):
            GATE.classify([row], blobs)
        return
    assert GATE.classify([row], blobs) == (0, 1)


@pytest.mark.parametrize("name", ["cp1.1-design-002-freeze-receipt.json", "cp1.1-design-002-independent-review.json"])
@pytest.mark.parametrize("mode", ["missing", "changed"])
def test_design002_receipts_mandatory_even_zero_findings(name, mode):
    blobs = historical_frozen_blobs()
    path = "docs/verification/" + name
    if mode == "missing": del blobs[path]
    else: blobs[path] = b"No findings here\n"
    assert GATE.classify([], blobs) == (0, 0)
    with pytest.raises(ValueError, match="FROZEN_ARTIFACT"):
        GATE.frozen_integrity(blobs)


def test_timeout_removes_stale_receipt(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    stale = tmp_path / "secret-scan-receipt.json"; stale.write_text('{"status":"PASS"}')
    monkeypatch.chdir(tmp_path)
    calls = []
    def timeout(*args, **kwargs):
        calls.append(args)
        raise GATE.collection.ScanError("COLLECTOR_TIMEOUT")
    # A separate real-process test proves timeout/cleanup; this checks stale output.
    monkeypatch.setattr(GATE, "initialize_collection", lambda *args, **kwargs: {})
    monkeypatch.setattr(GATE, "supervised", timeout)
    assert GATE.main(["--scan"]) == 1
    assert len(calls) == 1
    assert not stale.exists()


@pytest.mark.parametrize("arguments", [
    ["--worker"],
    ["--worker", "invalid"],
    ["--worker", "a" * 32, "--unexpected"],
    ["--worker", "a" * 32, "--scan"],
    ["--worker", "a" * 32],
    ["--worker", "a" * 32, "--expected-head", "0" * 40],
])
def test_worker_failures_remove_stale_receipt_without_traceback(tmp_path, arguments):
    """Invalid/internal CLI modes cannot preserve a previous successful receipt."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    stale = tmp_path / "secret-scan-receipt.json"
    stale.write_text('{"status":"PASS"}', encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-I", "-X", "utf8",
         str(ROOT / "scripts/ci/check_secret_scan.py"), *arguments],
        cwd=tmp_path, capture_output=True, timeout=30,
    check=False)
    assert result.returncode != 0
    assert not stale.exists()
    assert b"Traceback" not in result.stderr
    assert b"PASS" not in result.stdout


@pytest.mark.parametrize("mutation", ["missing_pointer", "wrong_value", "duplicate_pointer", "empty_pointers"])
def test_canonical_fixture_exception_rejects_wrong_selector(evidence, monkeypatch, mutation):
    import json
    binding = next(x for x in GATE.ADDITIONAL_EXCEPTIONS if x[4].startswith("json:"))
    pointers = json.loads(binding[4][5:])
    if mutation == "missing_pointer":
        pointers[0] = "/nonexistent"
    elif mutation == "wrong_value":
        pointers[0] = "/schema_version"
    elif mutation == "duplicate_pointer":
        pointers.append(pointers[0])
    else:
        pointers = []
    wrong = (*binding[:4], "json:" + json.dumps(pointers))
    monkeypatch.setattr(GATE, "ADDITIONAL_EXCEPTIONS", (wrong,))
    with pytest.raises(ValueError, match="EXCEPTION_FIELD_CHANGED"):
        GATE.classify([finding(binding)], evidence)


def test_additional_bindings_do_not_admit_new_occurrence(evidence):
    binding = GATE.ADDITIONAL_EXCEPTIONS[0]
    row = finding(binding)
    row["fingerprint"] = "0" * 40
    assert GATE.classify([row], evidence) == (0, 1)
