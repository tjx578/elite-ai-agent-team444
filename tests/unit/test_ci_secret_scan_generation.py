"""Historical coverage and successor lifecycle specifications, not freeze evidence."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
GATE = ModuleType("generation_gate_tests")
GATE.__file__ = str(ROOT / "scripts/ci/check_secret_scan.py")
exec(compile(Path(GATE.__file__).read_bytes(), GATE.__file__, "exec"), GATE.__dict__)  # noqa: S102 -- load exact test-subject bytes without bytecode cache


@pytest.fixture(scope="module", autouse=True)
def verified_collection():
    GATE.initialize_collection(ROOT)


@pytest.fixture(scope="module")
def production_blobs():
    paths = {GATE.HISTORICAL_FROZEN_PATHS.get(p, p) for p in GATE.FROZEN_DIGESTS}
    paths.update(GATE.ACTIVE_MEMBER_DIGESTS)
    paths.update(GATE.SUCCESSOR_ARTIFACT_DIGESTS)
    return {p: subprocess.check_output(["git", "-C", str(ROOT), "show", "HEAD:" + p]) for p in paths}


def rebind_test_artifacts(monkeypatch, blobs):
    """Synthetic policy fixture only; never modifies production source or files."""
    monkeypatch.setattr(GATE, "SUCCESSOR_ARTIFACT_DIGESTS", {
        p: tuple(hashlib.sha256(blobs[p]).digest()) for p in GATE.SUCCESSOR_ARTIFACT_DIGESTS
    })


def test_historical_archive_does_not_substitute_current_agents(production_blobs):
    assert production_blobs["AGENTS.md"] != production_blobs[GATE.HISTORICAL_FROZEN_PATHS["AGENTS.md"]]
    GATE.historical_frozen_integrity(production_blobs)
    changed = dict(production_blobs)
    changed[GATE.HISTORICAL_FROZEN_PATHS["AGENTS.md"]] = changed["AGENTS.md"]
    with pytest.raises(ValueError, match="FROZEN_ARTIFACT_CHANGED"):
        GATE.historical_frozen_integrity(changed)


def test_pending_generation_cannot_inherit_historical_pass(production_blobs, monkeypatch):
    blobs = dict(production_blobs)
    review = json.loads(blobs[GATE.ACTIVE_REVIEW_PATH])
    review.update(status="REVIEW_PENDING", reviewer=None, reviewed_at=None,
                  findings=None, open_blocking_findings=None)
    blobs[GATE.ACTIVE_REVIEW_PATH] = json.dumps(review).encode()
    freeze = json.loads(blobs[GATE.ACTIVE_FREEZE_PATH])
    freeze.update(status="REVIEW_PENDING", active_generation=False,
                  owner_acceptance="PENDING_FINAL_OWNER_REVIEW")
    freeze["review_receipt"].update(status="REVIEW_PENDING", sha256=hashlib.sha256(blobs[GATE.ACTIVE_REVIEW_PATH]).hexdigest())
    blobs[GATE.ACTIVE_FREEZE_PATH] = json.dumps(freeze).encode()
    rebind_test_artifacts(monkeypatch, blobs)
    assert GATE.classify([], blobs) == (0, 0)
    with pytest.raises(ValueError, match="ACTIVE_GENERATION_NOT_FROZEN"):
        GATE.frozen_integrity(blobs)


@pytest.mark.parametrize("path", sorted(GATE.ACTIVE_MEMBER_DIGESTS))
@pytest.mark.parametrize("mode", ["missing", "changed"])
def test_each_active_member_is_bound(production_blobs, path, mode):
    blobs = dict(production_blobs)
    if mode == "missing":
        del blobs[path]
    else:
        blobs[path] += b"\n"
    with pytest.raises(ValueError, match="ACTIVE_GENERATION_ARTIFACT"):
        GATE.active_generation_integrity(blobs)


@pytest.mark.parametrize("path", sorted(GATE.SUCCESSOR_ARTIFACT_DIGESTS))
def test_successor_receipts_are_independently_pinned(production_blobs, path):
    blobs = dict(production_blobs)
    blobs[path] += b"\n"
    with pytest.raises(ValueError, match="ACTIVE_GENERATION_ARTIFACT_CHANGED"):
        GATE.active_generation_integrity(blobs)


@pytest.fixture
def reviewed_synthetic_generation(production_blobs, monkeypatch):
    # Exercise lifecycle semantics using explicit in-memory fixture pins. This
    # fixture is not a review or acceptance of any real generation.
    blobs = dict(production_blobs)
    review = json.loads(blobs[GATE.ACTIVE_REVIEW_PATH])
    review.update(status="PASS", reviewer="synthetic test fixture", reviewed_at="2000-01-01T00:00:00Z",
                  evidence_class="EXACT_ARTIFACT_DESIGN_REVIEW", findings=[], open_blocking_findings=0)
    blobs[GATE.ACTIVE_REVIEW_PATH] = json.dumps(review).encode()
    freeze = json.loads(blobs[GATE.ACTIVE_FREEZE_PATH])
    freeze.update(status="FROZEN_LOCAL_PENDING_REMOTE_INTEGRATION", active_generation=True,
                  owner_acceptance="APPROVED", frozen_by="synthetic test fixture",
                  frozen_at="2000-01-01T00:00:00Z")
    freeze["review_receipt"].update(status="PASS", sha256=hashlib.sha256(blobs[GATE.ACTIVE_REVIEW_PATH]).hexdigest())
    blobs[GATE.ACTIVE_FREEZE_PATH] = json.dumps(freeze).encode()
    rebind_test_artifacts(monkeypatch, blobs)
    return blobs


def test_complete_synthetic_lifecycle_is_valid(reviewed_synthetic_generation):
    GATE.frozen_integrity(reviewed_synthetic_generation)


@pytest.mark.parametrize("field,value", [
    ("active_generation", False), ("owner_acceptance", "PENDING_FINAL_OWNER_REVIEW"),
    ("status", "REVIEW_PENDING"), ("frozen_members", True), ("runtime_loaded", True),
])
def test_review_alone_does_not_complete_freeze(reviewed_synthetic_generation, monkeypatch, field, value):
    blobs = dict(reviewed_synthetic_generation)
    freeze = json.loads(blobs[GATE.ACTIVE_FREEZE_PATH])
    freeze[field] = value
    blobs[GATE.ACTIVE_FREEZE_PATH] = json.dumps(freeze).encode()
    rebind_test_artifacts(monkeypatch, blobs)
    with pytest.raises(ValueError, match="ACTIVE_GENERATION"):
        GATE.active_generation_integrity(blobs)


def test_review_hash_and_manifest_hash_are_not_interchangeable(reviewed_synthetic_generation, monkeypatch):
    blobs = dict(reviewed_synthetic_generation)
    freeze = json.loads(blobs[GATE.ACTIVE_FREEZE_PATH])
    freeze["review_receipt"]["sha256"] = freeze["manifest"]["sha256"]
    blobs[GATE.ACTIVE_FREEZE_PATH] = json.dumps(freeze).encode()
    rebind_test_artifacts(monkeypatch, blobs)
    with pytest.raises(ValueError, match="ACTIVE_GENERATION_FREEZE_BINDING"):
        GATE.active_generation_integrity(blobs)


@pytest.mark.parametrize("field,value", [
    ("status", "WARN"), ("reviewer", None), ("reviewed_at", ""),
    ("open_blocking_findings", 1), ("open_blocking_findings", False),
    ("findings", None), ("evidence_class", "HISTORICAL_REVIEW"),
])
def test_incomplete_review_cannot_support_freeze(reviewed_synthetic_generation, monkeypatch, field, value):
    blobs = dict(reviewed_synthetic_generation)
    review = json.loads(blobs[GATE.ACTIVE_REVIEW_PATH])
    review[field] = value
    blobs[GATE.ACTIVE_REVIEW_PATH] = json.dumps(review).encode()
    freeze = json.loads(blobs[GATE.ACTIVE_FREEZE_PATH])
    freeze["review_receipt"].update(status=review["status"], sha256=hashlib.sha256(blobs[GATE.ACTIVE_REVIEW_PATH]).hexdigest())
    blobs[GATE.ACTIVE_FREEZE_PATH] = json.dumps(freeze).encode()
    rebind_test_artifacts(monkeypatch, blobs)
    with pytest.raises(ValueError, match="ACTIVE_GENERATION"):
        GATE.active_generation_integrity(blobs)


def test_production_gate_always_calls_both_domains(monkeypatch):
    calls = []
    marker = {"test": b"fixture"}
    monkeypatch.setattr(GATE, "historical_frozen_integrity", lambda blobs: calls.append(("historical", blobs)))
    monkeypatch.setattr(GATE, "active_generation_integrity", lambda blobs: calls.append(("active", blobs)))
    GATE.frozen_integrity(marker)
    assert calls == [("historical", marker), ("active", marker)]
