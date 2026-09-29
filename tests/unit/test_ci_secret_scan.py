"""Exact evidence exceptions must not suppress unknown secrets or context drift."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from detect_secrets.core.secrets_collection import SecretsCollection
from detect_secrets.settings import default_settings

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("secret_validator", ROOT / "scripts/ci/check_secret_scan.py")
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


@pytest.fixture(scope="module")
def scan_report():
    # Run the real scanner on immutable evidence, independently of allowlist entries.
    secrets = SecretsCollection()
    with default_settings():
        for path in validator.FILE_DIGESTS:
            secrets.scan_file(path)
    results = {}
    for path, items in secrets.json().items():
        canonical = path.replace("\\", "/")
        for item in items:
            item["filename"] = canonical
        results[canonical] = items
    return {"results": results}


def first_finding(report):
    path = "docs/research/algorithm-donors/adoption-registry.yaml"
    return path, copy.deepcopy(report["results"][path][0])


def one(path, finding):
    return {"results": {path: [finding]}}


def test_real_102_addendum_findings_and_four_legacy_digests(scan_report):
    counts = {p: len(items) for p, items in scan_report["results"].items()}
    prefix = "docs/research/algorithm-donors/"
    assert counts == {
        prefix + "adoption-registry.yaml": 89,
        prefix + "receipts/ALG-REG-001-freeze.yaml": 9,
        prefix + "receipts/CP0_ADDENDUM_01_A01_REVIEW_a6c2f24.json": 4,
        "docs/verification/sentient-identity-20260928.json": 4,
    }
    assert validator.validate_report(scan_report, ROOT) == (106, [])


@pytest.mark.parametrize("change", ["path", "fingerprint", "type", "new_hex", "non_digest", "line"])
def test_exact_binding_rejects_changed_finding(scan_report, change):
    path, finding = first_finding(scan_report)
    if change == "path":
        path = "docs/unrelated-evidence.yaml"
        finding["filename"] = path
    elif change == "fingerprint":
        finding["hashed_secret"] = hashlib.sha1(b"altered evidence").hexdigest()
    elif change == "type":
        finding["type"] = "Secret Keyword"
    elif change == "new_hex":
        candidate = hashlib.sha256(b"previously unrecognized digest").hexdigest()
        finding["hashed_secret"] = hashlib.sha1(candidate.encode()).hexdigest()
    elif change == "non_digest":
        finding["type"] = "Base64 High Entropy String"
        finding["hashed_secret"] = hashlib.sha1(b"synthetic non-digest candidate").hexdigest()
    else:
        finding["line_number"] = 1
    allowed, failures = validator.validate_report(one(path, finding), ROOT)
    assert allowed == 0 and len(failures) == 1


@pytest.mark.parametrize("report", [None, [], {}, {"results": []}, {"results": {"x": None}},
                                   {"results": {"x": [None]}}, {"results": {"x": [{}]}}])
def test_malformed_report_fails_closed(report):
    with pytest.raises((TypeError, ValueError)):
        validator.validate_report(report, ROOT)


@pytest.mark.parametrize("field,value", [("line_number", True), ("line_number", 0),
    ("line_number", "5"), ("hashed_secret", None), ("hashed_secret", "invalid"),
    ("type", None), ("filename", "different/path")])
def test_malformed_finding_fails_closed(scan_report, field, value):
    path, finding = first_finding(scan_report)
    finding[field] = value
    with pytest.raises((TypeError, ValueError)):
        validator.validate_report(one(path, finding), ROOT)


def test_duplicate_finding_fails_closed(scan_report):
    path, finding = first_finding(scan_report)
    with pytest.raises((TypeError, ValueError)):
        validator.validate_report({"results": {path: [finding, finding]}}, ROOT)


@pytest.mark.parametrize("mutation", ["field", "value", "extra_context", "missing"])
def test_evidence_context_is_pinned(scan_report, tmp_path, mutation):
    for path in validator.FILE_DIGESTS:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / path).read_bytes())
    path, finding = first_finding(scan_report)
    target = tmp_path / path
    if mutation == "missing":
        target.unlink()
    else:
        text = target.read_text(encoding="utf-8")
        if mutation == "field":
            text = text.replace("cp0_accepted_sha:", "untrusted_context:", 1)
        elif mutation == "value":
            lines = text.splitlines()
            line = finding["line_number"] - 1
            lines[line] = lines[line][:-1] + ("0" if lines[line][-1] != "0" else "1")
            text = "\n".join(lines) + "\n"
        else:
            text += "\nadditional_unreviewed_context: true\n"
        target.write_text(text, encoding="utf-8")
    with pytest.raises((ValueError, OSError)):
        validator.validate_report(scan_report, tmp_path)


def test_crlf_checkout_preserves_exact_git_context(scan_report, tmp_path):
    for path in validator.FILE_DIGESTS:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / path).read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    assert validator.validate_report(scan_report, tmp_path) == (106, [])


@pytest.mark.parametrize("content", ["not-json", '{"results":{},"results":{}}', '{"results":{"x":[],"x":[]}}'])
def test_cli_malformed_json_returns_failure(tmp_path, monkeypatch, content):
    report = tmp_path / "report.json"
    report.write_text(content, encoding="utf-8")
    monkeypatch.setattr(validator.sys, "argv", ["check_secret_scan.py", str(report)])
    assert validator.main() == 1


def test_cli_real_report_succeeds(scan_report, tmp_path, monkeypatch):
    report = tmp_path / "report.json"
    report.write_text(json.dumps(scan_report), encoding="utf-8")
    monkeypatch.setattr(validator.sys, "argv", ["check_secret_scan.py", str(report)])
    assert validator.main() == 0

def test_windows_scanner_path_separators(scan_report):
    windows = {"results": {}}
    for path, items in copy.deepcopy(scan_report["results"]).items():
        path = path.replace("/", chr(92))
        for item in items:
            item["filename"] = path
        windows["results"][path] = items
    assert validator.validate_report(windows, ROOT) == (106, [])
