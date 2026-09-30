"""Supervised collection, exact exceptions, and mandatory frozen integrity.

Supplied reports cannot prove coverage. Receipts are fresh outputs only.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import logging
import os
import re
import secrets
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import ModuleType
from typing import Any, NoReturn, cast

# The reviewed validator/launcher is caller-trusted. Checking its source is a
# consistency check, not self-authentication of code that has already started.
# Collector source is authenticated independently before any helper is invoked.
BOOTSTRAP_TIMEOUT = 15.0
BOOTSTRAP_MAX_SOURCE_BYTES = 4 * 1024 * 1024
SCANNER_PATHS = ("scripts/ci/check_secret_scan.py", "scripts/ci/collect_secret_scan.py")
collection: Any = None
_bootstrap_binding: dict[str, Any] = {}
_verified_sources: dict[str, bytes] = {}


class BootstrapError(ValueError):
    """Fixed, sanitized failures before collector code is available."""


def _bootstrap_require(condition: bool, code: str) -> None:
    if not condition:
        raise BootstrapError(code)


def require(condition: bool, code: str) -> None:
    if collection is None:
        _bootstrap_require(condition, code)
    else:
        collection.require(condition, code)


def _bootstrap_git(root: Path, args: tuple[str, ...], deadline: float,
                   limit: int = BOOTSTRAP_MAX_SOURCE_BYTES, *, own_group: bool = True) -> bytes:
    """Read bounded output; parent owns a group/job, internal roles inherit it.

    Internal roles are private supervised entrypoints. They must not detach Git
    from the outer worker group, whose 120-second deadline owns descendants.
    """
    _bootstrap_require(time.monotonic() < deadline and limit > 0, "BOOTSTRAP_TIMEOUT")
    env = os.environ.copy()
    env.update(GIT_NO_REPLACE_OBJECTS="1", GIT_OPTIONAL_LOCKS="0",
               GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    command = ["git", "-c", "core.fsmonitor=false", "-C", str(root), *args]
    job = WindowsJob() if own_group and os.name == "nt" else None
    if job is not None:
        # The trampoline cannot launch Git before assignment to the owned job.
        gate = "import sys,subprocess; gate=sys.stdin.buffer.read(1); sys.exit(subprocess.call(sys.argv[1:]) if gate==b'1' else 125)"
        command = [sys.executable, "-I", "-c", gate, *command]
    child: subprocess.Popen[bytes] | None = None
    reader: threading.Thread | None = None
    reader_started = False
    output = bytearray()
    failure = threading.Event()

    def drain(stream: Any) -> None:
        try:
            while True:
                chunk = stream.read(4096)
                if not chunk:
                    return
                if len(output) + len(chunk) > limit:
                    failure.set()
                    return
                output.extend(chunk)
        except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
            failure.set()
        finally:
            try:
                stream.close()
            except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
                failure.set()

    try:
        child = subprocess.Popen(command, stdin=subprocess.PIPE if job else subprocess.DEVNULL,
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                 env=env, shell=False,
                                 start_new_session=own_group and os.name != "nt")
        if job is not None:
            job.assign(child.pid)
            _bootstrap_require(child.stdin is not None, "BOOTSTRAP_PIPE")
            assert child.stdin is not None
            child.stdin.write(b"1")
            child.stdin.close()
        _bootstrap_require(child.stdout is not None, "BOOTSTRAP_PIPE")
        reader = threading.Thread(target=drain, args=(child.stdout,), daemon=True)
        reader.start()
        reader_started = True
        while child.poll() is None or reader.is_alive():
            _bootstrap_require(not failure.is_set(), "BOOTSTRAP_GIT_OUTPUT")
            _bootstrap_require(time.monotonic() < deadline, "BOOTSTRAP_TIMEOUT")
            failure.wait(0.01)
        _bootstrap_require(time.monotonic() < deadline, "BOOTSTRAP_TIMEOUT")
        _bootstrap_require(not failure.is_set(), "BOOTSTRAP_GIT_OUTPUT")
        _bootstrap_require(child.returncode == 0, "BOOTSTRAP_GIT_FAILURE")
        return bytes(output)
    except BootstrapError:
        raise
    except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
        raise BootstrapError("BOOTSTRAP_GIT_FAILURE") from None
    finally:
        # Cover every post-Popen setup failure, including Thread.start failure.
        cleanup_failed = False
        if own_group and os.name != "nt" and child is not None:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
                cleanup_failed = True
        if job is not None:
            try:
                job.close()
            except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
                cleanup_failed = True
        if child is not None:
            try:
                if child.poll() is None:
                    child.kill()
                child.wait(timeout=5)
            except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
                cleanup_failed = True
            for stream in (child.stdin, child.stdout if not reader_started else None):
                if stream is not None:
                    try:
                        stream.close()
                    except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
                        cleanup_failed = True
        if reader is not None and reader_started:
            try:
                reader.join(timeout=1)
                cleanup_failed = cleanup_failed or reader.is_alive()
            except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
                cleanup_failed = True
        _bootstrap_require(not cleanup_failed, "BOOTSTRAP_CLEANUP_FAILED")


def _bootstrap_working_bytes(root: Path, relative: str) -> bytes:
    target = root / relative
    _bootstrap_require(target.is_file() and not target.is_symlink(), "BOOTSTRAP_SOURCE_PATH")
    _bootstrap_require(target.resolve().is_relative_to(root), "BOOTSTRAP_SOURCE_PATH")
    for component in (target, *target.parents):
        if component == root:
            break
        _bootstrap_require(not component.is_symlink() and not (
            getattr(component.lstat(), "st_file_attributes", 0) & 1024), "BOOTSTRAP_SOURCE_PATH")
    with target.open("rb") as stream:
        raw = stream.read(2 * BOOTSTRAP_MAX_SOURCE_BYTES + 1)
    _bootstrap_require(len(raw) <= 2 * BOOTSTRAP_MAX_SOURCE_BYTES, "BOOTSTRAP_SOURCE_LIMIT")
    return raw


def initialize_collection(root: Path, expected_head: str | None = None, *,
                          _own_group: bool = True) -> dict[str, Any]:
    """Bind both sources; execute only the exact verified collector blob buffer.

    Validator/interpreter/Git are inherited caller trust. Validator read-back is
    source consistency; it cannot authenticate the already-running entrypoint.
    Git blob bytes remain raw; only checkout comparison permits CRLF conversion.
    """
    global collection, _bootstrap_binding, _verified_sources
    collection = None
    _bootstrap_binding = {}
    _verified_sources = {}
    try:
        root = root.resolve()
        deadline = time.monotonic() + BOOTSTRAP_TIMEOUT
        top = Path(_bootstrap_git(root, ("rev-parse", "--show-toplevel"), deadline, own_group=_own_group).decode().strip()).resolve()
        _bootstrap_require(top == root, "BOOTSTRAP_ROOT_MISMATCH")
        _bootstrap_require(Path(__file__).resolve() == root / SCANNER_PATHS[0], "BOOTSTRAP_VALIDATOR_PATH")
        head = _bootstrap_git(root, ("rev-parse", "HEAD"), deadline, own_group=_own_group).decode("ascii").strip()
        _bootstrap_require(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", head) is not None,
                           "BOOTSTRAP_HEAD_FORMAT")
        if expected_head is not None:
            _bootstrap_require(head == expected_head, "BOOTSTRAP_HEAD_MISMATCH")
        _bootstrap_require(not _bootstrap_git(root, ("status", "--porcelain=v1", "--untracked-files=no"), deadline, own_group=_own_group),
                           "BOOTSTRAP_DIRTY_TREE")
        tree_bytes = _bootstrap_git(root, ("ls-tree", "-z", "--full-tree", head, "--", *SCANNER_PATHS), deadline, own_group=_own_group)
        rows = tree_bytes.split(b"\0")
        _bootstrap_require(rows[-1] == b"" and len(rows) == 3, "BOOTSTRAP_INVENTORY")
        sources: dict[str, bytes] = {}
        metadata: dict[str, Any] = {}
        for record in rows[:-1]:
            meta, path_bytes = record.split(b"\t", 1)
            mode, kind, oid = meta.decode("ascii").split()
            path = path_bytes.decode("utf-8", errors="strict")
            _bootstrap_require(path in SCANNER_PATHS and path not in sources, "BOOTSTRAP_INVENTORY")
            _bootstrap_require(mode in {"100644", "100755"} and kind == "blob", "BOOTSTRAP_SOURCE_TYPE")
            _bootstrap_require(re.fullmatch(r"[0-9a-f]{" + str(len(head)) + r"}", oid) is not None,
                               "BOOTSTRAP_BLOB_FORMAT")
            raw = _bootstrap_git(root, ("cat-file", "blob", oid), deadline, own_group=_own_group)
            _bootstrap_require(len(raw) <= BOOTSTRAP_MAX_SOURCE_BYTES and b"\0" not in raw,
                               "BOOTSTRAP_SOURCE_LIMIT")
            raw.decode("utf-8", errors="strict")
            object_bytes = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
            actual_oid = (hashlib.sha1(object_bytes).hexdigest() if len(oid) == 40
                          else hashlib.sha256(object_bytes).hexdigest())
            _bootstrap_require(actual_oid == oid, "BOOTSTRAP_BLOB_MISMATCH")
            working = _bootstrap_working_bytes(root, path)
            _bootstrap_require(working == raw or working.replace(b"\r\n", b"\n") == raw,
                               "BOOTSTRAP_SOURCE_MISMATCH")
            sources[path] = raw
            metadata[path] = {"blob_oid": oid, "raw_sha256": hashlib.sha256(raw).hexdigest(),
                              "byte_length": len(raw)}
        _bootstrap_require(set(sources) == set(SCANNER_PATHS), "BOOTSTRAP_INVENTORY")
        _bootstrap_require(_bootstrap_git(root, ("rev-parse", "HEAD"), deadline, own_group=_own_group).decode("ascii").strip() == head,
                           "BOOTSTRAP_HEAD_DRIFT")
        _bootstrap_require(not _bootstrap_git(root, ("status", "--porcelain=v1", "--untracked-files=no"), deadline, own_group=_own_group),
                           "BOOTSTRAP_SOURCE_DRIFT")
        _bootstrap_require(time.monotonic() < deadline, "BOOTSTRAP_TIMEOUT")
        # No source loader, cached bytecode, or reopening of the collector path.
        module = ModuleType("_secret_collection")
        module.__file__ = str(root / SCANNER_PATHS[1])
        exec(compile(sources[SCANNER_PATHS[1]], module.__file__, "exec"), module.__dict__)  # noqa: S102 -- execute only authenticated Git buffer
        collection = module
        _verified_sources = sources
        _bootstrap_binding = {"root": str(root), "head": head, "sources": metadata,
                              "validator_trust": "CALLER_TRUSTED_ENTRYPOINT",
                              "collector_loading": "VERIFIED_GIT_BLOB_BUFFER"}
        return dict(_bootstrap_binding)
    except BootstrapError:
        raise
    except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
        raise BootstrapError("BOOTSTRAP_SOURCE_FAILURE") from None


def _invalidate_receipt_before_bootstrap(root: Path, *, own_group: bool = True) -> None:
    """Invalidate stale output even if authentication or argument parsing fails."""
    target = root / "secret-scan-receipt.json"
    _bootstrap_require(not target.is_symlink() and not target.is_dir(), "UNSAFE_RECEIPT_PATH")
    tracked = _bootstrap_git(root, ("ls-files", "--", "secret-scan-receipt.json"),
                             time.monotonic() + BOOTSTRAP_TIMEOUT, limit=1024, own_group=own_group)
    _bootstrap_require(not tracked, "TRACKED_RECEIPT_PATH")
    target.unlink(missing_ok=True)

FILE_DIGESTS = {
    'docs/architecture/cp1/acceptance-scenarios.json': (107, 133, 220, 195, 37, 212, 134, 237, 122, 1, 163, 31, 104, 167, 146, 88, 240, 91, 234, 193, 46, 136, 15, 49, 83, 98, 125, 244, 168, 70, 62, 73),
    'docs/architecture/cp1/cp1.1-freeze-receipt.json': (143, 163, 219, 230, 72, 200, 42, 21, 221, 181, 3, 208, 158, 7, 139, 129, 39, 185, 210, 170, 219, 91, 241, 244, 236, 24, 122, 234, 9, 250, 29, 173),
    'docs/architecture/cp1/fixtures/manifest.json': (18, 147, 21, 82, 197, 192, 152, 108, 48, 118, 116, 42, 94, 172, 6, 140, 30, 248, 135, 36, 96, 225, 79, 182, 204, 110, 64, 134, 18, 66, 221, 8),
    'docs/architecture/cp1/persona-profile.yaml': (68, 25, 67, 1, 221, 64, 210, 25, 210, 71, 107, 230, 76, 245, 88, 11, 200, 54, 115, 253, 69, 96, 252, 249, 46, 40, 35, 207, 95, 3, 153, 23),
    'docs/architecture/cp1/persona-source-binding.json': (38, 71, 238, 140, 202, 134, 49, 98, 116, 105, 27, 93, 32, 101, 102, 55, 85, 90, 141, 64, 119, 135, 230, 4, 58, 171, 49, 37, 8, 234, 47, 245),
    'docs/architecture/cp1/prohibition-matrix-draft.json': (231, 130, 248, 72, 219, 255, 7, 148, 202, 57, 37, 79, 6, 72, 0, 180, 108, 61, 6, 154, 185, 163, 223, 146, 16, 160, 109, 190, 68, 233, 81, 220),
    'docs/architecture/cp1/reviews/cp11-review-manifest.json': (2, 134, 127, 96, 11, 15, 169, 151, 60, 36, 145, 29, 225, 158, 225, 94, 189, 45, 82, 17, 70, 74, 193, 134, 222, 216, 77, 196, 104, 199, 203, 14),
    'docs/architecture/cp1/reviews/final-contract-review-prefreeze.json': (185, 206, 216, 229, 16, 76, 37, 84, 60, 60, 145, 244, 155, 168, 203, 17, 76, 60, 96, 50, 224, 118, 115, 228, 93, 2, 138, 51, 28, 14, 254, 53),
    'docs/architecture/cp1/reviews/final-persona-review-prefreeze.json': (20, 207, 101, 87, 253, 243, 84, 50, 199, 211, 213, 233, 94, 165, 64, 40, 69, 2, 79, 58, 19, 161, 197, 70, 14, 122, 83, 192, 208, 159, 222, 76),
    'docs/architecture/cp1/schema-fixture-verification.json': (255, 212, 82, 51, 51, 141, 128, 105, 18, 177, 188, 244, 215, 247, 221, 50, 182, 76, 239, 13, 6, 191, 170, 159, 196, 117, 178, 102, 2, 17, 62, 172),
    'docs/architecture/persona/persona-profile.yaml': (181, 135, 242, 248, 90, 56, 170, 137, 8, 24, 185, 190, 218, 192, 136, 165, 220, 191, 112, 24, 37, 101, 61, 196, 244, 149, 240, 209, 241, 145, 225, 183),
    'docs/research/algorithm-donors/adoption-registry.yaml': (232, 38, 225, 155, 241, 135, 92, 224, 205, 94, 3, 99, 125, 166, 47, 56, 65, 169, 252, 91, 129, 74, 130, 139, 97, 154, 13, 132, 124, 76, 181, 221),
    'docs/research/algorithm-donors/receipts/ALG-REG-001-freeze.yaml': (204, 114, 241, 206, 13, 41, 36, 105, 61, 51, 4, 251, 7, 48, 118, 172, 131, 51, 46, 173, 231, 211, 247, 84, 81, 90, 124, 202, 250, 114, 162, 39),
    'docs/research/algorithm-donors/receipts/CP0_ADDENDUM_01_A01_REVIEW_a6c2f24.json': (73, 192, 23, 27, 18, 117, 73, 21, 134, 87, 88, 162, 41, 95, 14, 175, 173, 129, 86, 102, 233, 66, 139, 2, 61, 156, 252, 48, 21, 149, 178, 170),
    'docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json': (18, 121, 230, 54, 8, 69, 130, 198, 230, 148, 111, 143, 45, 43, 70, 167, 13, 142, 8, 152, 50, 115, 132, 144, 43, 232, 9, 57, 244, 150, 116, 140),
    'docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json': (13, 208, 112, 164, 38, 148, 132, 178, 229, 239, 216, 55, 203, 247, 67, 206, 149, 21, 84, 225, 52, 10, 222, 156, 233, 81, 60, 116, 95, 223, 146, 188),
    'docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute/intake-receipt.json': (125, 188, 224, 231, 97, 77, 47, 48, 29, 122, 151, 89, 236, 71, 170, 204, 108, 185, 165, 14, 202, 50, 151, 149, 10, 81, 2, 184, 174, 69, 174, 244),
    'docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json': (133, 221, 54, 174, 55, 1, 30, 228, 249, 59, 183, 225, 73, 40, 208, 136, 28, 106, 205, 66, 210, 184, 226, 188, 205, 14, 1, 212, 154, 205, 173, 58),
    'docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/manifest-snapshot.json': (108, 254, 213, 154, 103, 252, 61, 248, 46, 30, 157, 36, 138, 6, 214, 175, 113, 205, 170, 94, 90, 119, 79, 132, 45, 54, 175, 24, 205, 224, 188, 20),
    'docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json': (206, 134, 156, 47, 219, 48, 9, 172, 7, 158, 101, 222, 119, 197, 156, 105, 84, 116, 19, 140, 204, 122, 241, 39, 170, 90, 54, 42, 84, 219, 207, 181),
    'docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json': (240, 186, 5, 7, 84, 207, 12, 197, 75, 93, 62, 194, 93, 214, 51, 97, 53, 79, 98, 240, 89, 241, 25, 85, 100, 63, 236, 14, 46, 36, 230, 4),
    'docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json': (176, 116, 156, 47, 19, 3, 240, 101, 201, 82, 144, 221, 162, 156, 58, 248, 149, 43, 122, 168, 94, 66, 172, 99, 65, 226, 94, 196, 58, 185, 176, 186),
    'docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json': (89, 247, 50, 255, 84, 230, 147, 196, 96, 243, 85, 212, 121, 74, 24, 127, 196, 155, 232, 185, 37, 125, 123, 150, 10, 143, 194, 13, 48, 158, 31, 223),
    'docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/skill-candidates.json': (114, 178, 254, 131, 69, 166, 35, 195, 1, 126, 80, 165, 139, 200, 184, 242, 226, 242, 1, 251, 91, 13, 59, 84, 114, 125, 239, 11, 235, 92, 188, 148),
    'docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json': (110, 71, 66, 25, 243, 130, 145, 250, 42, 233, 17, 111, 56, 228, 132, 145, 207, 95, 70, 86, 190, 208, 244, 59, 234, 211, 52, 192, 162, 103, 13, 15),
    'docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json': (178, 91, 27, 97, 80, 177, 247, 182, 84, 146, 12, 50, 152, 248, 65, 222, 18, 88, 235, 36, 223, 157, 111, 123, 92, 30, 21, 108, 226, 219, 92, 126),
    'docs/verification/cp1.1-design-002-freeze-receipt.json': (153, 32, 181, 75, 78, 223, 49, 145, 140, 169, 86, 117, 77, 138, 177, 146, 113, 25, 155, 83, 231, 68, 88, 117, 22, 28, 191, 112, 187, 204, 69, 238),
    'docs/verification/cp1.1-design-002-independent-review.json': (239, 29, 180, 185, 171, 91, 220, 210, 64, 144, 248, 229, 122, 183, 11, 126, 126, 237, 154, 104, 210, 210, 232, 193, 255, 74, 67, 10, 134, 243, 154, 76),
    'docs/verification/cp1.1-design-002-review-manifest.json': (214, 41, 50, 187, 203, 252, 164, 89, 175, 101, 78, 218, 142, 213, 226, 237, 7, 53, 99, 234, 68, 30, 137, 227, 68, 61, 220, 2, 213, 208, 242, 207),
    'docs/verification/sentient-identity-20260928.json': (90, 18, 91, 128, 73, 58, 71, 103, 30, 66, 166, 105, 201, 235, 107, 135, 59, 159, 73, 222, 79, 120, 122, 152, 239, 45, 16, 104, 225, 15, 202, 7),
}

EXCEPTIONS = (
    ('docs/architecture/cp1/acceptance-scenarios.json', 5, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'base_commit'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 12, 'Hex High Entropy String', (40, 216, 226, 201, 77, 58, 50, 55, 181, 17, 7, 221, 62, 116, 141, 152, 138, 185, 134, 122), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 16, 'Hex High Entropy String', (104, 224, 25, 155, 139, 100, 133, 5, 58, 235, 71, 235, 234, 137, 131, 229, 39, 173, 242, 14), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 22, 'Hex High Entropy String', (252, 167, 183, 0, 238, 235, 53, 248, 61, 141, 183, 67, 153, 172, 59, 19, 91, 114, 177, 38), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 26, 'Hex High Entropy String', (167, 92, 232, 50, 130, 186, 82, 149, 51, 114, 249, 166, 165, 58, 226, 121, 168, 108, 238, 236), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 30, 'Hex High Entropy String', (203, 106, 166, 228, 208, 246, 170, 172, 0, 10, 197, 226, 31, 172, 9, 102, 52, 189, 100, 245), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 34, 'Hex High Entropy String', (36, 165, 88, 204, 189, 52, 63, 62, 133, 130, 84, 117, 49, 70, 26, 79, 166, 22, 144, 206), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 38, 'Hex High Entropy String', (34, 67, 26, 17, 89, 182, 101, 115, 171, 226, 70, 187, 66, 41, 92, 11, 25, 77, 116, 55), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 42, 'Hex High Entropy String', (142, 111, 102, 12, 131, 99, 218, 146, 182, 198, 120, 158, 180, 52, 137, 234, 130, 255, 247, 18), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 46, 'Hex High Entropy String', (82, 83, 120, 129, 11, 200, 209, 6, 166, 116, 5, 180, 82, 241, 208, 94, 204, 216, 70, 110), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 50, 'Hex High Entropy String', (68, 253, 142, 184, 169, 104, 112, 90, 23, 251, 159, 133, 244, 4, 156, 169, 119, 91, 42, 143), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 54, 'Hex High Entropy String', (199, 111, 227, 21, 141, 105, 130, 201, 184, 42, 68, 188, 21, 87, 52, 164, 238, 187, 3, 150), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 58, 'Hex High Entropy String', (213, 7, 47, 200, 91, 46, 121, 96, 75, 180, 71, 20, 55, 243, 235, 92, 81, 24, 146, 242), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 62, 'Hex High Entropy String', (243, 155, 70, 196, 127, 23, 7, 149, 201, 142, 199, 121, 250, 203, 231, 17, 65, 193, 88, 136), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 66, 'Hex High Entropy String', (223, 141, 240, 196, 183, 163, 48, 58, 99, 224, 180, 151, 254, 188, 207, 56, 49, 204, 178, 181), 'sha256'),
    ('docs/architecture/cp1/acceptance-scenarios.json', 70, 'Hex High Entropy String', (225, 118, 143, 206, 76, 152, 120, 14, 213, 73, 55, 94, 110, 135, 148, 111, 192, 168, 199, 141), 'sha256'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 8, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'base_sha'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 16, 'Hex High Entropy String', (255, 52, 141, 216, 156, 20, 44, 144, 115, 153, 206, 149, 181, 103, 154, 39, 137, 128, 232, 233), 'sha256'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 22, 'Hex High Entropy String', (170, 239, 145, 149, 195, 109, 125, 17, 204, 5, 0, 186, 248, 251, 37, 187, 225, 61, 61, 117), 'sha256'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 28, 'Hex High Entropy String', (21, 250, 247, 128, 81, 28, 154, 232, 75, 138, 74, 143, 252, 245, 31, 89, 86, 107, 193, 186), 'sha256'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 34, 'Hex High Entropy String', (119, 130, 135, 251, 138, 147, 61, 98, 140, 41, 209, 10, 36, 74, 89, 71, 73, 243, 66, 67), 'gateway-contract.md'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 35, 'Hex High Entropy String', (226, 238, 147, 135, 58, 236, 60, 26, 27, 64, 243, 108, 106, 26, 41, 1, 211, 21, 92, 74), 'gateway-schema.json'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 36, 'Hex High Entropy String', (216, 221, 15, 121, 10, 252, 59, 82, 25, 148, 145, 0, 5, 231, 89, 255, 48, 74, 12, 188), 'persona-guidance.md'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 37, 'Hex High Entropy String', (141, 8, 116, 33, 215, 97, 248, 68, 82, 232, 33, 229, 24, 183, 3, 69, 153, 37, 74, 196), 'persona-profile.yaml'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 38, 'Hex High Entropy String', (7, 69, 42, 201, 132, 192, 36, 213, 231, 205, 22, 251, 221, 6, 141, 120, 37, 67, 208, 118), 'acceptance-scenarios.json'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 39, 'Hex High Entropy String', (130, 163, 199, 214, 168, 52, 39, 164, 198, 206, 56, 113, 0, 150, 177, 81, 214, 39, 90, 255), 'prohibition-matrix.md'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 40, 'Hex High Entropy String', (79, 107, 43, 81, 254, 44, 165, 82, 18, 140, 104, 233, 217, 51, 166, 58, 47, 46, 164, 7), 'prohibition-matrix-draft.json'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 41, 'Hex High Entropy String', (222, 42, 167, 69, 157, 22, 106, 247, 129, 101, 183, 77, 128, 182, 50, 60, 186, 88, 67, 235), 'verify_contract_fixtures.py'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 42, 'Hex High Entropy String', (207, 43, 19, 151, 63, 181, 206, 2, 255, 178, 106, 175, 69, 84, 16, 21, 104, 61, 99, 107), 'schema-fixture-verification.json'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 43, 'Hex High Entropy String', (67, 197, 132, 179, 148, 231, 104, 17, 27, 157, 166, 3, 38, 107, 19, 75, 22, 190, 227, 172), 'fixtures/envelope.canonical.json'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 44, 'Hex High Entropy String', (10, 80, 108, 251, 161, 207, 134, 78, 144, 117, 40, 37, 161, 86, 127, 169, 149, 100, 51, 88), 'fixtures/request.canonical.json'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 45, 'Hex High Entropy String', (9, 128, 49, 224, 243, 247, 126, 92, 239, 37, 149, 32, 112, 94, 10, 27, 90, 150, 87, 16), 'fixtures/response.canonical.json'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 46, 'Hex High Entropy String', (196, 209, 4, 6, 26, 134, 170, 59, 28, 171, 251, 74, 194, 25, 83, 164, 189, 108, 119, 204), 'fixtures/manifest.json'),
    ('docs/architecture/cp1/cp1.1-freeze-receipt.json', 51, 'Hex High Entropy String', (63, 151, 77, 189, 199, 224, 63, 79, 5, 111, 116, 163, 76, 247, 215, 125, 232, 40, 218, 172), 'sha256_at_freeze'),
    ('docs/architecture/cp1/fixtures/manifest.json', 6, 'Hex High Entropy String', (67, 197, 132, 179, 148, 231, 104, 17, 27, 157, 166, 3, 38, 107, 19, 75, 22, 190, 227, 172), 'envelope.canonical.json'),
    ('docs/architecture/cp1/fixtures/manifest.json', 7, 'Hex High Entropy String', (10, 80, 108, 251, 161, 207, 134, 78, 144, 117, 40, 37, 161, 86, 127, 169, 149, 100, 51, 88), 'request.canonical.json'),
    ('docs/architecture/cp1/fixtures/manifest.json', 8, 'Hex High Entropy String', (9, 128, 49, 224, 243, 247, 126, 92, 239, 37, 149, 32, 112, 94, 10, 27, 90, 150, 87, 16), 'response.canonical.json'),
    ('docs/architecture/cp1/persona-profile.yaml', 5, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'base_sha'),
    ('docs/architecture/cp1/persona-profile.yaml', 8, 'Hex High Entropy String', (40, 216, 226, 201, 77, 58, 50, 55, 181, 17, 7, 221, 62, 116, 141, 152, 138, 185, 134, 122), 'sha256'),
    ('docs/architecture/cp1/persona-profile.yaml', 16, 'Hex High Entropy String', (104, 224, 25, 155, 139, 100, 133, 5, 58, 235, 71, 235, 234, 137, 131, 229, 39, 173, 242, 14), 'sha256'),
    ('docs/architecture/cp1/persona-profile.yaml', 66, 'Hex High Entropy String', (216, 221, 15, 121, 10, 252, 59, 82, 25, 148, 145, 0, 5, 231, 89, 255, 48, 74, 12, 188), 'sha256'),
    ('docs/architecture/cp1/persona-source-binding.json', 4, 'Hex High Entropy String', (105, 2, 120, 47, 34, 124, 26, 226, 112, 44, 49, 0, 60, 108, 113, 172, 105, 100, 45, 245), 'source_baseline_sha'),
    ('docs/architecture/cp1/persona-source-binding.json', 5, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'target_base_sha'),
    ('docs/architecture/cp1/persona-source-binding.json', 9, 'Hex High Entropy String', (40, 216, 226, 201, 77, 58, 50, 55, 181, 17, 7, 221, 62, 116, 141, 152, 138, 185, 134, 122), 'sha256'),
    ('docs/architecture/cp1/persona-source-binding.json', 17, 'Hex High Entropy String', (104, 224, 25, 155, 139, 100, 133, 5, 58, 235, 71, 235, 234, 137, 131, 229, 39, 173, 242, 14), 'sha256'),
    ('docs/architecture/cp1/persona-source-binding.json', 25, 'Hex High Entropy String', (105, 134, 247, 149, 242, 137, 232, 192, 123, 176, 27, 163, 156, 39, 26, 21, 151, 73, 134, 68), 'sha256'),
    ('docs/architecture/cp1/persona-source-binding.json', 28, 'Hex High Entropy String', (55, 90, 207, 249, 6, 69, 180, 110, 232, 105, 34, 117, 106, 61, 7, 78, 9, 73, 108, 55), 'historical_receipt_sha256'),
    ('docs/architecture/cp1/prohibition-matrix-draft.json', 3, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'base_sha'),
    ('docs/architecture/cp1/prohibition-matrix-draft.json', 14, 'Hex High Entropy String', (169, 224, 15, 15, 238, 176, 222, 242, 51, 183, 69, 53, 191, 32, 153, 246, 110, 229, 36, 197), 'docs/research/algorithm-donors/anti-pattern-registry.md'),
    ('docs/architecture/cp1/prohibition-matrix-draft.json', 15, 'Hex High Entropy String', (82, 79, 178, 186, 38, 235, 247, 138, 198, 15, 174, 178, 40, 147, 58, 27, 241, 53, 136, 241), 'docs/research/algorithm-donors/anti-patterns.md'),
    ('docs/architecture/cp1/prohibition-matrix-draft.json', 16, 'Hex High Entropy String', (128, 118, 119, 117, 221, 1, 211, 208, 222, 8, 115, 237, 37, 38, 178, 253, 146, 14, 209, 8), 'docs/research/algorithm-donors/adoption-registry.yaml'),
    ('docs/architecture/cp1/prohibition-matrix-draft.json', 17, 'Hex High Entropy String', (119, 130, 135, 251, 138, 147, 61, 98, 140, 41, 209, 10, 36, 74, 89, 71, 73, 243, 66, 67), 'docs/architecture/cp1/gateway-contract.md'),
    ('docs/architecture/cp1/prohibition-matrix-draft.json', 1607, 'Hex High Entropy String', (225, 118, 143, 206, 76, 152, 120, 14, 213, 73, 55, 94, 110, 135, 148, 111, 192, 168, 199, 141), 'historical_reviewed_sha256'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 2, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'base_sha'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 5, 'Hex High Entropy String', (119, 130, 135, 251, 138, 147, 61, 98, 140, 41, 209, 10, 36, 74, 89, 71, 73, 243, 66, 67), 'gateway-contract.md'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 6, 'Hex High Entropy String', (226, 238, 147, 135, 58, 236, 60, 26, 27, 64, 243, 108, 106, 26, 41, 1, 211, 21, 92, 74), 'gateway-schema.json'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 7, 'Hex High Entropy String', (216, 221, 15, 121, 10, 252, 59, 82, 25, 148, 145, 0, 5, 231, 89, 255, 48, 74, 12, 188), 'persona-guidance.md'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 8, 'Hex High Entropy String', (141, 8, 116, 33, 215, 97, 248, 68, 82, 232, 33, 229, 24, 183, 3, 69, 153, 37, 74, 196), 'persona-profile.yaml'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 9, 'Hex High Entropy String', (7, 69, 42, 201, 132, 192, 36, 213, 231, 205, 22, 251, 221, 6, 141, 120, 37, 67, 208, 118), 'acceptance-scenarios.json'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 10, 'Hex High Entropy String', (130, 163, 199, 214, 168, 52, 39, 164, 198, 206, 56, 113, 0, 150, 177, 81, 214, 39, 90, 255), 'prohibition-matrix.md'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 11, 'Hex High Entropy String', (79, 107, 43, 81, 254, 44, 165, 82, 18, 140, 104, 233, 217, 51, 166, 58, 47, 46, 164, 7), 'prohibition-matrix-draft.json'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 12, 'Hex High Entropy String', (222, 42, 167, 69, 157, 22, 106, 247, 129, 101, 183, 77, 128, 182, 50, 60, 186, 88, 67, 235), 'verify_contract_fixtures.py'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 13, 'Hex High Entropy String', (207, 43, 19, 151, 63, 181, 206, 2, 255, 178, 106, 175, 69, 84, 16, 21, 104, 61, 99, 107), 'schema-fixture-verification.json'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 14, 'Hex High Entropy String', (67, 197, 132, 179, 148, 231, 104, 17, 27, 157, 166, 3, 38, 107, 19, 75, 22, 190, 227, 172), 'fixtures/envelope.canonical.json'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 15, 'Hex High Entropy String', (10, 80, 108, 251, 161, 207, 134, 78, 144, 117, 40, 37, 161, 86, 127, 169, 149, 100, 51, 88), 'fixtures/request.canonical.json'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 16, 'Hex High Entropy String', (9, 128, 49, 224, 243, 247, 126, 92, 239, 37, 149, 32, 112, 94, 10, 27, 90, 150, 87, 16), 'fixtures/response.canonical.json'),
    ('docs/architecture/cp1/reviews/cp11-review-manifest.json', 17, 'Hex High Entropy String', (196, 209, 4, 6, 26, 134, 170, 59, 28, 171, 251, 74, 194, 25, 83, 164, 189, 108, 119, 204), 'fixtures/manifest.json'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 6, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'base_sha'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 8, 'Hex High Entropy String', (255, 52, 141, 216, 156, 20, 44, 144, 115, 153, 206, 149, 181, 103, 154, 39, 137, 128, 232, 233), 'manifest_sha256'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 10, 'Hex High Entropy String', (119, 130, 135, 251, 138, 147, 61, 98, 140, 41, 209, 10, 36, 74, 89, 71, 73, 243, 66, 67), 'gateway-contract.md'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 11, 'Hex High Entropy String', (226, 238, 147, 135, 58, 236, 60, 26, 27, 64, 243, 108, 106, 26, 41, 1, 211, 21, 92, 74), 'gateway-schema.json'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 12, 'Hex High Entropy String', (216, 221, 15, 121, 10, 252, 59, 82, 25, 148, 145, 0, 5, 231, 89, 255, 48, 74, 12, 188), 'persona-guidance.md'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 13, 'Hex High Entropy String', (141, 8, 116, 33, 215, 97, 248, 68, 82, 232, 33, 229, 24, 183, 3, 69, 153, 37, 74, 196), 'persona-profile.yaml'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 14, 'Hex High Entropy String', (7, 69, 42, 201, 132, 192, 36, 213, 231, 205, 22, 251, 221, 6, 141, 120, 37, 67, 208, 118), 'acceptance-scenarios.json'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 15, 'Hex High Entropy String', (130, 163, 199, 214, 168, 52, 39, 164, 198, 206, 56, 113, 0, 150, 177, 81, 214, 39, 90, 255), 'prohibition-matrix.md'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 16, 'Hex High Entropy String', (79, 107, 43, 81, 254, 44, 165, 82, 18, 140, 104, 233, 217, 51, 166, 58, 47, 46, 164, 7), 'prohibition-matrix-draft.json'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 17, 'Hex High Entropy String', (222, 42, 167, 69, 157, 22, 106, 247, 129, 101, 183, 77, 128, 182, 50, 60, 186, 88, 67, 235), 'verify_contract_fixtures.py'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 18, 'Hex High Entropy String', (207, 43, 19, 151, 63, 181, 206, 2, 255, 178, 106, 175, 69, 84, 16, 21, 104, 61, 99, 107), 'schema-fixture-verification.json'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 19, 'Hex High Entropy String', (67, 197, 132, 179, 148, 231, 104, 17, 27, 157, 166, 3, 38, 107, 19, 75, 22, 190, 227, 172), 'fixtures/envelope.canonical.json'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 20, 'Hex High Entropy String', (10, 80, 108, 251, 161, 207, 134, 78, 144, 117, 40, 37, 161, 86, 127, 169, 149, 100, 51, 88), 'fixtures/request.canonical.json'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 21, 'Hex High Entropy String', (9, 128, 49, 224, 243, 247, 126, 92, 239, 37, 149, 32, 112, 94, 10, 27, 90, 150, 87, 16), 'fixtures/response.canonical.json'),
    ('docs/architecture/cp1/reviews/final-contract-review-prefreeze.json', 22, 'Hex High Entropy String', (196, 209, 4, 6, 26, 134, 170, 59, 28, 171, 251, 74, 194, 25, 83, 164, 189, 108, 119, 204), 'fixtures/manifest.json'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 7, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'base_sha'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 8, 'Hex High Entropy String', (255, 52, 141, 216, 156, 20, 44, 144, 115, 153, 206, 149, 181, 103, 154, 39, 137, 128, 232, 233), 'review_manifest_sha256'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 14, 'Hex High Entropy String', (119, 130, 135, 251, 138, 147, 61, 98, 140, 41, 209, 10, 36, 74, 89, 71, 73, 243, 66, 67), 'gateway-contract.md'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 15, 'Hex High Entropy String', (226, 238, 147, 135, 58, 236, 60, 26, 27, 64, 243, 108, 106, 26, 41, 1, 211, 21, 92, 74), 'gateway-schema.json'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 16, 'Hex High Entropy String', (216, 221, 15, 121, 10, 252, 59, 82, 25, 148, 145, 0, 5, 231, 89, 255, 48, 74, 12, 188), 'persona-guidance.md'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 17, 'Hex High Entropy String', (141, 8, 116, 33, 215, 97, 248, 68, 82, 232, 33, 229, 24, 183, 3, 69, 153, 37, 74, 196), 'persona-profile.yaml'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 18, 'Hex High Entropy String', (7, 69, 42, 201, 132, 192, 36, 213, 231, 205, 22, 251, 221, 6, 141, 120, 37, 67, 208, 118), 'acceptance-scenarios.json'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 19, 'Hex High Entropy String', (130, 163, 199, 214, 168, 52, 39, 164, 198, 206, 56, 113, 0, 150, 177, 81, 214, 39, 90, 255), 'prohibition-matrix.md'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 20, 'Hex High Entropy String', (79, 107, 43, 81, 254, 44, 165, 82, 18, 140, 104, 233, 217, 51, 166, 58, 47, 46, 164, 7), 'prohibition-matrix-draft.json'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 21, 'Hex High Entropy String', (222, 42, 167, 69, 157, 22, 106, 247, 129, 101, 183, 77, 128, 182, 50, 60, 186, 88, 67, 235), 'verify_contract_fixtures.py'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 22, 'Hex High Entropy String', (207, 43, 19, 151, 63, 181, 206, 2, 255, 178, 106, 175, 69, 84, 16, 21, 104, 61, 99, 107), 'schema-fixture-verification.json'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 23, 'Hex High Entropy String', (67, 197, 132, 179, 148, 231, 104, 17, 27, 157, 166, 3, 38, 107, 19, 75, 22, 190, 227, 172), 'fixtures/envelope.canonical.json'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 24, 'Hex High Entropy String', (10, 80, 108, 251, 161, 207, 134, 78, 144, 117, 40, 37, 161, 86, 127, 169, 149, 100, 51, 88), 'fixtures/request.canonical.json'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 25, 'Hex High Entropy String', (9, 128, 49, 224, 243, 247, 126, 92, 239, 37, 149, 32, 112, 94, 10, 27, 90, 150, 87, 16), 'fixtures/response.canonical.json'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 26, 'Hex High Entropy String', (196, 209, 4, 6, 26, 134, 170, 59, 28, 171, 251, 74, 194, 25, 83, 164, 189, 108, 119, 204), 'fixtures/manifest.json'),
    ('docs/architecture/cp1/reviews/final-persona-review-prefreeze.json', 37, 'Hex High Entropy String', (127, 178, 170, 31, 55, 169, 59, 117, 49, 17, 225, 38, 49, 11, 150, 31, 201, 29, 104, 54), 'sha256'),
    ('docs/architecture/cp1/schema-fixture-verification.json', 66, 'Hex High Entropy String', (226, 238, 147, 135, 58, 236, 60, 26, 27, 64, 243, 108, 106, 26, 41, 1, 211, 21, 92, 74), 'gateway-schema.json'),
    ('docs/architecture/cp1/schema-fixture-verification.json', 67, 'Hex High Entropy String', (222, 42, 167, 69, 157, 22, 106, 247, 129, 101, 183, 77, 128, 182, 50, 60, 186, 88, 67, 235), 'verify_contract_fixtures.py'),
    ('docs/architecture/cp1/schema-fixture-verification.json', 68, 'Hex High Entropy String', (196, 209, 4, 6, 26, 134, 170, 59, 28, 171, 251, 74, 194, 25, 83, 164, 189, 108, 119, 204), 'fixtures/manifest.json'),
    ('docs/architecture/persona/persona-profile.yaml', 5, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'base_sha'),
    ('docs/architecture/persona/persona-profile.yaml', 8, 'Hex High Entropy String', (40, 216, 226, 201, 77, 58, 50, 55, 181, 17, 7, 221, 62, 116, 141, 152, 138, 185, 134, 122), 'sha256'),
    ('docs/architecture/persona/persona-profile.yaml', 16, 'Hex High Entropy String', (104, 224, 25, 155, 139, 100, 133, 5, 58, 235, 71, 235, 234, 137, 131, 229, 39, 173, 242, 14), 'sha256'),
    ('docs/architecture/persona/persona-profile.yaml', 66, 'Hex High Entropy String', (251, 164, 86, 240, 153, 237, 83, 79, 100, 76, 64, 74, 116, 65, 178, 192, 189, 214, 185, 246), 'sha256'),
    ('docs/architecture/persona/persona-profile.yaml', 105, 'Hex High Entropy String', (141, 8, 116, 33, 215, 97, 248, 68, 82, 232, 33, 229, 24, 183, 3, 69, 153, 37, 74, 196), 'sha256'),
    ('docs/architecture/persona/persona-profile.yaml', 107, 'Hex High Entropy String', (153, 123, 139, 254, 62, 31, 238, 60, 245, 30, 236, 50, 208, 188, 98, 85, 132, 116, 89, 25), 'source_commit'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5, 'Hex High Entropy String', (129, 133, 207, 144, 133, 204, 55, 202, 173, 209, 206, 101, 48, 121, 59, 94, 101, 28, 88, 255), 'cp0_accepted_sha'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 21, 'Hex High Entropy String', (80, 78, 174, 84, 238, 228, 198, 8, 172, 47, 44, 211, 130, 143, 75, 204, 184, 230, 211, 190), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 38, 'Hex High Entropy String', (92, 184, 5, 127, 71, 250, 115, 158, 105, 104, 35, 167, 38, 238, 15, 46, 194, 170, 25, 238), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 59, 'Hex High Entropy String', (222, 120, 222, 172, 138, 175, 143, 175, 200, 78, 126, 3, 9, 2, 144, 114, 137, 238, 167, 8), 'reported_donor_manifest_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 64, 'Hex High Entropy String', (190, 150, 128, 118, 212, 76, 116, 204, 170, 2, 88, 37, 65, 5, 19, 249, 152, 129, 178, 132), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 79, 'Hex High Entropy String', (232, 42, 165, 115, 126, 38, 51, 149, 154, 178, 67, 43, 13, 83, 155, 0, 139, 92, 104, 241), 'reported_donor_manifest_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 84, 'Hex High Entropy String', (216, 53, 173, 111, 37, 240, 218, 161, 253, 213, 213, 159, 156, 50, 113, 225, 46, 39, 77, 85), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 99, 'Hex High Entropy String', (152, 130, 38, 168, 46, 64, 69, 105, 182, 161, 167, 214, 41, 230, 66, 232, 54, 58, 235, 151), 'reported_donor_manifest_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 104, 'Hex High Entropy String', (93, 241, 28, 36, 80, 87, 120, 128, 237, 92, 197, 33, 249, 15, 89, 199, 102, 68, 15, 49), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 592, 'Hex High Entropy String', (85, 31, 156, 99, 254, 24, 229, 27, 42, 159, 219, 193, 181, 71, 148, 99, 158, 251, 176, 36), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 609, 'Hex High Entropy String', (213, 26, 72, 48, 174, 186, 234, 179, 201, 110, 203, 159, 178, 65, 171, 227, 236, 39, 223, 148), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 626, 'Hex High Entropy String', (121, 76, 47, 204, 224, 84, 102, 156, 134, 92, 169, 192, 111, 71, 36, 197, 118, 113, 235, 179), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 643, 'Hex High Entropy String', (131, 138, 110, 131, 10, 90, 1, 127, 31, 65, 159, 150, 119, 166, 184, 95, 200, 97, 142, 5), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 660, 'Hex High Entropy String', (68, 107, 82, 85, 218, 84, 240, 32, 207, 241, 252, 168, 78, 205, 213, 231, 89, 35, 34, 1), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 677, 'Hex High Entropy String', (98, 180, 225, 134, 120, 107, 4, 19, 246, 51, 247, 42, 216, 250, 118, 182, 116, 2, 145, 48), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 694, 'Hex High Entropy String', (3, 0, 154, 159, 95, 136, 141, 20, 234, 207, 1, 145, 59, 240, 190, 98, 90, 27, 94, 249), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 711, 'Hex High Entropy String', (151, 62, 204, 164, 81, 205, 255, 119, 205, 67, 31, 10, 135, 129, 3, 118, 140, 131, 245, 120), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 728, 'Hex High Entropy String', (57, 163, 83, 254, 219, 80, 166, 172, 129, 130, 204, 228, 154, 152, 48, 206, 38, 164, 159, 214), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 745, 'Hex High Entropy String', (127, 15, 11, 173, 173, 225, 161, 174, 42, 188, 43, 174, 105, 24, 96, 69, 64, 240, 13, 166), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 764, 'Hex High Entropy String', (85, 38, 87, 181, 73, 246, 75, 96, 166, 22, 93, 84, 242, 141, 243, 65, 97, 2, 50, 160), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 781, 'Hex High Entropy String', (207, 101, 120, 159, 80, 70, 174, 145, 206, 86, 40, 225, 248, 166, 217, 32, 131, 147, 243, 247), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 798, 'Hex High Entropy String', (255, 77, 112, 150, 91, 139, 112, 213, 134, 41, 56, 161, 122, 51, 115, 102, 251, 210, 148, 93), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 815, 'Hex High Entropy String', (213, 61, 79, 184, 174, 149, 7, 132, 54, 223, 47, 183, 230, 206, 156, 203, 10, 18, 202, 81), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 832, 'Hex High Entropy String', (204, 252, 105, 209, 34, 223, 203, 232, 111, 189, 38, 73, 42, 165, 60, 254, 229, 238, 254, 48), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 849, 'Hex High Entropy String', (152, 73, 62, 132, 25, 121, 141, 251, 40, 99, 211, 39, 56, 13, 214, 128, 243, 194, 255, 204), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 866, 'Hex High Entropy String', (233, 39, 50, 154, 248, 81, 4, 106, 126, 13, 242, 214, 119, 251, 111, 157, 78, 1, 40, 91), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 883, 'Hex High Entropy String', (68, 235, 248, 140, 88, 23, 164, 71, 83, 27, 129, 247, 32, 195, 143, 132, 25, 16, 100, 211), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 900, 'Hex High Entropy String', (89, 203, 177, 122, 42, 16, 183, 57, 203, 224, 139, 55, 20, 21, 208, 150, 49, 108, 236, 15), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 917, 'Hex High Entropy String', (96, 211, 136, 205, 110, 69, 189, 62, 63, 95, 187, 90, 141, 25, 186, 200, 250, 6, 176, 101), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 934, 'Hex High Entropy String', (45, 70, 92, 199, 63, 40, 153, 62, 227, 85, 46, 22, 51, 113, 19, 183, 145, 194, 143, 226), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 951, 'Hex High Entropy String', (232, 243, 196, 253, 251, 156, 83, 9, 232, 93, 228, 93, 30, 99, 215, 213, 51, 244, 254, 117), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 968, 'Hex High Entropy String', (72, 32, 143, 76, 255, 135, 207, 251, 54, 71, 224, 25, 183, 161, 101, 0, 217, 245, 73, 120), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 985, 'Hex High Entropy String', (87, 117, 253, 132, 136, 228, 232, 98, 240, 160, 108, 194, 199, 143, 133, 239, 36, 42, 109, 10), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1002, 'Hex High Entropy String', (125, 237, 108, 164, 56, 133, 81, 232, 15, 45, 107, 82, 100, 132, 113, 150, 232, 73, 255, 245), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1019, 'Hex High Entropy String', (247, 47, 194, 29, 90, 141, 136, 172, 11, 35, 101, 191, 76, 108, 195, 64, 227, 121, 173, 215), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1036, 'Hex High Entropy String', (79, 141, 246, 76, 238, 6, 75, 134, 113, 48, 193, 255, 55, 22, 150, 13, 27, 108, 38, 128), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1053, 'Hex High Entropy String', (248, 15, 154, 153, 169, 231, 245, 244, 79, 128, 5, 193, 192, 174, 236, 77, 52, 28, 255, 41), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1070, 'Hex High Entropy String', (176, 115, 227, 189, 44, 179, 187, 187, 59, 50, 18, 216, 242, 236, 182, 160, 15, 249, 248, 37), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1087, 'Hex High Entropy String', (45, 248, 16, 195, 201, 122, 57, 107, 19, 89, 206, 21, 188, 147, 223, 71, 186, 114, 149, 188), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1105, 'Hex High Entropy String', (117, 134, 156, 89, 175, 156, 141, 198, 18, 193, 38, 218, 43, 249, 184, 22, 143, 223, 15, 179), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1122, 'Hex High Entropy String', (21, 167, 123, 37, 56, 227, 185, 32, 71, 21, 65, 73, 227, 72, 200, 126, 234, 66, 19, 252), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1139, 'Hex High Entropy String', (6, 204, 247, 246, 110, 94, 209, 8, 18, 222, 114, 142, 59, 227, 49, 247, 179, 106, 41, 106), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1156, 'Hex High Entropy String', (7, 178, 25, 70, 233, 135, 30, 192, 99, 28, 142, 196, 208, 249, 50, 165, 89, 170, 174, 37), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1173, 'Hex High Entropy String', (155, 8, 206, 236, 40, 152, 238, 208, 113, 177, 206, 114, 225, 90, 255, 58, 29, 22, 230, 28), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1190, 'Hex High Entropy String', (159, 230, 21, 8, 80, 180, 17, 62, 153, 64, 246, 252, 85, 72, 207, 72, 108, 68, 245, 204), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1207, 'Hex High Entropy String', (245, 170, 65, 15, 91, 13, 197, 187, 144, 0, 219, 209, 154, 174, 181, 219, 85, 23, 46, 155), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1226, 'Hex High Entropy String', (94, 245, 69, 220, 199, 3, 13, 156, 53, 157, 237, 1, 79, 41, 120, 72, 32, 79, 221, 155), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1243, 'Hex High Entropy String', (181, 209, 211, 77, 71, 205, 180, 201, 61, 192, 92, 212, 57, 78, 200, 164, 191, 61, 101, 116), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1260, 'Hex High Entropy String', (126, 249, 173, 145, 163, 155, 221, 20, 69, 153, 46, 79, 209, 23, 183, 96, 20, 206, 222, 110), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1277, 'Hex High Entropy String', (152, 27, 143, 144, 103, 121, 139, 12, 249, 19, 150, 56, 175, 92, 145, 169, 238, 27, 136, 178), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1294, 'Hex High Entropy String', (160, 254, 2, 194, 226, 224, 50, 119, 15, 134, 9, 181, 201, 58, 186, 138, 113, 168, 99, 67), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1311, 'Hex High Entropy String', (46, 153, 17, 3, 35, 88, 111, 132, 183, 31, 13, 121, 85, 41, 216, 247, 24, 236, 182, 194), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1328, 'Hex High Entropy String', (83, 203, 79, 62, 97, 119, 183, 14, 203, 179, 26, 139, 201, 127, 181, 46, 195, 160, 81, 222), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1347, 'Hex High Entropy String', (5, 250, 41, 148, 47, 69, 25, 147, 130, 221, 121, 15, 96, 161, 170, 47, 192, 92, 153, 231), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1364, 'Hex High Entropy String', (48, 114, 116, 46, 60, 230, 32, 105, 59, 221, 67, 239, 135, 222, 19, 168, 135, 52, 43, 72), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1381, 'Hex High Entropy String', (85, 110, 179, 82, 143, 223, 233, 75, 188, 254, 31, 99, 17, 101, 68, 248, 0, 157, 190, 80), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1398, 'Hex High Entropy String', (162, 65, 7, 182, 216, 204, 230, 235, 225, 215, 84, 50, 210, 147, 45, 20, 61, 26, 70, 67), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1415, 'Hex High Entropy String', (44, 5, 186, 1, 141, 7, 241, 249, 36, 19, 223, 31, 94, 122, 34, 168, 44, 62, 189, 203), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1432, 'Hex High Entropy String', (43, 153, 246, 174, 204, 111, 88, 53, 100, 218, 135, 196, 71, 12, 242, 154, 39, 223, 170, 253), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1449, 'Hex High Entropy String', (56, 97, 8, 183, 4, 31, 164, 160, 225, 214, 241, 213, 90, 211, 192, 250, 130, 255, 241, 113), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1466, 'Hex High Entropy String', (223, 92, 20, 50, 92, 205, 131, 110, 199, 38, 239, 125, 63, 219, 168, 27, 251, 224, 101, 32), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1483, 'Hex High Entropy String', (152, 118, 167, 156, 171, 88, 141, 130, 122, 111, 162, 176, 250, 30, 50, 208, 85, 76, 135, 222), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1500, 'Hex High Entropy String', (89, 97, 79, 26, 84, 4, 194, 81, 143, 18, 201, 1, 70, 143, 206, 74, 233, 41, 115, 219), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1517, 'Hex High Entropy String', (176, 63, 183, 55, 91, 196, 180, 138, 235, 132, 240, 10, 210, 205, 177, 7, 126, 91, 189, 209), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1534, 'Hex High Entropy String', (164, 39, 171, 177, 147, 78, 172, 144, 174, 153, 173, 136, 84, 111, 26, 166, 33, 133, 33, 114), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1551, 'Hex High Entropy String', (22, 205, 135, 166, 79, 239, 83, 84, 248, 6, 132, 60, 188, 177, 75, 92, 83, 245, 217, 89), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1568, 'Hex High Entropy String', (71, 11, 29, 134, 85, 90, 15, 37, 252, 87, 217, 57, 156, 157, 230, 121, 26, 110, 49, 169), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1585, 'Hex High Entropy String', (184, 236, 172, 28, 92, 56, 192, 205, 35, 144, 80, 186, 204, 215, 104, 203, 74, 67, 150, 54), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1602, 'Hex High Entropy String', (29, 108, 216, 86, 216, 0, 45, 158, 85, 204, 254, 228, 156, 175, 77, 184, 171, 54, 8, 110), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1619, 'Hex High Entropy String', (83, 195, 23, 134, 187, 186, 224, 207, 156, 187, 39, 42, 32, 4, 232, 193, 115, 169, 139, 32), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1636, 'Hex High Entropy String', (78, 33, 157, 204, 202, 188, 24, 31, 18, 43, 185, 32, 14, 20, 208, 192, 71, 26, 164, 249), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1653, 'Hex High Entropy String', (213, 8, 128, 63, 36, 32, 93, 7, 11, 117, 120, 255, 249, 23, 229, 238, 67, 164, 201, 167), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1670, 'Hex High Entropy String', (215, 234, 138, 210, 96, 47, 212, 21, 151, 96, 73, 129, 131, 78, 90, 138, 161, 50, 228, 208), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1687, 'Hex High Entropy String', (223, 88, 105, 43, 177, 158, 205, 158, 251, 112, 83, 121, 92, 10, 182, 236, 232, 28, 129, 54), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1704, 'Hex High Entropy String', (252, 252, 67, 242, 44, 221, 125, 16, 83, 117, 62, 250, 207, 22, 203, 168, 200, 35, 174, 182), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 1721, 'Hex High Entropy String', (178, 80, 81, 110, 136, 20, 139, 84, 129, 116, 62, 81, 162, 237, 206, 249, 29, 35, 97, 39), 'source_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5681, 'Hex High Entropy String', (240, 101, 47, 37, 76, 76, 204, 31, 189, 216, 180, 216, 195, 99, 151, 182, 112, 231, 167, 104), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5687, 'Hex High Entropy String', (171, 243, 130, 76, 66, 184, 217, 131, 244, 157, 221, 124, 55, 110, 189, 179, 54, 41, 15, 9), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5693, 'Hex High Entropy String', (133, 86, 126, 204, 109, 55, 16, 93, 46, 89, 31, 100, 230, 176, 211, 177, 216, 135, 100, 24), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5699, 'Hex High Entropy String', (208, 24, 26, 216, 134, 74, 93, 250, 31, 190, 53, 115, 111, 90, 135, 151, 160, 229, 49, 11), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5705, 'Hex High Entropy String', (65, 205, 233, 160, 55, 190, 172, 180, 33, 161, 31, 92, 191, 200, 203, 174, 49, 138, 129, 244), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5711, 'Hex High Entropy String', (48, 184, 155, 210, 21, 188, 134, 73, 238, 49, 141, 101, 50, 118, 91, 166, 96, 45, 233, 14), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5720, 'Hex High Entropy String', (171, 16, 49, 88, 110, 81, 76, 68, 140, 181, 27, 40, 116, 230, 184, 178, 5, 175, 222, 147), 'reported_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5726, 'Hex High Entropy String', (86, 135, 42, 80, 27, 248, 173, 134, 47, 210, 47, 35, 154, 51, 132, 127, 250, 74, 199, 171), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5738, 'Hex High Entropy String', (147, 76, 11, 255, 157, 232, 186, 117, 162, 158, 113, 238, 223, 179, 26, 45, 167, 156, 242, 57), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5778, 'Hex High Entropy String', (205, 122, 30, 174, 237, 24, 93, 101, 8, 105, 228, 16, 127, 50, 61, 109, 77, 11, 60, 214), 'sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5800, 'Hex High Entropy String', (219, 59, 95, 40, 117, 202, 163, 172, 210, 6, 167, 134, 161, 95, 180, 221, 51, 172, 153, 134), 'reviewed_sha'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5816, 'Hex High Entropy String', (206, 220, 122, 51, 99, 176, 222, 193, 201, 254, 215, 215, 172, 166, 119, 156, 54, 156, 73, 1), 'review_receipt_sha256'),
    ('docs/research/algorithm-donors/adoption-registry.yaml', 5820, 'Hex High Entropy String', (11, 73, 201, 25, 121, 140, 80, 35, 238, 215, 117, 31, 152, 141, 108, 113, 201, 133, 61, 194), 'value'),
    ('docs/research/algorithm-donors/receipts/ALG-REG-001-freeze.yaml', 4, 'Hex High Entropy String', (219, 59, 95, 40, 117, 202, 163, 172, 210, 6, 167, 134, 161, 95, 180, 221, 51, 172, 153, 134), 'reviewed_source_commit'),
    ('docs/research/algorithm-donors/receipts/ALG-REG-001-freeze.yaml', 10, 'Hex High Entropy String', (206, 220, 122, 51, 99, 176, 222, 193, 201, 254, 215, 215, 172, 166, 119, 156, 54, 156, 73, 1), 'review_receipt_sha256'),
    ('docs/research/algorithm-donors/receipts/ALG-REG-001-freeze.yaml', 31, 'Hex High Entropy String', (129, 133, 207, 144, 133, 204, 55, 202, 173, 209, 206, 101, 48, 121, 59, 94, 101, 28, 88, 255), 'accepted_sha'),
    ('docs/research/algorithm-donors/receipts/ALG-REG-001-freeze.yaml', 36, 'Hex High Entropy String', (11, 73, 201, 25, 121, 140, 80, 35, 238, 215, 117, 31, 152, 141, 108, 113, 201, 133, 61, 194), 'adoption-registry.yaml'),
    ('docs/research/algorithm-donors/receipts/ALG-REG-001-freeze.yaml', 37, 'Hex High Entropy String', (169, 224, 15, 15, 238, 176, 222, 242, 51, 183, 69, 53, 191, 32, 153, 246, 110, 229, 36, 197), 'anti-pattern-registry.md'),
    ('docs/research/algorithm-donors/receipts/ALG-REG-001-freeze.yaml', 38, 'Hex High Entropy String', (82, 79, 178, 186, 38, 235, 247, 138, 198, 15, 174, 178, 40, 147, 58, 27, 241, 53, 136, 241), 'anti-patterns.md'),
    ('docs/research/algorithm-donors/receipts/ALG-REG-001-freeze.yaml', 39, 'Hex High Entropy String', (161, 124, 171, 0, 251, 21, 124, 30, 92, 216, 115, 55, 25, 30, 199, 164, 117, 222, 121, 143), 'codex-desktop-implementation-contract.md'),
    ('docs/research/algorithm-donors/receipts/ALG-REG-001-freeze.yaml', 41, 'Hex High Entropy String', (128, 118, 119, 117, 221, 1, 211, 208, 222, 8, 115, 237, 37, 38, 178, 253, 146, 14, 209, 8), 'adoption-registry.yaml'),
    ('docs/research/algorithm-donors/receipts/ALG-REG-001-freeze.yaml', 53, 'Hex High Entropy String', (59, 208, 109, 246, 225, 237, 8, 15, 134, 123, 63, 8, 18, 98, 120, 137, 174, 238, 247, 130), 'external_original_review_receipt_sha256'),
    ('docs/research/algorithm-donors/receipts/CP0_ADDENDUM_01_A01_REVIEW_a6c2f24.json', 2, 'Hex High Entropy String', (219, 59, 95, 40, 117, 202, 163, 172, 210, 6, 167, 134, 161, 95, 180, 221, 51, 172, 153, 134), 'reviewed_sha'),
    ('docs/research/algorithm-donors/receipts/CP0_ADDENDUM_01_A01_REVIEW_a6c2f24.json', 3, 'Hex High Entropy String', (212, 222, 61, 218, 176, 157, 83, 9, 108, 132, 27, 13, 7, 255, 206, 254, 189, 14, 201, 162), 'previous_sha'),
    ('docs/research/algorithm-donors/receipts/CP0_ADDENDUM_01_A01_REVIEW_a6c2f24.json', 4, 'Hex High Entropy String', (129, 133, 207, 144, 133, 204, 55, 202, 173, 209, 206, 101, 48, 121, 59, 94, 101, 28, 88, 255), 'cp0_accepted_sha'),
    ('docs/research/algorithm-donors/receipts/CP0_ADDENDUM_01_A01_REVIEW_a6c2f24.json', 10, 'Hex High Entropy String', (11, 73, 201, 25, 121, 140, 80, 35, 238, 215, 117, 31, 152, 141, 108, 113, 201, 133, 61, 194), 'registry_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 13, 'Hex High Entropy String', (53, 110, 155, 147, 173, 203, 248, 177, 132, 115, 219, 156, 170, 210, 86, 242, 93, 71, 210, 90), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 14, 'Hex High Entropy String', (255, 99, 49, 126, 208, 14, 252, 80, 159, 252, 90, 11, 194, 47, 159, 227, 222, 95, 95, 202), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 20, 'Hex High Entropy String', (143, 5, 223, 5, 60, 70, 111, 250, 68, 251, 117, 81, 7, 173, 189, 193, 98, 3, 231, 98), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 21, 'Hex High Entropy String', (60, 149, 245, 39, 120, 188, 27, 128, 3, 144, 130, 127, 185, 1, 84, 72, 225, 133, 37, 119), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 34, 'Hex High Entropy String', (184, 229, 146, 175, 224, 163, 4, 68, 173, 252, 14, 180, 173, 95, 160, 249, 217, 25, 22, 136), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 35, 'Hex High Entropy String', (195, 161, 20, 151, 178, 133, 25, 71, 85, 228, 62, 151, 120, 186, 138, 204, 113, 65, 196, 89), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 43, 'Hex High Entropy String', (208, 158, 162, 49, 87, 191, 185, 195, 73, 60, 120, 228, 77, 44, 72, 191, 153, 240, 164, 160), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 44, 'Hex High Entropy String', (117, 148, 58, 211, 37, 12, 208, 252, 200, 79, 98, 54, 127, 214, 196, 162, 254, 13, 73, 195), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 52, 'Hex High Entropy String', (253, 173, 214, 28, 151, 187, 174, 209, 173, 32, 184, 146, 166, 77, 178, 231, 91, 184, 212, 116), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 53, 'Hex High Entropy String', (230, 94, 170, 161, 216, 94, 81, 186, 169, 9, 51, 210, 87, 119, 202, 79, 129, 66, 206, 160), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 78, 'Hex High Entropy String', (170, 205, 157, 186, 193, 192, 87, 149, 70, 253, 245, 140, 23, 192, 137, 87, 253, 40, 27, 32), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 79, 'Hex High Entropy String', (174, 190, 239, 32, 16, 202, 85, 28, 11, 96, 68, 76, 15, 57, 42, 55, 104, 27, 214, 181), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 100, 'Hex High Entropy String', (153, 168, 137, 78, 232, 193, 26, 147, 148, 127, 11, 165, 17, 24, 158, 162, 82, 221, 206, 237), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 101, 'Hex High Entropy String', (48, 149, 145, 236, 182, 90, 26, 218, 194, 159, 203, 24, 216, 172, 188, 219, 53, 81, 15, 236), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 129, 'Hex High Entropy String', (11, 81, 41, 26, 199, 213, 127, 65, 60, 112, 19, 158, 128, 216, 65, 97, 121, 2, 103, 249), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 130, 'Hex High Entropy String', (55, 181, 143, 101, 17, 121, 48, 165, 199, 81, 117, 199, 103, 114, 78, 119, 25, 183, 95, 181), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 136, 'Hex High Entropy String', (208, 232, 2, 154, 108, 111, 211, 236, 36, 172, 168, 149, 11, 254, 205, 125, 161, 244, 113, 241), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 137, 'Hex High Entropy String', (19, 159, 250, 14, 242, 148, 105, 129, 181, 164, 99, 231, 116, 33, 84, 202, 255, 114, 227, 172), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 150, 'Hex High Entropy String', (151, 20, 149, 152, 91, 199, 189, 209, 37, 37, 146, 228, 52, 241, 74, 67, 179, 86, 161, 247), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 151, 'Hex High Entropy String', (216, 104, 186, 32, 214, 40, 190, 46, 22, 72, 57, 84, 82, 43, 157, 223, 163, 119, 165, 189), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 159, 'Hex High Entropy String', (194, 119, 184, 180, 39, 168, 236, 230, 151, 224, 121, 182, 236, 129, 212, 178, 80, 230, 139, 16), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 160, 'Hex High Entropy String', (58, 62, 111, 228, 46, 186, 215, 0, 215, 30, 225, 43, 148, 205, 33, 7, 201, 223, 233, 116), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 177, 'Hex High Entropy String', (45, 156, 142, 57, 217, 74, 226, 141, 35, 209, 117, 3, 98, 127, 140, 170, 174, 44, 226, 95), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 178, 'Hex High Entropy String', (196, 64, 98, 205, 27, 38, 158, 169, 116, 247, 168, 112, 186, 61, 83, 50, 172, 40, 105, 178), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 203, 'Hex High Entropy String', (203, 69, 88, 196, 75, 46, 21, 5, 164, 174, 116, 102, 196, 147, 214, 226, 133, 106, 0, 150), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 204, 'Hex High Entropy String', (230, 93, 56, 34, 104, 211, 178, 172, 37, 43, 75, 242, 213, 253, 67, 219, 140, 107, 20, 240), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 217, 'Hex High Entropy String', (98, 112, 158, 168, 60, 154, 89, 1, 98, 68, 158, 196, 192, 44, 144, 228, 62, 141, 15, 82), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 218, 'Hex High Entropy String', (155, 119, 101, 36, 182, 154, 39, 200, 34, 239, 186, 144, 72, 216, 94, 238, 161, 68, 225, 219), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 246, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'canonical_base_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/intake-receipt.json', 247, 'Hex High Entropy String', (84, 155, 213, 28, 63, 69, 196, 129, 214, 203, 75, 137, 141, 51, 3, 157, 78, 149, 157, 34), 'manifest_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 11, 'Hex High Entropy String', (53, 110, 155, 147, 173, 203, 248, 177, 132, 115, 219, 156, 170, 210, 86, 242, 93, 71, 210, 90), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 12, 'Hex High Entropy String', (255, 99, 49, 126, 208, 14, 252, 80, 159, 252, 90, 11, 194, 47, 159, 227, 222, 95, 95, 202), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 18, 'Hex High Entropy String', (143, 5, 223, 5, 60, 70, 111, 250, 68, 251, 117, 81, 7, 173, 189, 193, 98, 3, 231, 98), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 19, 'Hex High Entropy String', (60, 149, 245, 39, 120, 188, 27, 128, 3, 144, 130, 127, 185, 1, 84, 72, 225, 133, 37, 119), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 32, 'Hex High Entropy String', (253, 173, 214, 28, 151, 187, 174, 209, 173, 32, 184, 146, 166, 77, 178, 231, 91, 184, 212, 116), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 33, 'Hex High Entropy String', (230, 94, 170, 161, 216, 94, 81, 186, 169, 9, 51, 210, 87, 119, 202, 79, 129, 66, 206, 160), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 58, 'Hex High Entropy String', (170, 205, 157, 186, 193, 192, 87, 149, 70, 253, 245, 140, 23, 192, 137, 87, 253, 40, 27, 32), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 59, 'Hex High Entropy String', (174, 190, 239, 32, 16, 202, 85, 28, 11, 96, 68, 76, 15, 57, 42, 55, 104, 27, 214, 181), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 80, 'Hex High Entropy String', (153, 168, 137, 78, 232, 193, 26, 147, 148, 127, 11, 165, 17, 24, 158, 162, 82, 221, 206, 237), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 81, 'Hex High Entropy String', (48, 149, 145, 236, 182, 90, 26, 218, 194, 159, 203, 24, 216, 172, 188, 219, 53, 81, 15, 236), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 115, 'Hex High Entropy String', (11, 81, 41, 26, 199, 213, 127, 65, 60, 112, 19, 158, 128, 216, 65, 97, 121, 2, 103, 249), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 116, 'Hex High Entropy String', (55, 181, 143, 101, 17, 121, 48, 165, 199, 81, 117, 199, 103, 114, 78, 119, 25, 183, 95, 181), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 122, 'Hex High Entropy String', (208, 232, 2, 154, 108, 111, 211, 236, 36, 172, 168, 149, 11, 254, 205, 125, 161, 244, 113, 241), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 123, 'Hex High Entropy String', (19, 159, 250, 14, 242, 148, 105, 129, 181, 164, 99, 231, 116, 33, 84, 202, 255, 114, 227, 172), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 136, 'Hex High Entropy String', (194, 119, 184, 180, 39, 168, 236, 230, 151, 224, 121, 182, 236, 129, 212, 178, 80, 230, 139, 16), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 137, 'Hex High Entropy String', (58, 62, 111, 228, 46, 186, 215, 0, 215, 30, 225, 43, 148, 205, 33, 7, 201, 223, 233, 116), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 154, 'Hex High Entropy String', (45, 156, 142, 57, 217, 74, 226, 141, 35, 209, 117, 3, 98, 127, 140, 170, 174, 44, 226, 95), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 155, 'Hex High Entropy String', (196, 64, 98, 205, 27, 38, 158, 169, 116, 247, 168, 112, 186, 61, 83, 50, 172, 40, 105, 178), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 180, 'Hex High Entropy String', (203, 69, 88, 196, 75, 46, 21, 5, 164, 174, 116, 102, 196, 147, 214, 226, 133, 106, 0, 150), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 181, 'Hex High Entropy String', (230, 93, 56, 34, 104, 211, 178, 172, 37, 43, 75, 242, 213, 253, 67, 219, 140, 107, 20, 240), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 194, 'Hex High Entropy String', (98, 112, 158, 168, 60, 154, 89, 1, 98, 68, 158, 196, 192, 44, 144, 228, 62, 141, 15, 82), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute-retry/skill-candidates.json', 195, 'Hex High Entropy String', (155, 119, 101, 36, 182, 154, 39, 200, 34, 239, 186, 144, 72, 216, 94, 238, 161, 68, 225, 219), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute/intake-receipt.json', 6, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'canonical_base_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute/intake-receipt.json', 9, 'Hex High Entropy String', (84, 155, 213, 28, 63, 69, 196, 129, 214, 203, 75, 137, 141, 51, 3, 157, 78, 149, 157, 34), 'manifest_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute/intake-receipt.json', 31, 'Hex High Entropy String', (53, 110, 155, 147, 173, 203, 248, 177, 132, 115, 219, 156, 170, 210, 86, 242, 93, 71, 210, 90), 'historical_head_observation'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/compute/intake-receipt.json', 55, 'Hex High Entropy String', (11, 81, 41, 26, 199, 213, 127, 65, 60, 112, 19, 158, 128, 216, 65, 97, 121, 2, 103, 249), 'historical_head_observation'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 5, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'canonical_base_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 16, 'Hex High Entropy String', (84, 155, 213, 28, 63, 69, 196, 129, 214, 203, 75, 137, 141, 51, 3, 157, 78, 149, 157, 34), 'manifest_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 56, 'Hex High Entropy String', (159, 89, 138, 209, 200, 28, 17, 220, 203, 226, 8, 42, 190, 17, 170, 219, 163, 141, 64, 6), 'receipt_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 80, 'Hex High Entropy String', (17, 217, 77, 43, 14, 33, 27, 229, 111, 224, 110, 130, 70, 141, 191, 15, 24, 84, 236, 31), 'commit'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 81, 'Hex High Entropy String', (204, 217, 21, 222, 150, 70, 202, 109, 119, 83, 116, 236, 85, 49, 30, 131, 179, 161, 190, 204), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 85, 'Hex High Entropy String', (186, 3, 133, 242, 182, 196, 214, 202, 186, 36, 183, 107, 12, 173, 94, 200, 219, 157, 35, 2), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 86, 'Hex High Entropy String', (169, 245, 128, 253, 86, 234, 187, 195, 20, 19, 173, 121, 136, 187, 55, 136, 155, 182, 119, 120), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 102, 'Hex High Entropy String', (12, 113, 235, 162, 53, 135, 157, 0, 9, 79, 105, 50, 36, 19, 43, 152, 239, 147, 236, 165), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 103, 'Hex High Entropy String', (137, 51, 132, 198, 153, 74, 112, 67, 164, 144, 78, 97, 244, 177, 247, 86, 207, 87, 119, 251), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 114, 'Hex High Entropy String', (18, 5, 154, 150, 142, 73, 51, 143, 105, 148, 196, 101, 34, 176, 136, 1, 237, 61, 76, 174), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 115, 'Hex High Entropy String', (146, 245, 195, 147, 252, 220, 208, 116, 92, 118, 0, 251, 250, 225, 143, 200, 41, 242, 188, 61), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 126, 'Hex High Entropy String', (112, 243, 169, 19, 108, 49, 38, 201, 178, 61, 213, 182, 111, 111, 121, 190, 149, 35, 134, 234), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 127, 'Hex High Entropy String', (98, 41, 161, 48, 142, 22, 170, 40, 142, 118, 87, 135, 161, 80, 186, 122, 223, 65, 116, 87), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 143, 'Hex High Entropy String', (158, 29, 38, 4, 146, 78, 45, 9, 175, 89, 12, 46, 196, 127, 135, 76, 2, 238, 107, 180), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 144, 'Hex High Entropy String', (213, 112, 155, 87, 136, 24, 44, 179, 101, 15, 62, 146, 252, 155, 104, 97, 100, 199, 87, 113), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 160, 'Hex High Entropy String', (255, 34, 237, 67, 47, 113, 76, 152, 217, 204, 231, 113, 214, 140, 100, 98, 98, 171, 163, 26), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 161, 'Hex High Entropy String', (126, 144, 222, 141, 50, 159, 7, 83, 183, 221, 6, 128, 44, 123, 180, 40, 77, 235, 103, 168), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 177, 'Hex High Entropy String', (250, 86, 215, 116, 134, 226, 131, 210, 17, 129, 97, 79, 184, 72, 243, 180, 177, 91, 85, 100), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 178, 'Hex High Entropy String', (119, 160, 175, 202, 90, 66, 65, 181, 198, 146, 245, 249, 215, 205, 141, 141, 49, 66, 191, 19), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 194, 'Hex High Entropy String', (202, 38, 9, 67, 13, 175, 93, 100, 223, 251, 224, 8, 188, 1, 185, 99, 79, 190, 105, 230), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 195, 'Hex High Entropy String', (190, 220, 73, 38, 37, 85, 149, 150, 128, 55, 75, 241, 240, 49, 8, 1, 30, 243, 12, 132), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 206, 'Hex High Entropy String', (98, 192, 200, 126, 58, 145, 222, 233, 255, 91, 173, 99, 177, 226, 82, 172, 164, 134, 251, 23), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 207, 'Hex High Entropy String', (203, 87, 118, 247, 62, 198, 29, 33, 96, 167, 250, 34, 17, 53, 117, 230, 110, 219, 180, 99), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 223, 'Hex High Entropy String', (47, 201, 159, 123, 105, 213, 234, 26, 176, 121, 72, 50, 206, 231, 216, 93, 73, 127, 183, 9), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 224, 'Hex High Entropy String', (56, 189, 98, 144, 73, 77, 206, 3, 191, 188, 132, 59, 242, 119, 100, 37, 243, 32, 106, 122), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 240, 'Hex High Entropy String', (165, 235, 2, 107, 116, 202, 202, 26, 89, 97, 76, 181, 104, 64, 122, 76, 187, 106, 235, 190), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 241, 'Hex High Entropy String', (64, 120, 31, 28, 24, 74, 58, 248, 93, 134, 223, 97, 3, 192, 90, 1, 161, 255, 255, 117), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 279, 'Hex High Entropy String', (5, 246, 149, 251, 209, 231, 66, 207, 229, 38, 71, 245, 183, 3, 31, 243, 161, 118, 35, 19), 'commit'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 280, 'Hex High Entropy String', (139, 157, 74, 160, 77, 129, 112, 92, 230, 124, 63, 136, 106, 101, 117, 206, 42, 160, 39, 199), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 284, 'Hex High Entropy String', (115, 27, 125, 152, 49, 62, 162, 248, 212, 227, 235, 181, 69, 102, 234, 59, 8, 61, 198, 222), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 285, 'Hex High Entropy String', (225, 80, 246, 213, 90, 21, 246, 55, 31, 218, 0, 49, 31, 241, 8, 140, 91, 3, 218, 137), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 301, 'Hex High Entropy String', (96, 138, 169, 118, 144, 128, 26, 206, 205, 79, 114, 91, 219, 37, 96, 188, 243, 4, 171, 229), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 302, 'Hex High Entropy String', (74, 51, 174, 183, 85, 50, 254, 182, 177, 119, 251, 111, 146, 152, 147, 67, 3, 21, 161, 32), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 313, 'Hex High Entropy String', (44, 194, 122, 96, 26, 203, 253, 89, 108, 23, 15, 73, 97, 156, 211, 224, 32, 159, 213, 96), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 314, 'Hex High Entropy String', (91, 181, 212, 55, 70, 73, 191, 135, 197, 124, 165, 127, 53, 69, 210, 26, 19, 91, 4, 224), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 330, 'Hex High Entropy String', (133, 189, 186, 184, 87, 123, 215, 75, 63, 26, 104, 77, 20, 94, 20, 127, 1, 29, 162, 173), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 331, 'Hex High Entropy String', (86, 144, 44, 115, 167, 138, 5, 48, 7, 151, 197, 240, 254, 65, 81, 36, 137, 90, 157, 221), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 347, 'Hex High Entropy String', (248, 209, 19, 131, 39, 236, 12, 68, 246, 238, 33, 234, 2, 39, 45, 142, 234, 211, 163, 234), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 348, 'Hex High Entropy String', (64, 238, 10, 92, 138, 61, 40, 70, 61, 174, 159, 16, 54, 144, 146, 253, 134, 125, 252, 90), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 364, 'Hex High Entropy String', (177, 219, 127, 14, 229, 160, 55, 159, 238, 199, 149, 186, 177, 76, 67, 55, 69, 210, 142, 155), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 365, 'Hex High Entropy String', (8, 183, 173, 204, 184, 117, 212, 181, 108, 72, 166, 73, 215, 255, 181, 218, 21, 63, 217, 190), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 381, 'Hex High Entropy String', (182, 130, 176, 131, 55, 4, 244, 76, 212, 81, 235, 8, 117, 78, 17, 44, 45, 4, 43, 188), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 382, 'Hex High Entropy String', (231, 213, 136, 148, 74, 148, 4, 207, 50, 92, 0, 14, 228, 72, 21, 147, 202, 1, 104, 195), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 398, 'Hex High Entropy String', (29, 53, 81, 29, 31, 160, 125, 154, 215, 124, 51, 151, 64, 173, 206, 131, 167, 99, 171, 28), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 399, 'Hex High Entropy String', (116, 229, 170, 176, 22, 195, 51, 146, 154, 34, 87, 112, 17, 42, 118, 188, 106, 48, 133, 131), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 415, 'Hex High Entropy String', (223, 213, 219, 5, 104, 40, 123, 217, 1, 130, 153, 91, 148, 242, 212, 118, 253, 88, 60, 234), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 416, 'Hex High Entropy String', (220, 55, 118, 126, 125, 241, 40, 104, 139, 228, 162, 104, 99, 196, 52, 122, 98, 135, 173, 217), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 432, 'Hex High Entropy String', (94, 69, 104, 143, 181, 130, 181, 84, 233, 127, 96, 53, 75, 199, 236, 93, 96, 60, 204, 14), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 433, 'Hex High Entropy String', (219, 154, 221, 172, 26, 62, 98, 198, 197, 157, 200, 191, 20, 150, 157, 96, 224, 170, 189, 129), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 449, 'Hex High Entropy String', (110, 205, 250, 39, 150, 22, 30, 182, 64, 222, 245, 54, 108, 124, 81, 203, 232, 188, 61, 31), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 450, 'Hex High Entropy String', (71, 190, 78, 139, 194, 211, 201, 180, 167, 2, 81, 117, 150, 76, 231, 50, 17, 55, 78, 244), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 492, 'Hex High Entropy String', (196, 154, 46, 215, 66, 139, 85, 88, 109, 184, 130, 9, 71, 111, 46, 199, 160, 34, 48, 15), 'receipt_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 515, 'Hex High Entropy String', (114, 187, 144, 88, 169, 252, 173, 43, 67, 238, 103, 54, 218, 215, 128, 153, 172, 193, 195, 170), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 516, 'Hex High Entropy String', (227, 143, 91, 21, 154, 163, 36, 133, 138, 80, 247, 75, 179, 134, 106, 85, 68, 189, 234, 80), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 521, 'Hex High Entropy String', (42, 196, 30, 169, 129, 140, 170, 100, 131, 185, 231, 96, 43, 15, 54, 33, 158, 88, 243, 233), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 522, 'Hex High Entropy String', (5, 51, 215, 83, 148, 244, 22, 180, 92, 1, 48, 21, 145, 13, 226, 167, 252, 114, 143, 92), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 530, 'Hex High Entropy String', (193, 210, 65, 8, 157, 72, 55, 62, 141, 11, 119, 28, 174, 171, 222, 110, 158, 190, 11, 31), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 531, 'Hex High Entropy String', (191, 163, 154, 118, 174, 38, 39, 116, 228, 196, 68, 161, 154, 73, 226, 103, 154, 72, 152, 45), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 539, 'Hex High Entropy String', (80, 212, 208, 1, 2, 129, 152, 139, 108, 248, 146, 36, 127, 44, 69, 36, 150, 159, 79, 221), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 540, 'Hex High Entropy String', (180, 101, 120, 47, 238, 205, 87, 139, 60, 45, 136, 251, 69, 145, 223, 69, 32, 75, 156, 255), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 548, 'Hex High Entropy String', (166, 6, 173, 241, 239, 234, 48, 159, 92, 205, 188, 164, 139, 138, 89, 240, 105, 58, 211, 154), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 549, 'Hex High Entropy String', (118, 178, 123, 174, 6, 65, 187, 116, 136, 139, 246, 2, 229, 232, 138, 249, 63, 242, 18, 213), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 557, 'Hex High Entropy String', (117, 22, 176, 248, 188, 24, 83, 35, 108, 215, 122, 18, 129, 0, 169, 203, 176, 12, 12, 72), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 558, 'Hex High Entropy String', (182, 54, 231, 9, 100, 22, 21, 181, 116, 197, 254, 17, 212, 139, 180, 59, 210, 69, 166, 81), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 566, 'Hex High Entropy String', (65, 226, 20, 203, 49, 134, 177, 188, 104, 120, 125, 105, 175, 48, 97, 57, 170, 195, 200, 232), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 567, 'Hex High Entropy String', (24, 202, 137, 170, 95, 141, 43, 9, 95, 216, 51, 118, 254, 50, 142, 207, 140, 195, 17, 203), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 575, 'Hex High Entropy String', (159, 20, 60, 79, 244, 231, 161, 112, 104, 127, 23, 165, 1, 63, 222, 201, 74, 62, 54, 242), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 576, 'Hex High Entropy String', (214, 5, 110, 56, 73, 222, 112, 239, 70, 167, 79, 31, 121, 86, 77, 72, 144, 18, 39, 204), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 584, 'Hex High Entropy String', (170, 110, 11, 202, 206, 128, 100, 69, 79, 216, 187, 117, 108, 96, 64, 233, 154, 124, 19, 116), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 585, 'Hex High Entropy String', (218, 208, 42, 81, 39, 28, 236, 208, 159, 142, 2, 36, 203, 35, 217, 233, 130, 232, 83, 233), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 616, 'Hex High Entropy String', (133, 161, 133, 205, 195, 204, 20, 9, 216, 82, 33, 127, 51, 158, 135, 63, 74, 50, 153, 238), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 617, 'Hex High Entropy String', (57, 172, 6, 243, 145, 16, 36, 205, 203, 58, 233, 221, 91, 106, 152, 121, 15, 96, 119, 20), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 622, 'Hex High Entropy String', (87, 44, 201, 53, 193, 243, 97, 56, 166, 251, 133, 81, 64, 25, 1, 150, 165, 40, 187, 77), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 623, 'Hex High Entropy String', (195, 191, 8, 48, 16, 229, 196, 188, 58, 255, 1, 98, 210, 66, 66, 137, 126, 73, 7, 224), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 631, 'Hex High Entropy String', (146, 160, 12, 191, 126, 126, 226, 178, 81, 61, 190, 38, 75, 12, 120, 128, 105, 90, 126, 43), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 632, 'Hex High Entropy String', (83, 34, 205, 237, 223, 166, 51, 1, 188, 253, 91, 166, 198, 132, 226, 175, 183, 26, 13, 6), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 640, 'Hex High Entropy String', (160, 162, 162, 101, 98, 95, 43, 85, 95, 113, 224, 195, 155, 17, 203, 230, 223, 178, 186, 72), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 641, 'Hex High Entropy String', (92, 43, 104, 105, 234, 44, 184, 167, 89, 92, 136, 248, 18, 206, 148, 56, 228, 16, 216, 39), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 649, 'Hex High Entropy String', (212, 18, 68, 134, 13, 83, 91, 138, 26, 7, 161, 96, 177, 54, 174, 136, 252, 154, 141, 113), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 650, 'Hex High Entropy String', (138, 222, 136, 73, 24, 61, 127, 41, 210, 138, 193, 130, 251, 154, 29, 140, 108, 71, 110, 82), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 658, 'Hex High Entropy String', (233, 26, 27, 103, 96, 108, 181, 92, 180, 10, 148, 126, 197, 160, 238, 88, 159, 121, 166, 200), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 659, 'Hex High Entropy String', (160, 207, 58, 40, 246, 87, 25, 90, 144, 81, 108, 212, 165, 116, 176, 50, 200, 140, 249, 72), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 667, 'Hex High Entropy String', (108, 83, 102, 68, 244, 167, 223, 82, 165, 95, 222, 194, 4, 38, 249, 160, 31, 143, 166, 39), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 668, 'Hex High Entropy String', (103, 7, 210, 196, 218, 126, 117, 151, 242, 233, 106, 31, 23, 203, 62, 142, 113, 183, 193, 180), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 711, 'Hex High Entropy String', (88, 6, 196, 27, 105, 67, 153, 97, 196, 153, 243, 253, 35, 25, 131, 169, 146, 114, 125, 155), 'receipt_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 720, 'Hex High Entropy String', (149, 56, 48, 73, 115, 230, 189, 0, 111, 165, 10, 61, 20, 244, 87, 148, 42, 52, 253, 69), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 721, 'Hex High Entropy String', (32, 177, 4, 55, 245, 249, 37, 39, 116, 254, 25, 55, 53, 69, 224, 61, 105, 86, 193, 118), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 728, 'Hex High Entropy String', (129, 163, 178, 150, 94, 94, 92, 114, 50, 2, 88, 244, 43, 139, 220, 83, 217, 238, 120, 116), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 730, 'Hex High Entropy String', (44, 124, 73, 254, 162, 44, 226, 0, 156, 27, 4, 123, 247, 248, 145, 99, 124, 175, 46, 162), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 737, 'Hex High Entropy String', (113, 216, 115, 8, 190, 165, 228, 118, 95, 3, 151, 118, 55, 9, 192, 225, 175, 16, 198, 187), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 739, 'Hex High Entropy String', (128, 35, 253, 17, 22, 179, 174, 15, 224, 3, 149, 200, 205, 36, 106, 178, 20, 97, 23, 52), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 746, 'Hex High Entropy String', (33, 54, 99, 160, 242, 94, 91, 95, 242, 104, 155, 53, 160, 50, 92, 254, 118, 92, 237, 159), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 748, 'Hex High Entropy String', (85, 131, 115, 38, 93, 52, 195, 165, 71, 143, 53, 24, 162, 233, 234, 184, 87, 140, 154, 204), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 755, 'Hex High Entropy String', (62, 58, 169, 211, 179, 212, 160, 244, 44, 94, 107, 152, 135, 242, 107, 96, 55, 21, 17, 247), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 757, 'Hex High Entropy String', (191, 24, 114, 165, 40, 194, 23, 105, 53, 30, 180, 180, 223, 240, 98, 76, 169, 158, 224, 28), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 764, 'Hex High Entropy String', (49, 98, 169, 76, 147, 51, 76, 153, 163, 143, 104, 129, 140, 220, 45, 108, 89, 15, 14, 76), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 766, 'Hex High Entropy String', (135, 174, 101, 142, 119, 41, 21, 63, 114, 18, 53, 93, 147, 225, 95, 1, 34, 218, 201, 109), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 773, 'Hex High Entropy String', (254, 107, 53, 65, 199, 104, 35, 86, 173, 7, 211, 111, 235, 170, 167, 178, 168, 215, 68, 77), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 775, 'Hex High Entropy String', (217, 53, 171, 14, 17, 96, 219, 109, 19, 40, 4, 16, 18, 28, 75, 232, 5, 32, 34, 48), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 782, 'Hex High Entropy String', (182, 128, 69, 219, 14, 33, 195, 182, 248, 51, 128, 163, 159, 201, 243, 142, 202, 77, 128, 19), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 784, 'Hex High Entropy String', (30, 76, 120, 90, 154, 90, 245, 91, 157, 34, 50, 239, 234, 178, 249, 151, 54, 71, 192, 186), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 791, 'Hex High Entropy String', (74, 36, 130, 76, 94, 207, 106, 99, 87, 59, 106, 181, 178, 183, 80, 25, 226, 233, 28, 16), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 793, 'Hex High Entropy String', (85, 19, 63, 79, 202, 1, 106, 115, 155, 95, 11, 70, 229, 41, 128, 9, 147, 171, 175, 33), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 800, 'Hex High Entropy String', (84, 160, 65, 54, 58, 112, 216, 186, 194, 127, 8, 71, 67, 241, 39, 234, 225, 95, 227, 16), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 802, 'Hex High Entropy String', (0, 94, 106, 220, 105, 91, 82, 117, 61, 182, 84, 231, 169, 213, 44, 204, 5, 56, 106, 195), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1118, 'Hex High Entropy String', (114, 182, 241, 1, 61, 73, 185, 5, 136, 3, 86, 70, 96, 166, 147, 142, 146, 229, 60, 117), 'receipt_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1149, 'Hex High Entropy String', (53, 110, 155, 147, 173, 203, 248, 177, 132, 115, 219, 156, 170, 210, 86, 242, 93, 71, 210, 90), 'historical_head_observation'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1173, 'Hex High Entropy String', (11, 81, 41, 26, 199, 213, 127, 65, 60, 112, 19, 158, 128, 216, 65, 97, 121, 2, 103, 249), 'historical_head_observation'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1207, 'Hex High Entropy String', (137, 88, 165, 215, 209, 15, 109, 250, 139, 242, 198, 106, 203, 108, 241, 30, 108, 13, 162, 254), 'receipt_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1221, 'Hex High Entropy String', (255, 99, 49, 126, 208, 14, 252, 80, 159, 252, 90, 11, 194, 47, 159, 227, 222, 95, 95, 202), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1227, 'Hex High Entropy String', (143, 5, 223, 5, 60, 70, 111, 250, 68, 251, 117, 81, 7, 173, 189, 193, 98, 3, 231, 98), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1228, 'Hex High Entropy String', (60, 149, 245, 39, 120, 188, 27, 128, 3, 144, 130, 127, 185, 1, 84, 72, 225, 133, 37, 119), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1241, 'Hex High Entropy String', (184, 229, 146, 175, 224, 163, 4, 68, 173, 252, 14, 180, 173, 95, 160, 249, 217, 25, 22, 136), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1242, 'Hex High Entropy String', (195, 161, 20, 151, 178, 133, 25, 71, 85, 228, 62, 151, 120, 186, 138, 204, 113, 65, 196, 89), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1250, 'Hex High Entropy String', (208, 158, 162, 49, 87, 191, 185, 195, 73, 60, 120, 228, 77, 44, 72, 191, 153, 240, 164, 160), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1251, 'Hex High Entropy String', (117, 148, 58, 211, 37, 12, 208, 252, 200, 79, 98, 54, 127, 214, 196, 162, 254, 13, 73, 195), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1259, 'Hex High Entropy String', (253, 173, 214, 28, 151, 187, 174, 209, 173, 32, 184, 146, 166, 77, 178, 231, 91, 184, 212, 116), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1260, 'Hex High Entropy String', (230, 94, 170, 161, 216, 94, 81, 186, 169, 9, 51, 210, 87, 119, 202, 79, 129, 66, 206, 160), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1285, 'Hex High Entropy String', (170, 205, 157, 186, 193, 192, 87, 149, 70, 253, 245, 140, 23, 192, 137, 87, 253, 40, 27, 32), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1286, 'Hex High Entropy String', (174, 190, 239, 32, 16, 202, 85, 28, 11, 96, 68, 76, 15, 57, 42, 55, 104, 27, 214, 181), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1307, 'Hex High Entropy String', (153, 168, 137, 78, 232, 193, 26, 147, 148, 127, 11, 165, 17, 24, 158, 162, 82, 221, 206, 237), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1308, 'Hex High Entropy String', (48, 149, 145, 236, 182, 90, 26, 218, 194, 159, 203, 24, 216, 172, 188, 219, 53, 81, 15, 236), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1337, 'Hex High Entropy String', (55, 181, 143, 101, 17, 121, 48, 165, 199, 81, 117, 199, 103, 114, 78, 119, 25, 183, 95, 181), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1343, 'Hex High Entropy String', (208, 232, 2, 154, 108, 111, 211, 236, 36, 172, 168, 149, 11, 254, 205, 125, 161, 244, 113, 241), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1344, 'Hex High Entropy String', (19, 159, 250, 14, 242, 148, 105, 129, 181, 164, 99, 231, 116, 33, 84, 202, 255, 114, 227, 172), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1357, 'Hex High Entropy String', (151, 20, 149, 152, 91, 199, 189, 209, 37, 37, 146, 228, 52, 241, 74, 67, 179, 86, 161, 247), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1358, 'Hex High Entropy String', (216, 104, 186, 32, 214, 40, 190, 46, 22, 72, 57, 84, 82, 43, 157, 223, 163, 119, 165, 189), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1366, 'Hex High Entropy String', (194, 119, 184, 180, 39, 168, 236, 230, 151, 224, 121, 182, 236, 129, 212, 178, 80, 230, 139, 16), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1367, 'Hex High Entropy String', (58, 62, 111, 228, 46, 186, 215, 0, 215, 30, 225, 43, 148, 205, 33, 7, 201, 223, 233, 116), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1384, 'Hex High Entropy String', (45, 156, 142, 57, 217, 74, 226, 141, 35, 209, 117, 3, 98, 127, 140, 170, 174, 44, 226, 95), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1385, 'Hex High Entropy String', (196, 64, 98, 205, 27, 38, 158, 169, 116, 247, 168, 112, 186, 61, 83, 50, 172, 40, 105, 178), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1410, 'Hex High Entropy String', (203, 69, 88, 196, 75, 46, 21, 5, 164, 174, 116, 102, 196, 147, 214, 226, 133, 106, 0, 150), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1411, 'Hex High Entropy String', (230, 93, 56, 34, 104, 211, 178, 172, 37, 43, 75, 242, 213, 253, 67, 219, 140, 107, 20, 240), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1424, 'Hex High Entropy String', (98, 112, 158, 168, 60, 154, 89, 1, 98, 68, 158, 196, 192, 44, 144, 228, 62, 141, 15, 82), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1425, 'Hex High Entropy String', (155, 119, 101, 36, 182, 154, 39, 200, 34, 239, 186, 144, 72, 216, 94, 238, 161, 68, 225, 219), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1478, 'Hex High Entropy String', (225, 118, 143, 206, 76, 152, 120, 14, 213, 73, 55, 94, 110, 135, 148, 111, 192, 168, 199, 141), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/intake-receipt.json', 1515, 'Hex High Entropy String', (255, 52, 141, 216, 156, 20, 44, 144, 115, 153, 206, 149, 181, 103, 154, 39, 137, 128, 232, 233), 'manifest_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/manifest-snapshot.json', 259, 'Hex High Entropy String', (17, 217, 77, 43, 14, 33, 27, 229, 111, 224, 110, 130, 70, 141, 191, 15, 24, 84, 236, 31), 'head_observation'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/manifest-snapshot.json', 276, 'Hex High Entropy String', (5, 246, 149, 251, 209, 231, 66, 207, 229, 38, 71, 245, 183, 3, 31, 243, 161, 118, 35, 19), 'head_observation'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/manifest-snapshot.json', 312, 'Hex High Entropy String', (53, 110, 155, 147, 173, 203, 248, 177, 132, 115, 219, 156, 170, 210, 86, 242, 93, 71, 210, 90), 'head_observation'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/manifest-snapshot.json', 330, 'Hex High Entropy String', (114, 187, 144, 88, 169, 252, 173, 43, 67, 238, 103, 54, 218, 215, 128, 153, 172, 193, 195, 170), 'head_observation'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/manifest-snapshot.json', 348, 'Hex High Entropy String', (133, 161, 133, 205, 195, 204, 20, 9, 216, 82, 33, 127, 51, 158, 135, 63, 74, 50, 153, 238), 'head_observation'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/manifest-snapshot.json', 678, 'Hex High Entropy String', (11, 81, 41, 26, 199, 213, 127, 65, 60, 112, 19, 158, 128, 216, 65, 97, 121, 2, 103, 249), 'head_observation'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 5, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'canonical_base_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 9, 'Hex High Entropy String', (149, 56, 48, 73, 115, 230, 189, 0, 111, 165, 10, 61, 20, 244, 87, 148, 42, 52, 253, 69), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 10, 'Hex High Entropy String', (32, 177, 4, 55, 245, 249, 37, 39, 116, 254, 25, 55, 53, 69, 224, 61, 105, 86, 193, 118), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 17, 'Hex High Entropy String', (129, 163, 178, 150, 94, 94, 92, 114, 50, 2, 88, 244, 43, 139, 220, 83, 217, 238, 120, 116), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 19, 'Hex High Entropy String', (44, 124, 73, 254, 162, 44, 226, 0, 156, 27, 4, 123, 247, 248, 145, 99, 124, 175, 46, 162), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 26, 'Hex High Entropy String', (113, 216, 115, 8, 190, 165, 228, 118, 95, 3, 151, 118, 55, 9, 192, 225, 175, 16, 198, 187), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 28, 'Hex High Entropy String', (128, 35, 253, 17, 22, 179, 174, 15, 224, 3, 149, 200, 205, 36, 106, 178, 20, 97, 23, 52), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 35, 'Hex High Entropy String', (33, 54, 99, 160, 242, 94, 91, 95, 242, 104, 155, 53, 160, 50, 92, 254, 118, 92, 237, 159), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 37, 'Hex High Entropy String', (85, 131, 115, 38, 93, 52, 195, 165, 71, 143, 53, 24, 162, 233, 234, 184, 87, 140, 154, 204), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 44, 'Hex High Entropy String', (62, 58, 169, 211, 179, 212, 160, 244, 44, 94, 107, 152, 135, 242, 107, 96, 55, 21, 17, 247), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 46, 'Hex High Entropy String', (191, 24, 114, 165, 40, 194, 23, 105, 53, 30, 180, 180, 223, 240, 98, 76, 169, 158, 224, 28), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 53, 'Hex High Entropy String', (49, 98, 169, 76, 147, 51, 76, 153, 163, 143, 104, 129, 140, 220, 45, 108, 89, 15, 14, 76), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 55, 'Hex High Entropy String', (135, 174, 101, 142, 119, 41, 21, 63, 114, 18, 53, 93, 147, 225, 95, 1, 34, 218, 201, 109), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 62, 'Hex High Entropy String', (254, 107, 53, 65, 199, 104, 35, 86, 173, 7, 211, 111, 235, 170, 167, 178, 168, 215, 68, 77), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 64, 'Hex High Entropy String', (217, 53, 171, 14, 17, 96, 219, 109, 19, 40, 4, 16, 18, 28, 75, 232, 5, 32, 34, 48), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 71, 'Hex High Entropy String', (182, 128, 69, 219, 14, 33, 195, 182, 248, 51, 128, 163, 159, 201, 243, 142, 202, 77, 128, 19), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 73, 'Hex High Entropy String', (30, 76, 120, 90, 154, 90, 245, 91, 157, 34, 50, 239, 234, 178, 249, 151, 54, 71, 192, 186), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 80, 'Hex High Entropy String', (74, 36, 130, 76, 94, 207, 106, 99, 87, 59, 106, 181, 178, 183, 80, 25, 226, 233, 28, 16), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 82, 'Hex High Entropy String', (85, 19, 63, 79, 202, 1, 106, 115, 155, 95, 11, 70, 229, 41, 128, 9, 147, 171, 175, 33), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 89, 'Hex High Entropy String', (84, 160, 65, 54, 58, 112, 216, 186, 194, 127, 8, 71, 67, 241, 39, 234, 225, 95, 227, 16), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 91, 'Hex High Entropy String', (0, 94, 106, 220, 105, 91, 82, 117, 61, 182, 84, 231, 169, 213, 44, 204, 5, 56, 106, 195), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/intake-receipt.json', 375, 'Hex High Entropy String', (84, 155, 213, 28, 63, 69, 196, 129, 214, 203, 75, 137, 141, 51, 3, 157, 78, 149, 157, 34), 'manifest_digest'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 9, 'Hex High Entropy String', (149, 56, 48, 73, 115, 230, 189, 0, 111, 165, 10, 61, 20, 244, 87, 148, 42, 52, 253, 69), 'revision'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 13, 'Hex High Entropy String', (129, 163, 178, 150, 94, 94, 92, 114, 50, 2, 88, 244, 43, 139, 220, 83, 217, 238, 120, 116), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 15, 'Hex High Entropy String', (44, 124, 73, 254, 162, 44, 226, 0, 156, 27, 4, 123, 247, 248, 145, 99, 124, 175, 46, 162), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 22, 'Hex High Entropy String', (113, 216, 115, 8, 190, 165, 228, 118, 95, 3, 151, 118, 55, 9, 192, 225, 175, 16, 198, 187), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 24, 'Hex High Entropy String', (128, 35, 253, 17, 22, 179, 174, 15, 224, 3, 149, 200, 205, 36, 106, 178, 20, 97, 23, 52), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 31, 'Hex High Entropy String', (33, 54, 99, 160, 242, 94, 91, 95, 242, 104, 155, 53, 160, 50, 92, 254, 118, 92, 237, 159), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 33, 'Hex High Entropy String', (85, 131, 115, 38, 93, 52, 195, 165, 71, 143, 53, 24, 162, 233, 234, 184, 87, 140, 154, 204), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 40, 'Hex High Entropy String', (62, 58, 169, 211, 179, 212, 160, 244, 44, 94, 107, 152, 135, 242, 107, 96, 55, 21, 17, 247), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 42, 'Hex High Entropy String', (191, 24, 114, 165, 40, 194, 23, 105, 53, 30, 180, 180, 223, 240, 98, 76, 169, 158, 224, 28), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 49, 'Hex High Entropy String', (49, 98, 169, 76, 147, 51, 76, 153, 163, 143, 104, 129, 140, 220, 45, 108, 89, 15, 14, 76), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 51, 'Hex High Entropy String', (135, 174, 101, 142, 119, 41, 21, 63, 114, 18, 53, 93, 147, 225, 95, 1, 34, 218, 201, 109), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 58, 'Hex High Entropy String', (254, 107, 53, 65, 199, 104, 35, 86, 173, 7, 211, 111, 235, 170, 167, 178, 168, 215, 68, 77), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 60, 'Hex High Entropy String', (217, 53, 171, 14, 17, 96, 219, 109, 19, 40, 4, 16, 18, 28, 75, 232, 5, 32, 34, 48), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 67, 'Hex High Entropy String', (182, 128, 69, 219, 14, 33, 195, 182, 248, 51, 128, 163, 159, 201, 243, 142, 202, 77, 128, 19), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 69, 'Hex High Entropy String', (30, 76, 120, 90, 154, 90, 245, 91, 157, 34, 50, 239, 234, 178, 249, 151, 54, 71, 192, 186), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 76, 'Hex High Entropy String', (74, 36, 130, 76, 94, 207, 106, 99, 87, 59, 106, 181, 178, 183, 80, 25, 226, 233, 28, 16), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 78, 'Hex High Entropy String', (85, 19, 63, 79, 202, 1, 106, 115, 155, 95, 11, 70, 229, 41, 128, 9, 147, 171, 175, 33), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 85, 'Hex High Entropy String', (84, 160, 65, 54, 58, 112, 216, 186, 194, 127, 8, 71, 67, 241, 39, 234, 225, 95, 227, 16), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/ruflo/skill-candidates.json', 87, 'Hex High Entropy String', (0, 94, 106, 220, 105, 91, 82, 117, 61, 182, 84, 231, 169, 213, 44, 204, 5, 56, 106, 195), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 13, 'Hex High Entropy String', (17, 217, 77, 43, 14, 33, 27, 229, 111, 224, 110, 130, 70, 141, 191, 15, 24, 84, 236, 31), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 14, 'Hex High Entropy String', (158, 29, 38, 4, 146, 78, 45, 9, 175, 89, 12, 46, 196, 127, 135, 76, 2, 238, 107, 180), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 15, 'Hex High Entropy String', (213, 112, 155, 87, 136, 24, 44, 179, 101, 15, 62, 146, 252, 155, 104, 97, 100, 199, 87, 113), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 26, 'Hex High Entropy String', (255, 34, 237, 67, 47, 113, 76, 152, 217, 204, 231, 113, 214, 140, 100, 98, 98, 171, 163, 26), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 27, 'Hex High Entropy String', (126, 144, 222, 141, 50, 159, 7, 83, 183, 221, 6, 128, 44, 123, 180, 40, 77, 235, 103, 168), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 76, 'Hex High Entropy String', (5, 246, 149, 251, 209, 231, 66, 207, 229, 38, 71, 245, 183, 3, 31, 243, 161, 118, 35, 19), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 77, 'Hex High Entropy String', (177, 219, 127, 14, 229, 160, 55, 159, 238, 199, 149, 186, 177, 76, 67, 55, 69, 210, 142, 155), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 78, 'Hex High Entropy String', (8, 183, 173, 204, 184, 117, 212, 181, 108, 72, 166, 73, 215, 255, 181, 218, 21, 63, 217, 190), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 89, 'Hex High Entropy String', (182, 130, 176, 131, 55, 4, 244, 76, 212, 81, 235, 8, 117, 78, 17, 44, 45, 4, 43, 188), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 90, 'Hex High Entropy String', (231, 213, 136, 148, 74, 148, 4, 207, 50, 92, 0, 14, 228, 72, 21, 147, 202, 1, 104, 195), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 137, 'Hex High Entropy String', (114, 187, 144, 88, 169, 252, 173, 43, 67, 238, 103, 54, 218, 215, 128, 153, 172, 193, 195, 170), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 138, 'Hex High Entropy String', (227, 143, 91, 21, 154, 163, 36, 133, 138, 80, 247, 75, 179, 134, 106, 85, 68, 189, 234, 80), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 142, 'Hex High Entropy String', (42, 196, 30, 169, 129, 140, 170, 100, 131, 185, 231, 96, 43, 15, 54, 33, 158, 88, 243, 233), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 143, 'Hex High Entropy String', (5, 51, 215, 83, 148, 244, 22, 180, 92, 1, 48, 21, 145, 13, 226, 167, 252, 114, 143, 92), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 151, 'Hex High Entropy String', (193, 210, 65, 8, 157, 72, 55, 62, 141, 11, 119, 28, 174, 171, 222, 110, 158, 190, 11, 31), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 152, 'Hex High Entropy String', (191, 163, 154, 118, 174, 38, 39, 116, 228, 196, 68, 161, 154, 73, 226, 103, 154, 72, 152, 45), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 160, 'Hex High Entropy String', (80, 212, 208, 1, 2, 129, 152, 139, 108, 248, 146, 36, 127, 44, 69, 36, 150, 159, 79, 221), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 161, 'Hex High Entropy String', (180, 101, 120, 47, 238, 205, 87, 139, 60, 45, 136, 251, 69, 145, 223, 69, 32, 75, 156, 255), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 169, 'Hex High Entropy String', (166, 6, 173, 241, 239, 234, 48, 159, 92, 205, 188, 164, 139, 138, 89, 240, 105, 58, 211, 154), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 170, 'Hex High Entropy String', (118, 178, 123, 174, 6, 65, 187, 116, 136, 139, 246, 2, 229, 232, 138, 249, 63, 242, 18, 213), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 178, 'Hex High Entropy String', (117, 22, 176, 248, 188, 24, 83, 35, 108, 215, 122, 18, 129, 0, 169, 203, 176, 12, 12, 72), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 179, 'Hex High Entropy String', (182, 54, 231, 9, 100, 22, 21, 181, 116, 197, 254, 17, 212, 139, 180, 59, 210, 69, 166, 81), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 187, 'Hex High Entropy String', (65, 226, 20, 203, 49, 134, 177, 188, 104, 120, 125, 105, 175, 48, 97, 57, 170, 195, 200, 232), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 188, 'Hex High Entropy String', (24, 202, 137, 170, 95, 141, 43, 9, 95, 216, 51, 118, 254, 50, 142, 207, 140, 195, 17, 203), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 196, 'Hex High Entropy String', (159, 20, 60, 79, 244, 231, 161, 112, 104, 127, 23, 165, 1, 63, 222, 201, 74, 62, 54, 242), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 197, 'Hex High Entropy String', (214, 5, 110, 56, 73, 222, 112, 239, 70, 167, 79, 31, 121, 86, 77, 72, 144, 18, 39, 204), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 205, 'Hex High Entropy String', (170, 110, 11, 202, 206, 128, 100, 69, 79, 216, 187, 117, 108, 96, 64, 233, 154, 124, 19, 116), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 206, 'Hex High Entropy String', (218, 208, 42, 81, 39, 28, 236, 208, 159, 142, 2, 36, 203, 35, 217, 233, 130, 232, 83, 233), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 255, 'Hex High Entropy String', (133, 161, 133, 205, 195, 204, 20, 9, 216, 82, 33, 127, 51, 158, 135, 63, 74, 50, 153, 238), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 256, 'Hex High Entropy String', (57, 172, 6, 243, 145, 16, 36, 205, 203, 58, 233, 221, 91, 106, 152, 121, 15, 96, 119, 20), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 260, 'Hex High Entropy String', (87, 44, 201, 53, 193, 243, 97, 56, 166, 251, 133, 81, 64, 25, 1, 150, 165, 40, 187, 77), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 261, 'Hex High Entropy String', (195, 191, 8, 48, 16, 229, 196, 188, 58, 255, 1, 98, 210, 66, 66, 137, 126, 73, 7, 224), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 269, 'Hex High Entropy String', (146, 160, 12, 191, 126, 126, 226, 178, 81, 61, 190, 38, 75, 12, 120, 128, 105, 90, 126, 43), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 270, 'Hex High Entropy String', (83, 34, 205, 237, 223, 166, 51, 1, 188, 253, 91, 166, 198, 132, 226, 175, 183, 26, 13, 6), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 278, 'Hex High Entropy String', (160, 162, 162, 101, 98, 95, 43, 85, 95, 113, 224, 195, 155, 17, 203, 230, 223, 178, 186, 72), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 279, 'Hex High Entropy String', (92, 43, 104, 105, 234, 44, 184, 167, 89, 92, 136, 248, 18, 206, 148, 56, 228, 16, 216, 39), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 287, 'Hex High Entropy String', (212, 18, 68, 134, 13, 83, 91, 138, 26, 7, 161, 96, 177, 54, 174, 136, 252, 154, 141, 113), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 288, 'Hex High Entropy String', (138, 222, 136, 73, 24, 61, 127, 41, 210, 138, 193, 130, 251, 154, 29, 140, 108, 71, 110, 82), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 296, 'Hex High Entropy String', (233, 26, 27, 103, 96, 108, 181, 92, 180, 10, 148, 126, 197, 160, 238, 88, 159, 121, 166, 200), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 297, 'Hex High Entropy String', (160, 207, 58, 40, 246, 87, 25, 90, 144, 81, 108, 212, 165, 116, 176, 50, 200, 140, 249, 72), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 305, 'Hex High Entropy String', (108, 83, 102, 68, 244, 167, 223, 82, 165, 95, 222, 194, 4, 38, 249, 160, 31, 143, 166, 39), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 306, 'Hex High Entropy String', (103, 7, 210, 196, 218, 126, 117, 151, 242, 233, 106, 31, 23, 203, 62, 142, 113, 183, 193, 180), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 353, 'Hex High Entropy String', (149, 56, 48, 73, 115, 230, 189, 0, 111, 165, 10, 61, 20, 244, 87, 148, 42, 52, 253, 69), 'revision'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 357, 'Hex High Entropy String', (129, 163, 178, 150, 94, 94, 92, 114, 50, 2, 88, 244, 43, 139, 220, 83, 217, 238, 120, 116), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 359, 'Hex High Entropy String', (44, 124, 73, 254, 162, 44, 226, 0, 156, 27, 4, 123, 247, 248, 145, 99, 124, 175, 46, 162), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 366, 'Hex High Entropy String', (113, 216, 115, 8, 190, 165, 228, 118, 95, 3, 151, 118, 55, 9, 192, 225, 175, 16, 198, 187), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 368, 'Hex High Entropy String', (128, 35, 253, 17, 22, 179, 174, 15, 224, 3, 149, 200, 205, 36, 106, 178, 20, 97, 23, 52), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 375, 'Hex High Entropy String', (33, 54, 99, 160, 242, 94, 91, 95, 242, 104, 155, 53, 160, 50, 92, 254, 118, 92, 237, 159), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 377, 'Hex High Entropy String', (85, 131, 115, 38, 93, 52, 195, 165, 71, 143, 53, 24, 162, 233, 234, 184, 87, 140, 154, 204), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 384, 'Hex High Entropy String', (62, 58, 169, 211, 179, 212, 160, 244, 44, 94, 107, 152, 135, 242, 107, 96, 55, 21, 17, 247), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 386, 'Hex High Entropy String', (191, 24, 114, 165, 40, 194, 23, 105, 53, 30, 180, 180, 223, 240, 98, 76, 169, 158, 224, 28), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 393, 'Hex High Entropy String', (49, 98, 169, 76, 147, 51, 76, 153, 163, 143, 104, 129, 140, 220, 45, 108, 89, 15, 14, 76), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 395, 'Hex High Entropy String', (135, 174, 101, 142, 119, 41, 21, 63, 114, 18, 53, 93, 147, 225, 95, 1, 34, 218, 201, 109), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 402, 'Hex High Entropy String', (254, 107, 53, 65, 199, 104, 35, 86, 173, 7, 211, 111, 235, 170, 167, 178, 168, 215, 68, 77), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 404, 'Hex High Entropy String', (217, 53, 171, 14, 17, 96, 219, 109, 19, 40, 4, 16, 18, 28, 75, 232, 5, 32, 34, 48), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 411, 'Hex High Entropy String', (182, 128, 69, 219, 14, 33, 195, 182, 248, 51, 128, 163, 159, 201, 243, 142, 202, 77, 128, 19), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 413, 'Hex High Entropy String', (30, 76, 120, 90, 154, 90, 245, 91, 157, 34, 50, 239, 234, 178, 249, 151, 54, 71, 192, 186), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 420, 'Hex High Entropy String', (74, 36, 130, 76, 94, 207, 106, 99, 87, 59, 106, 181, 178, 183, 80, 25, 226, 233, 28, 16), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 422, 'Hex High Entropy String', (85, 19, 63, 79, 202, 1, 106, 115, 155, 95, 11, 70, 229, 41, 128, 9, 147, 171, 175, 33), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 429, 'Hex High Entropy String', (84, 160, 65, 54, 58, 112, 216, 186, 194, 127, 8, 71, 67, 241, 39, 234, 225, 95, 227, 16), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 431, 'Hex High Entropy String', (0, 94, 106, 220, 105, 91, 82, 117, 61, 182, 84, 231, 169, 213, 44, 204, 5, 56, 106, 195), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 482, 'Hex High Entropy String', (53, 110, 155, 147, 173, 203, 248, 177, 132, 115, 219, 156, 170, 210, 86, 242, 93, 71, 210, 90), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 483, 'Hex High Entropy String', (255, 99, 49, 126, 208, 14, 252, 80, 159, 252, 90, 11, 194, 47, 159, 227, 222, 95, 95, 202), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 489, 'Hex High Entropy String', (143, 5, 223, 5, 60, 70, 111, 250, 68, 251, 117, 81, 7, 173, 189, 193, 98, 3, 231, 98), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 490, 'Hex High Entropy String', (60, 149, 245, 39, 120, 188, 27, 128, 3, 144, 130, 127, 185, 1, 84, 72, 225, 133, 37, 119), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 503, 'Hex High Entropy String', (253, 173, 214, 28, 151, 187, 174, 209, 173, 32, 184, 146, 166, 77, 178, 231, 91, 184, 212, 116), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 504, 'Hex High Entropy String', (230, 94, 170, 161, 216, 94, 81, 186, 169, 9, 51, 210, 87, 119, 202, 79, 129, 66, 206, 160), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 529, 'Hex High Entropy String', (170, 205, 157, 186, 193, 192, 87, 149, 70, 253, 245, 140, 23, 192, 137, 87, 253, 40, 27, 32), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 530, 'Hex High Entropy String', (174, 190, 239, 32, 16, 202, 85, 28, 11, 96, 68, 76, 15, 57, 42, 55, 104, 27, 214, 181), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 551, 'Hex High Entropy String', (153, 168, 137, 78, 232, 193, 26, 147, 148, 127, 11, 165, 17, 24, 158, 162, 82, 221, 206, 237), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 552, 'Hex High Entropy String', (48, 149, 145, 236, 182, 90, 26, 218, 194, 159, 203, 24, 216, 172, 188, 219, 53, 81, 15, 236), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 586, 'Hex High Entropy String', (11, 81, 41, 26, 199, 213, 127, 65, 60, 112, 19, 158, 128, 216, 65, 97, 121, 2, 103, 249), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 587, 'Hex High Entropy String', (55, 181, 143, 101, 17, 121, 48, 165, 199, 81, 117, 199, 103, 114, 78, 119, 25, 183, 95, 181), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 593, 'Hex High Entropy String', (208, 232, 2, 154, 108, 111, 211, 236, 36, 172, 168, 149, 11, 254, 205, 125, 161, 244, 113, 241), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 594, 'Hex High Entropy String', (19, 159, 250, 14, 242, 148, 105, 129, 181, 164, 99, 231, 116, 33, 84, 202, 255, 114, 227, 172), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 607, 'Hex High Entropy String', (194, 119, 184, 180, 39, 168, 236, 230, 151, 224, 121, 182, 236, 129, 212, 178, 80, 230, 139, 16), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 608, 'Hex High Entropy String', (58, 62, 111, 228, 46, 186, 215, 0, 215, 30, 225, 43, 148, 205, 33, 7, 201, 223, 233, 116), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 625, 'Hex High Entropy String', (45, 156, 142, 57, 217, 74, 226, 141, 35, 209, 117, 3, 98, 127, 140, 170, 174, 44, 226, 95), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 626, 'Hex High Entropy String', (196, 64, 98, 205, 27, 38, 158, 169, 116, 247, 168, 112, 186, 61, 83, 50, 172, 40, 105, 178), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 651, 'Hex High Entropy String', (203, 69, 88, 196, 75, 46, 21, 5, 164, 174, 116, 102, 196, 147, 214, 226, 133, 106, 0, 150), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 652, 'Hex High Entropy String', (230, 93, 56, 34, 104, 211, 178, 172, 37, 43, 75, 242, 213, 253, 67, 219, 140, 107, 20, 240), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 665, 'Hex High Entropy String', (98, 112, 158, 168, 60, 154, 89, 1, 98, 68, 158, 196, 192, 44, 144, 228, 62, 141, 15, 82), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/skill-candidates.json', 666, 'Hex High Entropy String', (155, 119, 101, 36, 182, 154, 39, 200, 34, 239, 186, 144, 72, 216, 94, 238, 161, 68, 225, 219), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 4, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'canonical_base_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 6, 'Hex High Entropy String', (84, 155, 213, 28, 63, 69, 196, 129, 214, 203, 75, 137, 141, 51, 3, 157, 78, 149, 157, 34), 'manifest_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 24, 'Hex High Entropy String', (17, 217, 77, 43, 14, 33, 27, 229, 111, 224, 110, 130, 70, 141, 191, 15, 24, 84, 236, 31), 'commit'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 25, 'Hex High Entropy String', (204, 217, 21, 222, 150, 70, 202, 109, 119, 83, 116, 236, 85, 49, 30, 131, 179, 161, 190, 204), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 29, 'Hex High Entropy String', (186, 3, 133, 242, 182, 196, 214, 202, 186, 36, 183, 107, 12, 173, 94, 200, 219, 157, 35, 2), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 30, 'Hex High Entropy String', (169, 245, 128, 253, 86, 234, 187, 195, 20, 19, 173, 121, 136, 187, 55, 136, 155, 182, 119, 120), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 46, 'Hex High Entropy String', (12, 113, 235, 162, 53, 135, 157, 0, 9, 79, 105, 50, 36, 19, 43, 152, 239, 147, 236, 165), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 47, 'Hex High Entropy String', (137, 51, 132, 198, 153, 74, 112, 67, 164, 144, 78, 97, 244, 177, 247, 86, 207, 87, 119, 251), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 58, 'Hex High Entropy String', (18, 5, 154, 150, 142, 73, 51, 143, 105, 148, 196, 101, 34, 176, 136, 1, 237, 61, 76, 174), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 59, 'Hex High Entropy String', (146, 245, 195, 147, 252, 220, 208, 116, 92, 118, 0, 251, 250, 225, 143, 200, 41, 242, 188, 61), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 70, 'Hex High Entropy String', (112, 243, 169, 19, 108, 49, 38, 201, 178, 61, 213, 182, 111, 111, 121, 190, 149, 35, 134, 234), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 71, 'Hex High Entropy String', (98, 41, 161, 48, 142, 22, 170, 40, 142, 118, 87, 135, 161, 80, 186, 122, 223, 65, 116, 87), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 87, 'Hex High Entropy String', (158, 29, 38, 4, 146, 78, 45, 9, 175, 89, 12, 46, 196, 127, 135, 76, 2, 238, 107, 180), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 88, 'Hex High Entropy String', (213, 112, 155, 87, 136, 24, 44, 179, 101, 15, 62, 146, 252, 155, 104, 97, 100, 199, 87, 113), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 104, 'Hex High Entropy String', (255, 34, 237, 67, 47, 113, 76, 152, 217, 204, 231, 113, 214, 140, 100, 98, 98, 171, 163, 26), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 105, 'Hex High Entropy String', (126, 144, 222, 141, 50, 159, 7, 83, 183, 221, 6, 128, 44, 123, 180, 40, 77, 235, 103, 168), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 121, 'Hex High Entropy String', (250, 86, 215, 116, 134, 226, 131, 210, 17, 129, 97, 79, 184, 72, 243, 180, 177, 91, 85, 100), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 122, 'Hex High Entropy String', (119, 160, 175, 202, 90, 66, 65, 181, 198, 146, 245, 249, 215, 205, 141, 141, 49, 66, 191, 19), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 138, 'Hex High Entropy String', (202, 38, 9, 67, 13, 175, 93, 100, 223, 251, 224, 8, 188, 1, 185, 99, 79, 190, 105, 230), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 139, 'Hex High Entropy String', (190, 220, 73, 38, 37, 85, 149, 150, 128, 55, 75, 241, 240, 49, 8, 1, 30, 243, 12, 132), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 150, 'Hex High Entropy String', (98, 192, 200, 126, 58, 145, 222, 233, 255, 91, 173, 99, 177, 226, 82, 172, 164, 134, 251, 23), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 151, 'Hex High Entropy String', (203, 87, 118, 247, 62, 198, 29, 33, 96, 167, 250, 34, 17, 53, 117, 230, 110, 219, 180, 99), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 167, 'Hex High Entropy String', (47, 201, 159, 123, 105, 213, 234, 26, 176, 121, 72, 50, 206, 231, 216, 93, 73, 127, 183, 9), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 168, 'Hex High Entropy String', (56, 189, 98, 144, 73, 77, 206, 3, 191, 188, 132, 59, 242, 119, 100, 37, 243, 32, 106, 122), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 184, 'Hex High Entropy String', (165, 235, 2, 107, 116, 202, 202, 26, 89, 97, 76, 181, 104, 64, 122, 76, 187, 106, 235, 190), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 185, 'Hex High Entropy String', (64, 120, 31, 28, 24, 74, 58, 248, 93, 134, 223, 97, 3, 192, 90, 1, 161, 255, 255, 117), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 223, 'Hex High Entropy String', (5, 246, 149, 251, 209, 231, 66, 207, 229, 38, 71, 245, 183, 3, 31, 243, 161, 118, 35, 19), 'commit'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 224, 'Hex High Entropy String', (139, 157, 74, 160, 77, 129, 112, 92, 230, 124, 63, 136, 106, 101, 117, 206, 42, 160, 39, 199), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 228, 'Hex High Entropy String', (115, 27, 125, 152, 49, 62, 162, 248, 212, 227, 235, 181, 69, 102, 234, 59, 8, 61, 198, 222), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 229, 'Hex High Entropy String', (225, 80, 246, 213, 90, 21, 246, 55, 31, 218, 0, 49, 31, 241, 8, 140, 91, 3, 218, 137), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 245, 'Hex High Entropy String', (96, 138, 169, 118, 144, 128, 26, 206, 205, 79, 114, 91, 219, 37, 96, 188, 243, 4, 171, 229), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 246, 'Hex High Entropy String', (74, 51, 174, 183, 85, 50, 254, 182, 177, 119, 251, 111, 146, 152, 147, 67, 3, 21, 161, 32), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 257, 'Hex High Entropy String', (44, 194, 122, 96, 26, 203, 253, 89, 108, 23, 15, 73, 97, 156, 211, 224, 32, 159, 213, 96), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 258, 'Hex High Entropy String', (91, 181, 212, 55, 70, 73, 191, 135, 197, 124, 165, 127, 53, 69, 210, 26, 19, 91, 4, 224), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 274, 'Hex High Entropy String', (133, 189, 186, 184, 87, 123, 215, 75, 63, 26, 104, 77, 20, 94, 20, 127, 1, 29, 162, 173), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 275, 'Hex High Entropy String', (86, 144, 44, 115, 167, 138, 5, 48, 7, 151, 197, 240, 254, 65, 81, 36, 137, 90, 157, 221), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 291, 'Hex High Entropy String', (248, 209, 19, 131, 39, 236, 12, 68, 246, 238, 33, 234, 2, 39, 45, 142, 234, 211, 163, 234), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 292, 'Hex High Entropy String', (64, 238, 10, 92, 138, 61, 40, 70, 61, 174, 159, 16, 54, 144, 146, 253, 134, 125, 252, 90), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 308, 'Hex High Entropy String', (177, 219, 127, 14, 229, 160, 55, 159, 238, 199, 149, 186, 177, 76, 67, 55, 69, 210, 142, 155), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 309, 'Hex High Entropy String', (8, 183, 173, 204, 184, 117, 212, 181, 108, 72, 166, 73, 215, 255, 181, 218, 21, 63, 217, 190), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 325, 'Hex High Entropy String', (182, 130, 176, 131, 55, 4, 244, 76, 212, 81, 235, 8, 117, 78, 17, 44, 45, 4, 43, 188), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 326, 'Hex High Entropy String', (231, 213, 136, 148, 74, 148, 4, 207, 50, 92, 0, 14, 228, 72, 21, 147, 202, 1, 104, 195), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 342, 'Hex High Entropy String', (29, 53, 81, 29, 31, 160, 125, 154, 215, 124, 51, 151, 64, 173, 206, 131, 167, 99, 171, 28), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 343, 'Hex High Entropy String', (116, 229, 170, 176, 22, 195, 51, 146, 154, 34, 87, 112, 17, 42, 118, 188, 106, 48, 133, 131), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 359, 'Hex High Entropy String', (223, 213, 219, 5, 104, 40, 123, 217, 1, 130, 153, 91, 148, 242, 212, 118, 253, 88, 60, 234), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 360, 'Hex High Entropy String', (220, 55, 118, 126, 125, 241, 40, 104, 139, 228, 162, 104, 99, 196, 52, 122, 98, 135, 173, 217), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 376, 'Hex High Entropy String', (94, 69, 104, 143, 181, 130, 181, 84, 233, 127, 96, 53, 75, 199, 236, 93, 96, 60, 204, 14), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 377, 'Hex High Entropy String', (219, 154, 221, 172, 26, 62, 98, 198, 197, 157, 200, 191, 20, 150, 157, 96, 224, 170, 189, 129), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 393, 'Hex High Entropy String', (110, 205, 250, 39, 150, 22, 30, 182, 64, 222, 245, 54, 108, 124, 81, 203, 232, 188, 61, 31), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/intake-receipt.json', 394, 'Hex High Entropy String', (71, 190, 78, 139, 194, 211, 201, 180, 167, 2, 81, 117, 150, 76, 231, 50, 17, 55, 78, 244), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/skill-candidates.json', 13, 'Hex High Entropy String', (17, 217, 77, 43, 14, 33, 27, 229, 111, 224, 110, 130, 70, 141, 191, 15, 24, 84, 236, 31), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/skill-candidates.json', 14, 'Hex High Entropy String', (158, 29, 38, 4, 146, 78, 45, 9, 175, 89, 12, 46, 196, 127, 135, 76, 2, 238, 107, 180), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/skill-candidates.json', 15, 'Hex High Entropy String', (213, 112, 155, 87, 136, 24, 44, 179, 101, 15, 62, 146, 252, 155, 104, 97, 100, 199, 87, 113), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/skill-candidates.json', 26, 'Hex High Entropy String', (255, 34, 237, 67, 47, 113, 76, 152, 217, 204, 231, 113, 214, 140, 100, 98, 98, 171, 163, 26), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/skill-candidates.json', 27, 'Hex High Entropy String', (126, 144, 222, 141, 50, 159, 7, 83, 183, 221, 6, 128, 44, 123, 180, 40, 77, 235, 103, 168), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/skill-candidates.json', 76, 'Hex High Entropy String', (5, 246, 149, 251, 209, 231, 66, 207, 229, 38, 71, 245, 183, 3, 31, 243, 161, 118, 35, 19), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/skill-candidates.json', 77, 'Hex High Entropy String', (177, 219, 127, 14, 229, 160, 55, 159, 238, 199, 149, 186, 177, 76, 67, 55, 69, 210, 142, 155), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/skill-candidates.json', 78, 'Hex High Entropy String', (8, 183, 173, 204, 184, 117, 212, 181, 108, 72, 166, 73, 215, 255, 181, 218, 21, 63, 217, 190), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/skill-candidates.json', 89, 'Hex High Entropy String', (182, 130, 176, 131, 55, 4, 244, 76, 212, 81, 235, 8, 117, 78, 17, 44, 45, 4, 43, 188), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/typed/skill-candidates.json', 90, 'Hex High Entropy String', (231, 213, 136, 148, 74, 148, 4, 207, 50, 92, 0, 14, 228, 72, 21, 147, 202, 1, 104, 195), 'content_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 5, 'Hex High Entropy String', (22, 241, 53, 14, 213, 122, 178, 172, 135, 176, 226, 126, 69, 153, 118, 83, 192, 143, 28, 68), 'canonical_base_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 7, 'Hex High Entropy String', (84, 155, 213, 28, 63, 69, 196, 129, 214, 203, 75, 137, 141, 51, 3, 157, 78, 149, 157, 34), 'manifest_sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 23, 'Hex High Entropy String', (114, 187, 144, 88, 169, 252, 173, 43, 67, 238, 103, 54, 218, 215, 128, 153, 172, 193, 195, 170), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 24, 'Hex High Entropy String', (227, 143, 91, 21, 154, 163, 36, 133, 138, 80, 247, 75, 179, 134, 106, 85, 68, 189, 234, 80), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 29, 'Hex High Entropy String', (42, 196, 30, 169, 129, 140, 170, 100, 131, 185, 231, 96, 43, 15, 54, 33, 158, 88, 243, 233), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 30, 'Hex High Entropy String', (5, 51, 215, 83, 148, 244, 22, 180, 92, 1, 48, 21, 145, 13, 226, 167, 252, 114, 143, 92), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 38, 'Hex High Entropy String', (193, 210, 65, 8, 157, 72, 55, 62, 141, 11, 119, 28, 174, 171, 222, 110, 158, 190, 11, 31), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 39, 'Hex High Entropy String', (191, 163, 154, 118, 174, 38, 39, 116, 228, 196, 68, 161, 154, 73, 226, 103, 154, 72, 152, 45), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 47, 'Hex High Entropy String', (80, 212, 208, 1, 2, 129, 152, 139, 108, 248, 146, 36, 127, 44, 69, 36, 150, 159, 79, 221), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 48, 'Hex High Entropy String', (180, 101, 120, 47, 238, 205, 87, 139, 60, 45, 136, 251, 69, 145, 223, 69, 32, 75, 156, 255), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 56, 'Hex High Entropy String', (166, 6, 173, 241, 239, 234, 48, 159, 92, 205, 188, 164, 139, 138, 89, 240, 105, 58, 211, 154), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 57, 'Hex High Entropy String', (118, 178, 123, 174, 6, 65, 187, 116, 136, 139, 246, 2, 229, 232, 138, 249, 63, 242, 18, 213), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 65, 'Hex High Entropy String', (117, 22, 176, 248, 188, 24, 83, 35, 108, 215, 122, 18, 129, 0, 169, 203, 176, 12, 12, 72), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 66, 'Hex High Entropy String', (182, 54, 231, 9, 100, 22, 21, 181, 116, 197, 254, 17, 212, 139, 180, 59, 210, 69, 166, 81), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 74, 'Hex High Entropy String', (65, 226, 20, 203, 49, 134, 177, 188, 104, 120, 125, 105, 175, 48, 97, 57, 170, 195, 200, 232), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 75, 'Hex High Entropy String', (24, 202, 137, 170, 95, 141, 43, 9, 95, 216, 51, 118, 254, 50, 142, 207, 140, 195, 17, 203), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 83, 'Hex High Entropy String', (159, 20, 60, 79, 244, 231, 161, 112, 104, 127, 23, 165, 1, 63, 222, 201, 74, 62, 54, 242), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 84, 'Hex High Entropy String', (214, 5, 110, 56, 73, 222, 112, 239, 70, 167, 79, 31, 121, 86, 77, 72, 144, 18, 39, 204), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 92, 'Hex High Entropy String', (170, 110, 11, 202, 206, 128, 100, 69, 79, 216, 187, 117, 108, 96, 64, 233, 154, 124, 19, 116), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 93, 'Hex High Entropy String', (218, 208, 42, 81, 39, 28, 236, 208, 159, 142, 2, 36, 203, 35, 217, 233, 130, 232, 83, 233), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 124, 'Hex High Entropy String', (133, 161, 133, 205, 195, 204, 20, 9, 216, 82, 33, 127, 51, 158, 135, 63, 74, 50, 153, 238), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 125, 'Hex High Entropy String', (57, 172, 6, 243, 145, 16, 36, 205, 203, 58, 233, 221, 91, 106, 152, 121, 15, 96, 119, 20), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 130, 'Hex High Entropy String', (87, 44, 201, 53, 193, 243, 97, 56, 166, 251, 133, 81, 64, 25, 1, 150, 165, 40, 187, 77), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 131, 'Hex High Entropy String', (195, 191, 8, 48, 16, 229, 196, 188, 58, 255, 1, 98, 210, 66, 66, 137, 126, 73, 7, 224), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 139, 'Hex High Entropy String', (146, 160, 12, 191, 126, 126, 226, 178, 81, 61, 190, 38, 75, 12, 120, 128, 105, 90, 126, 43), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 140, 'Hex High Entropy String', (83, 34, 205, 237, 223, 166, 51, 1, 188, 253, 91, 166, 198, 132, 226, 175, 183, 26, 13, 6), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 148, 'Hex High Entropy String', (160, 162, 162, 101, 98, 95, 43, 85, 95, 113, 224, 195, 155, 17, 203, 230, 223, 178, 186, 72), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 149, 'Hex High Entropy String', (92, 43, 104, 105, 234, 44, 184, 167, 89, 92, 136, 248, 18, 206, 148, 56, 228, 16, 216, 39), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 157, 'Hex High Entropy String', (212, 18, 68, 134, 13, 83, 91, 138, 26, 7, 161, 96, 177, 54, 174, 136, 252, 154, 141, 113), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 158, 'Hex High Entropy String', (138, 222, 136, 73, 24, 61, 127, 41, 210, 138, 193, 130, 251, 154, 29, 140, 108, 71, 110, 82), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 166, 'Hex High Entropy String', (233, 26, 27, 103, 96, 108, 181, 92, 180, 10, 148, 126, 197, 160, 238, 88, 159, 121, 166, 200), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 167, 'Hex High Entropy String', (160, 207, 58, 40, 246, 87, 25, 90, 144, 81, 108, 212, 165, 116, 176, 50, 200, 140, 249, 72), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 175, 'Hex High Entropy String', (108, 83, 102, 68, 244, 167, 223, 82, 165, 95, 222, 194, 4, 38, 249, 160, 31, 143, 166, 39), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/intake-receipt.json', 176, 'Hex High Entropy String', (103, 7, 210, 196, 218, 126, 117, 151, 242, 233, 106, 31, 23, 203, 62, 142, 113, 183, 193, 180), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 11, 'Hex High Entropy String', (114, 187, 144, 88, 169, 252, 173, 43, 67, 238, 103, 54, 218, 215, 128, 153, 172, 193, 195, 170), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 12, 'Hex High Entropy String', (227, 143, 91, 21, 154, 163, 36, 133, 138, 80, 247, 75, 179, 134, 106, 85, 68, 189, 234, 80), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 16, 'Hex High Entropy String', (42, 196, 30, 169, 129, 140, 170, 100, 131, 185, 231, 96, 43, 15, 54, 33, 158, 88, 243, 233), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 17, 'Hex High Entropy String', (5, 51, 215, 83, 148, 244, 22, 180, 92, 1, 48, 21, 145, 13, 226, 167, 252, 114, 143, 92), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 25, 'Hex High Entropy String', (193, 210, 65, 8, 157, 72, 55, 62, 141, 11, 119, 28, 174, 171, 222, 110, 158, 190, 11, 31), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 26, 'Hex High Entropy String', (191, 163, 154, 118, 174, 38, 39, 116, 228, 196, 68, 161, 154, 73, 226, 103, 154, 72, 152, 45), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 34, 'Hex High Entropy String', (80, 212, 208, 1, 2, 129, 152, 139, 108, 248, 146, 36, 127, 44, 69, 36, 150, 159, 79, 221), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 35, 'Hex High Entropy String', (180, 101, 120, 47, 238, 205, 87, 139, 60, 45, 136, 251, 69, 145, 223, 69, 32, 75, 156, 255), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 43, 'Hex High Entropy String', (166, 6, 173, 241, 239, 234, 48, 159, 92, 205, 188, 164, 139, 138, 89, 240, 105, 58, 211, 154), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 44, 'Hex High Entropy String', (118, 178, 123, 174, 6, 65, 187, 116, 136, 139, 246, 2, 229, 232, 138, 249, 63, 242, 18, 213), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 52, 'Hex High Entropy String', (117, 22, 176, 248, 188, 24, 83, 35, 108, 215, 122, 18, 129, 0, 169, 203, 176, 12, 12, 72), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 53, 'Hex High Entropy String', (182, 54, 231, 9, 100, 22, 21, 181, 116, 197, 254, 17, 212, 139, 180, 59, 210, 69, 166, 81), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 61, 'Hex High Entropy String', (65, 226, 20, 203, 49, 134, 177, 188, 104, 120, 125, 105, 175, 48, 97, 57, 170, 195, 200, 232), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 62, 'Hex High Entropy String', (24, 202, 137, 170, 95, 141, 43, 9, 95, 216, 51, 118, 254, 50, 142, 207, 140, 195, 17, 203), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 70, 'Hex High Entropy String', (159, 20, 60, 79, 244, 231, 161, 112, 104, 127, 23, 165, 1, 63, 222, 201, 74, 62, 54, 242), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 71, 'Hex High Entropy String', (214, 5, 110, 56, 73, 222, 112, 239, 70, 167, 79, 31, 121, 86, 77, 72, 144, 18, 39, 204), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 79, 'Hex High Entropy String', (170, 110, 11, 202, 206, 128, 100, 69, 79, 216, 187, 117, 108, 96, 64, 233, 154, 124, 19, 116), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 80, 'Hex High Entropy String', (218, 208, 42, 81, 39, 28, 236, 208, 159, 142, 2, 36, 203, 35, 217, 233, 130, 232, 83, 233), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 129, 'Hex High Entropy String', (133, 161, 133, 205, 195, 204, 20, 9, 216, 82, 33, 127, 51, 158, 135, 63, 74, 50, 153, 238), 'commit_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 130, 'Hex High Entropy String', (57, 172, 6, 243, 145, 16, 36, 205, 203, 58, 233, 221, 91, 106, 152, 121, 15, 96, 119, 20), 'tree_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 134, 'Hex High Entropy String', (87, 44, 201, 53, 193, 243, 97, 56, 166, 251, 133, 81, 64, 25, 1, 150, 165, 40, 187, 77), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 135, 'Hex High Entropy String', (195, 191, 8, 48, 16, 229, 196, 188, 58, 255, 1, 98, 210, 66, 66, 137, 126, 73, 7, 224), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 143, 'Hex High Entropy String', (146, 160, 12, 191, 126, 126, 226, 178, 81, 61, 190, 38, 75, 12, 120, 128, 105, 90, 126, 43), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 144, 'Hex High Entropy String', (83, 34, 205, 237, 223, 166, 51, 1, 188, 253, 91, 166, 198, 132, 226, 175, 183, 26, 13, 6), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 152, 'Hex High Entropy String', (160, 162, 162, 101, 98, 95, 43, 85, 95, 113, 224, 195, 155, 17, 203, 230, 223, 178, 186, 72), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 153, 'Hex High Entropy String', (92, 43, 104, 105, 234, 44, 184, 167, 89, 92, 136, 248, 18, 206, 148, 56, 228, 16, 216, 39), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 161, 'Hex High Entropy String', (212, 18, 68, 134, 13, 83, 91, 138, 26, 7, 161, 96, 177, 54, 174, 136, 252, 154, 141, 113), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 162, 'Hex High Entropy String', (138, 222, 136, 73, 24, 61, 127, 41, 210, 138, 193, 130, 251, 154, 29, 140, 108, 71, 110, 82), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 170, 'Hex High Entropy String', (233, 26, 27, 103, 96, 108, 181, 92, 180, 10, 148, 126, 197, 160, 238, 88, 159, 121, 166, 200), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 171, 'Hex High Entropy String', (160, 207, 58, 40, 246, 87, 25, 90, 144, 81, 108, 212, 165, 116, 176, 50, 200, 140, 249, 72), 'sha256'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 179, 'Hex High Entropy String', (108, 83, 102, 68, 244, 167, 223, 82, 165, 95, 222, 194, 4, 38, 249, 160, 31, 143, 166, 39), 'blob_sha'),
    ('docs/research/checkpoint-intake/CP1/20260930-cp1-1-initial/watch/skill-candidates.json', 180, 'Hex High Entropy String', (103, 7, 210, 196, 218, 126, 117, 151, 242, 233, 106, 31, 23, 203, 62, 142, 113, 183, 193, 180), 'sha256'),
    ('docs/verification/cp1.1-design-002-freeze-receipt.json', 4, 'Hex High Entropy String', (153, 123, 139, 254, 62, 31, 238, 60, 245, 30, 236, 50, 208, 188, 98, 85, 132, 116, 89, 25), 'source_commit'),
    ('docs/verification/cp1.1-design-002-freeze-receipt.json', 12, 'Hex High Entropy String', (105, 25, 85, 13, 12, 79, 190, 129, 244, 130, 231, 253, 24, 111, 36, 207, 228, 195, 85, 155), 'sha256'),
    ('docs/verification/cp1.1-design-002-freeze-receipt.json', 16, 'Hex High Entropy String', (198, 164, 130, 210, 227, 38, 99, 187, 100, 195, 225, 162, 209, 245, 56, 225, 90, 97, 8, 248), 'sha256'),
    ('docs/verification/cp1.1-design-002-freeze-receipt.json', 39, 'Secret Keyword', (151, 171, 186, 105, 4, 231, 246, 218, 55, 99, 228, 207, 67, 40, 33, 89, 220, 207, 175, 164), 'prior_pr21_secret_scan'),
    ('docs/verification/cp1.1-design-002-independent-review.json', 6, 'Hex High Entropy String', (105, 25, 85, 13, 12, 79, 190, 129, 244, 130, 231, 253, 24, 111, 36, 207, 228, 195, 85, 155), 'reviewed_manifest_sha256'),
    ('docs/verification/cp1.1-design-002-independent-review.json', 9, 'Hex High Entropy String', (50, 143, 51, 125, 101, 162, 80, 63, 80, 236, 236, 153, 164, 62, 20, 120, 158, 45, 124, 45), 'manifest_sha256'),
    ('docs/verification/cp1.1-design-002-review-manifest.json', 3, 'Hex High Entropy String', (153, 123, 139, 254, 62, 31, 238, 60, 245, 30, 236, 50, 208, 188, 98, 85, 132, 116, 89, 25), 'source_commit'),
    ('docs/verification/cp1.1-design-002-review-manifest.json', 6, 'Hex High Entropy String', (146, 40, 135, 177, 11, 79, 219, 83, 198, 141, 219, 225, 33, 201, 62, 142, 165, 187, 218, 231), 'docs/architecture/persona/owner-interface-persona-contract.md'),
    ('docs/verification/cp1.1-design-002-review-manifest.json', 7, 'Hex High Entropy String', (211, 52, 209, 144, 233, 62, 52, 8, 31, 160, 52, 103, 215, 23, 1, 98, 198, 126, 133, 177), 'docs/architecture/persona/persona-acceptance-scenarios.md'),
    ('docs/verification/cp1.1-design-002-review-manifest.json', 8, 'Hex High Entropy String', (188, 122, 36, 239, 248, 227, 46, 121, 212, 168, 179, 196, 82, 160, 211, 155, 51, 216, 2, 0), 'docs/architecture/persona/persona-profile.yaml'),
    ('docs/verification/cp1.1-design-002-review-manifest.json', 9, 'Hex High Entropy String', (44, 235, 148, 190, 98, 229, 218, 167, 143, 23, 1, 66, 249, 74, 151, 70, 110, 212, 182, 176), 'docs/architecture/persona/persona-versioning.md'),
    ('docs/verification/cp1.1-design-002-review-manifest.json', 10, 'Hex High Entropy String', (35, 146, 100, 76, 82, 85, 252, 193, 191, 93, 11, 180, 202, 67, 220, 23, 0, 165, 126, 174), 'docs/architecture/persona/principle-derivation.md'),
    ('docs/verification/cp1.1-design-002-review-manifest.json', 11, 'Hex High Entropy String', (251, 164, 86, 240, 153, 237, 83, 79, 100, 76, 64, 74, 116, 65, 178, 192, 189, 214, 185, 246), 'docs/architecture/persona/runtime-guidance.md'),
    ('docs/verification/cp1.1-design-002-review-manifest.json', 12, 'Hex High Entropy String', (11, 4, 178, 202, 176, 112, 38, 91, 16, 226, 205, 226, 186, 220, 171, 117, 148, 172, 79, 20), 'docs/architecture/persona/WOLF15_SENTIENT_PRINCIPLE.md'),
    ('docs/verification/cp1.1-design-002-review-manifest.json', 13, 'Hex High Entropy String', (35, 194, 220, 209, 124, 181, 184, 167, 69, 68, 66, 180, 72, 39, 9, 164, 218, 166, 241, 249), 'README.md'),
    ('docs/verification/cp1.1-design-002-review-manifest.json', 14, 'Hex High Entropy String', (98, 179, 158, 105, 31, 95, 107, 5, 184, 149, 66, 192, 174, 187, 178, 90, 137, 219, 88, 221), 'AGENTS.md'),
    ('docs/verification/cp1.1-design-002-review-manifest.json', 15, 'Hex High Entropy String', (114, 100, 204, 131, 217, 138, 251, 103, 194, 159, 234, 196, 200, 13, 19, 173, 195, 148, 53, 120), 'docs/architecture/cp1/principle-integration.md'),
    ('docs/verification/sentient-identity-20260928.json', 2, 'Hex High Entropy String', (212, 23, 177, 43, 109, 225, 121, 113, 95, 26, 1, 122, 52, 232, 212, 94, 21, 129, 180, 186), 'base_sha'),
    ('docs/verification/sentient-identity-20260928.json', 4, 'Hex High Entropy String', (61, 235, 121, 179, 44, 4, 177, 65, 138, 132, 219, 88, 46, 1, 197, 247, 236, 21, 186, 55), 'source_manifest_sha256'),
    ('docs/verification/sentient-identity-20260928.json', 26, 'Hex High Entropy String', (2, 51, 125, 65, 54, 239, 8, 6, 76, 170, 142, 216, 250, 49, 164, 85, 105, 201, 56, 158), 'wheel_sha256'),
    ('docs/verification/sentient-identity-20260928.json', 56, 'Hex High Entropy String', (104, 157, 45, 51, 189, 135, 94, 135, 252, 228, 193, 151, 147, 63, 74, 82, 119, 159, 205, 112), 'git_source_manifest_sha256'),
)

FROZEN_DIGESTS = {
    'AGENTS.md': (168, 91, 30, 235, 253, 211, 180, 58, 8, 131, 44, 151, 244, 197, 255, 8, 216, 42, 58, 96, 115, 171, 235, 201, 82, 156, 200, 44, 196, 104, 88, 95),
    'README.md': (200, 7, 164, 31, 191, 19, 100, 142, 38, 252, 135, 202, 36, 0, 122, 148, 94, 12, 109, 138, 161, 15, 142, 32, 237, 124, 129, 39, 14, 205, 224, 7),
    'docs/architecture/cp1/acceptance-scenarios.json': (179, 252, 21, 55, 105, 59, 133, 153, 108, 28, 144, 181, 59, 208, 255, 92, 188, 190, 90, 219, 60, 66, 239, 134, 248, 142, 103, 0, 57, 227, 139, 205),
    'docs/architecture/cp1/cp1.1-freeze-receipt.json': (28, 248, 206, 174, 27, 116, 185, 54, 41, 217, 75, 10, 107, 133, 81, 15, 17, 69, 196, 110, 248, 133, 128, 15, 14, 119, 216, 214, 254, 51, 31, 236),
    'docs/architecture/cp1/fixtures/envelope.canonical.json': (216, 225, 205, 196, 233, 139, 196, 232, 221, 90, 25, 9, 122, 33, 160, 248, 191, 156, 175, 229, 146, 27, 47, 253, 213, 103, 229, 18, 81, 32, 91, 102),
    'docs/architecture/cp1/fixtures/manifest.json': (243, 224, 99, 78, 143, 81, 225, 5, 198, 1, 228, 234, 162, 17, 152, 100, 91, 250, 28, 100, 227, 188, 107, 243, 195, 10, 239, 237, 34, 185, 253, 8),
    'docs/architecture/cp1/fixtures/request.canonical.json': (174, 84, 23, 250, 192, 73, 253, 213, 188, 228, 142, 190, 207, 209, 165, 125, 108, 246, 45, 62, 36, 1, 204, 113, 124, 251, 61, 192, 28, 208, 102, 52),
    'docs/architecture/cp1/fixtures/response.canonical.json': (241, 83, 219, 170, 3, 140, 113, 128, 45, 215, 140, 93, 194, 232, 17, 226, 214, 74, 55, 7, 6, 112, 120, 237, 220, 247, 175, 25, 197, 189, 234, 170),
    'docs/architecture/cp1/gateway-contract.md': (86, 6, 72, 3, 246, 79, 153, 188, 104, 175, 61, 239, 214, 71, 66, 98, 45, 67, 195, 105, 99, 95, 129, 165, 201, 89, 244, 196, 49, 87, 210, 8),
    'docs/architecture/cp1/gateway-schema.json': (174, 192, 211, 44, 122, 71, 106, 9, 187, 81, 78, 139, 184, 224, 51, 221, 255, 9, 17, 219, 101, 228, 123, 195, 1, 144, 251, 37, 134, 4, 101, 231),
    'docs/architecture/cp1/persona-guidance.md': (229, 209, 52, 133, 102, 54, 22, 98, 154, 228, 242, 155, 93, 221, 45, 145, 182, 32, 41, 30, 162, 143, 26, 38, 126, 232, 201, 137, 134, 87, 111, 195),
    'docs/architecture/cp1/persona-profile.yaml': (237, 85, 48, 103, 23, 25, 170, 93, 119, 240, 49, 15, 239, 250, 218, 120, 135, 186, 216, 136, 63, 38, 178, 165, 4, 158, 152, 117, 12, 58, 43, 147),
    'docs/architecture/cp1/principle-integration.md': (20, 116, 133, 33, 42, 182, 51, 131, 190, 25, 8, 248, 239, 21, 68, 10, 80, 44, 224, 68, 81, 233, 116, 230, 144, 109, 95, 6, 91, 170, 24, 195),
    'docs/architecture/cp1/prohibition-matrix-draft.json': (229, 31, 158, 18, 244, 26, 255, 47, 235, 71, 234, 79, 48, 199, 62, 38, 208, 217, 130, 53, 96, 47, 238, 229, 86, 41, 35, 57, 29, 255, 12, 69),
    'docs/architecture/cp1/prohibition-matrix.md': (156, 190, 28, 159, 175, 1, 72, 249, 111, 4, 43, 189, 248, 162, 221, 180, 203, 237, 112, 131, 151, 102, 147, 103, 49, 14, 166, 227, 30, 146, 223, 112),
    'docs/architecture/cp1/reviews/cp11-review-manifest.json': (138, 205, 186, 183, 82, 132, 30, 151, 30, 220, 115, 218, 197, 95, 126, 215, 153, 80, 67, 197, 188, 167, 245, 122, 250, 73, 65, 142, 141, 176, 202, 227),
    'docs/architecture/cp1/reviews/final-contract-review-prefreeze.json': (112, 237, 91, 170, 181, 168, 14, 83, 80, 84, 144, 154, 160, 158, 143, 151, 37, 80, 213, 1, 165, 87, 238, 100, 185, 132, 56, 225, 73, 164, 103, 99),
    'docs/architecture/cp1/reviews/final-persona-review-prefreeze.json': (183, 16, 157, 189, 224, 146, 35, 202, 82, 28, 58, 227, 13, 222, 203, 169, 151, 244, 137, 25, 192, 148, 144, 81, 208, 87, 152, 53, 203, 110, 124, 134),
    'docs/architecture/cp1/schema-fixture-verification.json': (17, 212, 227, 36, 16, 109, 188, 184, 22, 229, 198, 88, 142, 178, 192, 113, 19, 182, 95, 164, 63, 6, 226, 128, 254, 90, 50, 33, 224, 167, 195, 85),
    'docs/architecture/cp1/verify_contract_fixtures.py': (225, 132, 14, 102, 199, 2, 29, 127, 187, 50, 183, 181, 159, 217, 94, 183, 163, 89, 249, 220, 34, 83, 173, 20, 113, 5, 208, 144, 19, 137, 197, 203),
    'docs/architecture/persona/WOLF15_SENTIENT_PRINCIPLE.md': (7, 191, 212, 75, 208, 13, 150, 212, 95, 168, 174, 145, 103, 153, 115, 73, 29, 84, 218, 155, 212, 37, 180, 7, 190, 39, 14, 152, 99, 50, 180, 48),
    'docs/architecture/persona/owner-interface-persona-contract.md': (241, 186, 238, 203, 164, 213, 191, 187, 192, 222, 41, 72, 146, 131, 162, 100, 37, 221, 216, 114, 218, 67, 37, 50, 223, 191, 184, 113, 106, 114, 171, 68),
    'docs/architecture/persona/persona-acceptance-scenarios.md': (156, 159, 148, 82, 175, 213, 109, 20, 56, 104, 49, 187, 71, 160, 72, 22, 167, 165, 34, 53, 2, 15, 24, 129, 248, 68, 80, 83, 111, 172, 52, 217),
    'docs/architecture/persona/persona-profile.yaml': (181, 135, 242, 248, 90, 56, 170, 137, 8, 24, 185, 190, 218, 192, 136, 165, 220, 191, 112, 24, 37, 101, 61, 196, 244, 149, 240, 209, 241, 145, 225, 183),
    'docs/architecture/persona/persona-versioning.md': (83, 161, 23, 32, 107, 177, 3, 136, 196, 129, 42, 172, 108, 211, 0, 246, 74, 196, 212, 86, 196, 248, 90, 163, 53, 192, 196, 253, 148, 91, 30, 173),
    'docs/architecture/persona/principle-derivation.md': (124, 246, 18, 225, 183, 20, 195, 254, 179, 118, 14, 176, 94, 12, 141, 123, 89, 138, 52, 226, 77, 194, 53, 12, 3, 7, 161, 138, 97, 10, 76, 129),
    'docs/architecture/persona/runtime-guidance.md': (47, 200, 216, 116, 126, 119, 92, 135, 243, 17, 61, 15, 64, 210, 178, 180, 173, 166, 190, 141, 139, 136, 13, 95, 95, 215, 121, 52, 251, 31, 241, 223),
    'docs/research/algorithm-donors/adoption-registry.yaml': (232, 38, 225, 155, 241, 135, 92, 224, 205, 94, 3, 99, 125, 166, 47, 56, 65, 169, 252, 91, 129, 74, 130, 139, 97, 154, 13, 132, 124, 76, 181, 221),
    'docs/research/algorithm-donors/anti-pattern-registry.md': (24, 109, 106, 230, 110, 204, 37, 230, 188, 146, 67, 102, 246, 210, 119, 199, 238, 140, 51, 125, 141, 188, 15, 36, 199, 231, 21, 136, 118, 229, 132, 121),
    'docs/research/algorithm-donors/anti-patterns.md': (77, 107, 123, 226, 112, 29, 13, 120, 169, 173, 79, 209, 44, 190, 134, 39, 121, 190, 4, 90, 216, 64, 111, 227, 215, 16, 123, 249, 119, 14, 184, 4),
    'docs/research/algorithm-donors/codex-desktop-implementation-contract.md': (245, 217, 199, 11, 233, 223, 149, 138, 237, 68, 223, 157, 112, 101, 111, 156, 54, 196, 172, 89, 85, 102, 117, 47, 157, 23, 178, 31, 164, 102, 67, 77),
    'docs/research/algorithm-donors/receipts/ALG-REG-001-freeze.yaml': (204, 114, 241, 206, 13, 41, 36, 105, 61, 51, 4, 251, 7, 48, 118, 172, 131, 51, 46, 173, 231, 211, 247, 84, 81, 90, 124, 202, 250, 114, 162, 39),
    'docs/research/algorithm-donors/receipts/CP0_ADDENDUM_01_A01_REVIEW_a6c2f24.json': (73, 192, 23, 27, 18, 117, 73, 21, 134, 87, 88, 162, 41, 95, 14, 175, 173, 129, 86, 102, 233, 66, 139, 2, 61, 156, 252, 48, 21, 149, 178, 170),
    'docs/verification/cp1.1-design-002-freeze-receipt.json': (153, 32, 181, 75, 78, 223, 49, 145, 140, 169, 86, 117, 77, 138, 177, 146, 113, 25, 155, 83, 231, 68, 88, 117, 22, 28, 191, 112, 187, 204, 69, 238),
    'docs/verification/cp1.1-design-002-independent-review.json': (239, 29, 180, 185, 171, 91, 220, 210, 64, 144, 248, 229, 122, 183, 11, 126, 126, 237, 154, 104, 210, 210, 232, 193, 255, 74, 67, 10, 134, 243, 154, 76),
    'docs/verification/cp1.1-design-002-review-manifest.json': (214, 41, 50, 187, 203, 252, 164, 89, 175, 101, 78, 218, 142, 213, 226, 237, 7, 53, 99, 234, 68, 30, 137, 227, 68, 61, 220, 2, 213, 208, 242, 207),
}



def exact_keys(value: Any, keys: set[str]) -> None:
    require(type(value) is dict and set(value) == keys, "INVALID_SCHEMA")


# Historical pins stay immutable; current AGENTS is bound by the successor.
HISTORICAL_FROZEN_PATHS = {"AGENTS.md": "docs/verification/cp1.1-design-003-historical-AGENTS.md"}
ACTIVE_GENERATION = "CP1.1-DESIGN-003"
ACTIVE_MANIFEST_PATH = "docs/verification/cp1.1-design-003-review-manifest.json"
ACTIVE_REVIEW_PATH = "docs/verification/cp1.1-design-003-independent-review.json"
ACTIVE_FREEZE_PATH = "docs/verification/cp1.1-design-003-freeze-receipt.json"
INTEGRATION_BASE_OID = (221, 73, 238, 16, 94, 58, 7, 179, 254, 20, 121, 37, 233, 212, 77, 156, 58, 118, 51, 255)
ACTIVE_MEMBER_DIGESTS = {
    'docs/architecture/persona/owner-interface-persona-contract.md': (241, 186, 238, 203, 164, 213, 191, 187, 192, 222, 41, 72, 146, 131, 162, 100, 37, 221, 216, 114, 218, 67, 37, 50, 223, 191, 184, 113, 106, 114, 171, 68),
    'docs/architecture/persona/persona-acceptance-scenarios.md': (156, 159, 148, 82, 175, 213, 109, 20, 56, 104, 49, 187, 71, 160, 72, 22, 167, 165, 34, 53, 2, 15, 24, 129, 248, 68, 80, 83, 111, 172, 52, 217),
    'docs/architecture/persona/persona-profile.yaml': (181, 135, 242, 248, 90, 56, 170, 137, 8, 24, 185, 190, 218, 192, 136, 165, 220, 191, 112, 24, 37, 101, 61, 196, 244, 149, 240, 209, 241, 145, 225, 183),
    'docs/architecture/persona/persona-versioning.md': (83, 161, 23, 32, 107, 177, 3, 136, 196, 129, 42, 172, 108, 211, 0, 246, 74, 196, 212, 86, 196, 248, 90, 163, 53, 192, 196, 253, 148, 91, 30, 173),
    'docs/architecture/persona/principle-derivation.md': (124, 246, 18, 225, 183, 20, 195, 254, 179, 118, 14, 176, 94, 12, 141, 123, 89, 138, 52, 226, 77, 194, 53, 12, 3, 7, 161, 138, 97, 10, 76, 129),
    'docs/architecture/persona/runtime-guidance.md': (47, 200, 216, 116, 126, 119, 92, 135, 243, 17, 61, 15, 64, 210, 178, 180, 173, 166, 190, 141, 139, 136, 13, 95, 95, 215, 121, 52, 251, 31, 241, 223),
    'docs/architecture/persona/WOLF15_SENTIENT_PRINCIPLE.md': (7, 191, 212, 75, 208, 13, 150, 212, 95, 168, 174, 145, 103, 153, 115, 73, 29, 84, 218, 155, 212, 37, 180, 7, 190, 39, 14, 152, 99, 50, 180, 48),
    'README.md': (200, 7, 164, 31, 191, 19, 100, 142, 38, 252, 135, 202, 36, 0, 122, 148, 94, 12, 109, 138, 161, 15, 142, 32, 237, 124, 129, 39, 14, 205, 224, 7),
    'AGENTS.md': (139, 178, 49, 35, 235, 37, 22, 164, 182, 118, 158, 90, 67, 85, 203, 249, 46, 33, 119, 17, 125, 95, 19, 101, 229, 59, 67, 224, 44, 107, 3, 208),
    'docs/architecture/cp1/principle-integration.md': (20, 116, 133, 33, 42, 182, 51, 131, 190, 25, 8, 248, 239, 21, 68, 10, 80, 44, 224, 68, 81, 233, 116, 230, 144, 109, 95, 6, 91, 170, 24, 195),
}
# Independently reviewed successor records; exact artifact pins do not replace runtime acceptance.
SUCCESSOR_ARTIFACT_DIGESTS = {
    'docs/verification/cp1.1-design-003-review-manifest.json': (57, 113, 84, 240, 228, 28, 219, 127, 186, 215, 103, 252, 75, 139, 136, 24, 218, 219, 158, 172, 149, 50, 228, 231, 26, 165, 109, 169, 74, 94, 64, 229),
    'docs/verification/cp1.1-design-003-independent-review.json': (10, 31, 154, 112, 167, 0, 248, 209, 80, 222, 75, 84, 178, 73, 116, 91, 18, 101, 204, 25, 216, 78, 199, 178, 83, 188, 84, 74, 176, 182, 183, 204),
    'docs/verification/cp1.1-design-003-freeze-receipt.json': (190, 219, 242, 2, 80, 31, 235, 182, 43, 145, 52, 219, 0, 142, 224, 72, 89, 209, 99, 253, 82, 188, 231, 33, 251, 124, 44, 102, 195, 238, 201, 175),
}

def historical_frozen_integrity(blobs: dict[str, bytes]) -> None:
    """Preserve all historical pins; only AGENTS uses its immutable archive."""
    for path, expected in FROZEN_DIGESTS.items():
        proof_path = HISTORICAL_FROZEN_PATHS.get(path, path)
        require(proof_path in blobs, "FROZEN_ARTIFACT_MISSING")
        require(tuple(hashlib.sha256(blobs[proof_path]).digest()) == expected,
                "FROZEN_ARTIFACT_CHANGED")


def active_generation_integrity(blobs: dict[str, bytes]) -> None:
    """Exact active bytes plus a fresh review/freeze; pending never means PASS."""
    for path, expected in {**ACTIVE_MEMBER_DIGESTS, **SUCCESSOR_ARTIFACT_DIGESTS}.items():
        require(path in blobs, "ACTIVE_GENERATION_ARTIFACT_MISSING")
        require(tuple(hashlib.sha256(blobs[path]).digest()) == expected,
                "ACTIVE_GENERATION_ARTIFACT_CHANGED")
    manifest = collection.parse(blobs[ACTIVE_MANIFEST_PATH])
    review = collection.parse(blobs[ACTIVE_REVIEW_PATH])
    freeze = collection.parse(blobs[ACTIVE_FREEZE_PATH])
    require(all(type(item) is dict for item in (manifest, review, freeze)),
            "ACTIVE_GENERATION_SCHEMA")
    require(manifest.get("schema_version") == "cp1.1-review-manifest/v1"
            and review.get("schema_version") == "cp1.1-independent-review/v1"
            and freeze.get("schema_version") == "cp1.1-freeze-receipt/v1",
            "ACTIVE_GENERATION_SCHEMA")
    require(all(item.get("generation") == ACTIVE_GENERATION for item in (manifest, review, freeze)),
            "ACTIVE_GENERATION_BINDING")
    require(manifest.get("predecessor") == "CP1.1-DESIGN-002"
            and manifest.get("status") == "CONTENT_BOUND", "ACTIVE_GENERATION_BINDING")
    expected_members = {path: bytes(value).hex() for path, value in ACTIVE_MEMBER_DIGESTS.items()}
    require(manifest.get("files") == expected_members, "ACTIVE_GENERATION_MEMBERS")
    source_commit = bytes(INTEGRATION_BASE_OID).hex()
    require(manifest.get("source_commit") == source_commit
            and freeze.get("source_commit") == source_commit, "ACTIVE_GENERATION_BASE")
    manifest_digest = collection.digest(blobs[ACTIVE_MANIFEST_PATH])
    review_digest = collection.digest(blobs[ACTIVE_REVIEW_PATH])
    require(review.get("reviewed_manifest_sha256") == manifest_digest,
            "ACTIVE_GENERATION_REVIEW_BINDING")
    require(freeze.get("manifest") == {"path": ACTIVE_MANIFEST_PATH, "sha256": manifest_digest},
            "ACTIVE_GENERATION_FREEZE_BINDING")
    require(freeze.get("review_receipt") == {
        "path": ACTIVE_REVIEW_PATH, "sha256": review_digest, "status": review.get("status")
    }, "ACTIVE_GENERATION_FREEZE_BINDING")
    require(type(freeze.get("frozen_members")) is int
            and freeze["frozen_members"] == len(expected_members), "ACTIVE_GENERATION_MEMBERS")
    require(freeze.get("excluded_from_frozen_members") == [
        ACTIVE_MANIFEST_PATH, ACTIVE_REVIEW_PATH, ACTIVE_FREEZE_PATH
    ], "ACTIVE_GENERATION_MEMBERS")
    require(freeze.get("runtime_loaded") is False
            and freeze.get("cp1_1_canonical_closed") is False
            and freeze.get("authority") == "NONE", "ACTIVE_GENERATION_AUTHORITY")
    # These three receipts are pinned independently of the manifest's member set.
    # Advancing them requires a fresh reviewed diff/pin update, never inheriting DESIGN-002 PASS.
    require(freeze.get("status") == "FROZEN_LOCAL_PENDING_REMOTE_INTEGRATION"
            and freeze.get("active_generation") is True
            and freeze.get("owner_acceptance") == "APPROVED"
            and review.get("status") == "PASS", "ACTIVE_GENERATION_NOT_FROZEN")
    require(type(review.get("open_blocking_findings")) is int
            and review["open_blocking_findings"] == 0
            and type(review.get("findings")) is list, "ACTIVE_GENERATION_REVIEW_INCOMPLETE")
    for value in (review.get("reviewer"), review.get("reviewed_at"),
                  freeze.get("frozen_by"), freeze.get("frozen_at")):
        require(type(value) is str and bool(value.strip()), "ACTIVE_GENERATION_REVIEW_INCOMPLETE")
    require(review.get("evidence_class") == "EXACT_ARTIFACT_DESIGN_REVIEW",
            "ACTIVE_GENERATION_REVIEW_INCOMPLETE")


def frozen_integrity(blobs: dict[str, bytes]) -> None:
    # Both domains are mandatory, even when no detector finds anything.
    historical_frozen_integrity(blobs)
    active_generation_integrity(blobs)



def classify(findings: list[dict[str, Any]], blobs: dict[str, bytes]) -> tuple[int, int]:
    known = {(p, n, k, bytes(fp).hex()): field for p, n, k, fp, field in EXCEPTIONS}
    seen: set[tuple[str, int, str, str]] = set()
    verified: dict[str, list[str]] = {}
    allowed = 0
    denied = 0
    require(type(findings) is list, "FINDINGS_SCHEMA")
    for item in findings:
        exact_keys(item, {"path", "line", "type", "fingerprint"})
        path, line, kind, fingerprint = (item[x] for x in ("path", "line", "type", "fingerprint"))
        require(type(path) is str and path in blobs, "FINDING_OUTSIDE_SCOPE")
        collection.safe_path(path)
        require(type(line) is int and 1 <= line <= len(blobs[path].decode("utf-8").splitlines()), "FINDING_LINE")
        require(type(kind) is str and bool(kind) and type(fingerprint) is str, "FINDING_SCHEMA")
        require(re.fullmatch(r"[0-9a-f]{40}", fingerprint) is not None, "FINDING_FINGERPRINT")
        identity = (path, line, kind, fingerprint)
        require(identity not in seen, "DUPLICATE_FINDING")
        seen.add(identity)
        field = known.get(identity)
        if field is None:
            denied += 1
            continue
        if path not in verified:
            normalized = blobs[path].replace(b"\r\n", b"\n")
            require(tuple(hashlib.sha256(normalized).digest()) == FILE_DIGESTS[path], "EXCEPTION_CONTEXT_CHANGED")
            verified[path] = normalized.decode("utf-8").splitlines()
        match = re.match(r"\s*[\"']?([^:\"']+)[\"']?\s*:", verified[path][line - 1])
        require(match is not None and match.group(1) == field, "EXCEPTION_FIELD_CHANGED")
        allowed += 1
    return allowed, denied


def gate_a(receipt: Any, source: dict[str, Any], blobs: dict[str, bytes], config: dict[str, Any], nonce: str) -> list[dict[str, Any]]:
    exact_keys(receipt, {"schema_version", "run_nonce", "source", "scope_policy", "config", "config_sha256",
                         "inventory_sha256", "processed_inputs", "findings", "completion"})
    require(receipt["schema_version"] == collection.SCHEMA and receipt["completion"] == "COMPLETE", "INCOMPLETE_COLLECTION")
    require(receipt["run_nonce"] == nonce, "STALE_COLLECTION")
    # Canonical bytes also distinguish integer 1 from boolean true.
    require(collection.canonical(receipt["source"]) == collection.canonical(source), "SOURCE_MISMATCH")
    require(collection.canonical(receipt["config"]) == collection.canonical(config), "CONFIG_MISMATCH")
    require(receipt["config_sha256"] == collection.digest(collection.canonical(config)), "CONFIG_DIGEST")
    require(receipt["inventory_sha256"] == collection.digest(collection.canonical(source["inputs"])), "INVENTORY_DIGEST")
    require(receipt["scope_policy"] == config["scope"], "SCOPE_MISMATCH")
    rows = receipt["processed_inputs"]
    require(type(rows) is list and len(rows) == len(source["inputs"]), "INPUT_COVERAGE")
    expected = {x["path"]: x for x in source["inputs"]}
    seen: set[str] = set()
    # Independently derive transforms and view identities, without running detectors.
    with collection.engine() as (plugins, transformers):
        detector_names = [p.__class__.__name__ for p in plugins]
        detector_types = {p.secret_type for p in plugins}
        for raw_row in rows:
            exact_keys(raw_row, {"path", "input_status", "mode", "blob_oid", "raw_sha256", "byte_length", "source_lines",
                             "required_detectors", "required_passes", "passes", "transform_attempts", "filter_decisions", "filter_decisions_digest"})
            row = cast(dict[str, Any], raw_row)
            path = row["path"]
            require(type(path) is str and path in expected and path not in seen, "INPUT_IDENTITY")
            seen.add(path)
            require(row["input_status"] == "PROCESSED", "INPUT_NOT_PROCESSED")
            for key in ("mode", "blob_oid", "raw_sha256", "byte_length"):
                require(collection.canonical(row[key]) == collection.canonical(expected[path][key]), "INPUT_BINDING")
            text = blobs[path].decode("utf-8")
            views, attempts = collection.views(path, text, transformers)
            require(type(row["source_lines"]) is int and row["source_lines"] == len(text.splitlines()), "LINE_COVERAGE")
            require(row["required_detectors"] == detector_names, "DETECTOR_SET")
            require(row["required_passes"] == [name for name, _ in views], "PASS_SET")
            require(collection.canonical(row["transform_attempts"]) == collection.canonical(attempts), "TRANSFORM_COVERAGE")
            require(row["filter_decisions"] == [] and row["filter_decisions_digest"] == collection.digest(b"[]"), "UNEXPECTED_FILTER")
            expected_passes = [{"name": name, "view_sha256": collection.digest(collection.canonical(lines)),
                                "line_numbers": collection.line_numbers(lines),
                                "lines": len(lines), "detectors": [{"name": p, "calls": max(1, len(lines))} for p in detector_names]}
                               for name, lines in views]
            require(collection.canonical(row["passes"]) == collection.canonical(expected_passes), "DETECTOR_COMPLETION")
    require(seen == set(expected), "MISSING_INPUT")
    require(type(receipt["findings"]) is list, "FINDINGS_SCHEMA")
    for item in receipt["findings"]:
        require(type(item) is dict and item.get("type") in detector_types, "UNKNOWN_FINDING_TYPE")
    return receipt["findings"]


class WindowsJob:
    """Job handle owns all descendants, including after the bootstrap exits."""
    def __init__(self) -> None:
        import ctypes
        from ctypes import wintypes
        self.ctypes = ctypes
        class BasicLimits(ctypes.Structure):
            _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                        ("flags", wintypes.DWORD), ("minimum_working", ctypes.c_size_t),
                        ("maximum_working", ctypes.c_size_t), ("active_limit", wintypes.DWORD),
                        ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD), ("scheduling", wintypes.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]
        class ExtendedLimits(ctypes.Structure):
            _fields_ = [("basic", BasicLimits), ("io", IO), ("process_memory", ctypes.c_size_t),
                        ("job_memory", ctypes.c_size_t), ("peak_process", ctypes.c_size_t), ("peak_job", ctypes.c_size_t)]
        class Accounting(ctypes.Structure):
            _fields_ = [(name, ctypes.c_int64) for name in ("user", "kernel", "period_user", "period_kernel")] + [
                (name, wintypes.DWORD) for name in ("page_faults", "total", "active", "terminated")]
        self.accounting = Accounting
        kernel = cast(Any, ctypes).WinDLL("kernel32", use_last_error=True)
        kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        kernel.CreateJobObjectW.restype = wintypes.HANDLE
        kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        kernel.SetInformationJobObject.restype = wintypes.BOOL
        kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        kernel.TerminateJobObject.restype = wintypes.BOOL
        kernel.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p]
        kernel.QueryInformationJobObject.restype = wintypes.BOOL
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle.restype = wintypes.BOOL
        self.kernel = kernel
        self.handle = kernel.CreateJobObjectW(None, None)
        _bootstrap_require(bool(self.handle), "JOB_CREATE_FAILED")
        limits = ExtendedLimits()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE; no breakaway.
        if not kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            kernel.CloseHandle(self.handle)
            raise BootstrapError("JOB_LIMIT_FAILED")

    def assign(self, pid: int) -> None:
        # Bootstrap waits for a byte; it cannot spawn the command before assignment.
        handle = self.kernel.OpenProcess(0x0100 | 0x0001, False, pid)
        _bootstrap_require(bool(handle), "PROCESS_HANDLE_FAILED")
        try:
            _bootstrap_require(bool(self.kernel.AssignProcessToJobObject(self.handle, handle)), "JOB_ASSIGN_FAILED")
        finally:
            self.kernel.CloseHandle(handle)

    def active(self) -> int:
        state = self.accounting()
        _bootstrap_require(bool(self.kernel.QueryInformationJobObject(self.handle, 1, self.ctypes.byref(state),
                                                          self.ctypes.sizeof(state), None)), "JOB_QUERY_FAILED")
        return state.active

    def close(self) -> None:
        try:
            _bootstrap_require(bool(self.kernel.TerminateJobObject(self.handle, 1)), "JOB_TERMINATION_FAILED")
            deadline = time.monotonic() + 5
            while self.active():
                _bootstrap_require(time.monotonic() < deadline, "JOB_TERMINATION_UNPROVEN")
                threading.Event().wait(0.01)
        finally:
            self.kernel.CloseHandle(self.handle)


def supervised(command: list[str], root: Path, timeout: float = 120.0, limit: int = 16 * 1024 * 1024, *, own_group: bool = True) -> bytes:
    """Bound both streams during collection; never render child stderr or exception text."""
    require(timeout > 0 and limit > 0, "INVALID_RESOURCE_LIMIT")
    deadline = time.monotonic() + timeout
    job = WindowsJob() if own_group and os.name == "nt" else None
    launch = command
    if job is not None:
        bootstrap = "import sys,subprocess; gate=sys.stdin.buffer.read(1); sys.exit(subprocess.call(sys.argv[1:]) if gate==b'1' else 125)"
        launch = [sys.executable, "-I", "-c", bootstrap, *command]
    child: subprocess.Popen[bytes] | None = None
    output = bytearray()
    failure = threading.Event()
    threads: list[threading.Thread] = []
    sizes = [0, 0]

    def drain(stream: Any, index: int) -> None:
        try:
            with collection.controlled_errors():
                while True:
                    data = stream.read(4096)
                    if not data:
                        break
                    sizes[index] += len(data)
                    if sum(sizes) > limit:
                        failure.set()
                        break
                    if index == 0:
                        output.extend(data)
        except collection.ScanError:
            failure.set()
        finally:
            stream.close()

    try:
        child = subprocess.Popen(launch, cwd=root, stdin=subprocess.PIPE if job else subprocess.DEVNULL,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False,
                                 start_new_session=own_group and os.name != "nt")
        require(time.monotonic() < deadline, "COLLECTOR_TIMEOUT")
        if job is not None:
            job.assign(child.pid)
            stream = child.stdin
            require(stream is not None, "BOOTSTRAP_PIPE")
            if stream is not None:
                require(stream.write(b"1") == 1, "BOOTSTRAP_PIPE")
                stream.close()
        require(child.stdout is not None and child.stderr is not None, "CHILD_PIPE")
        for index, stream in enumerate((child.stdout, child.stderr)):
            thread = threading.Thread(target=drain, args=(stream, index), daemon=True)
            thread.start()
            threads.append(thread)  # Only successfully started threads may be joined.
        while child.poll() is None or any(t.is_alive() for t in threads):
            require(not failure.is_set(), "COLLECTOR_OUTPUT_LIMIT")
            require(time.monotonic() < deadline, "COLLECTOR_TIMEOUT")
            failure.wait(0.01)
        require(not failure.is_set(), "COLLECTOR_READ_FAILURE")
        require(child.wait(timeout=5) == 0, "COLLECTOR_EXIT_FAILURE")
        require(time.monotonic() < deadline, "COLLECTOR_TIMEOUT")
        require(sizes[1] == 0, "COLLECTOR_STDERR")
        return bytes(output)
    finally:
        # A process group contains the validator worker, collector, and its Git children.
        cleanup_ok = True
        if own_group and os.name != "nt" and child is not None:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
                cleanup_ok = False
        if job is not None:
            try:
                job.close()
            except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
                cleanup_ok = False
        if child is not None:
            try:
                if child.poll() is None:
                    child.kill()
                child.wait(timeout=5)
            except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
                cleanup_ok = False
        for thread in threads:
            try:
                thread.join(timeout=1)
            except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
                cleanup_ok = False
        readers_stopped = not any(t.is_alive() for t in threads)
        if child is not None and readers_stopped:
            for stream in (child.stdin, child.stdout, child.stderr):
                if stream is not None:
                    try:
                        stream.close()
                    except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
                        cleanup_ok = False
        require(cleanup_ok and readers_stopped, "PROCESS_PIPE_TERMINATION_UNPROVEN")


def execute_scan(root: Path, *, enforce_frozen: bool = True) -> dict[str, Any]:
    """Fixture callers may explicitly omit production pins; CLI never does so."""
    if collection is None:
        initialize_collection(root)
    if collection is None:
        raise BootstrapError("BOOTSTRAP_SOURCE_FAILURE")
    require(str(root.resolve()) == _bootstrap_binding.get("root"), "BOOTSTRAP_ROOT_MISMATCH")
    require(sys.flags.utf8_mode == 1, "UTF8_MODE_REQUIRED")
    source, blobs = collection.snapshot(root)
    require(source["head"] == _bootstrap_binding.get("head"), "BOOTSTRAP_HEAD_MISMATCH")
    if enforce_frozen:
        frozen_integrity(blobs)
    here = Path(__file__).resolve()
    for name, raw in _verified_sources.items():
        require(name in blobs and blobs[name] == raw, "EXECUTED_CODE_NOT_IN_HEAD")
    config = collection.configuration()
    policy_binding = {
        "collector_blob": next(x["blob_oid"] for x in source["inputs"] if x["path"] == "scripts/ci/collect_secret_scan.py"),
        "validator_blob": next(x["blob_oid"] for x in source["inputs"] if x["path"] == "scripts/ci/check_secret_scan.py"),
        "verified_source_binding": _bootstrap_binding["sources"],
        "validator_trust": "CALLER_TRUSTED_ENTRYPOINT",
        "collector_loading": "VERIFIED_GIT_BLOB_BUFFER",
        "locked_provenance_sha256": collection.digest(blobs["uv.lock"]),
        "exception_set_sha256": collection.digest(collection.canonical(EXCEPTIONS)),
    }
    nonce = secrets.token_hex(16)
    command = [sys.executable, "-I", "-X", "utf8", str(here), "--collector", nonce,
               "--expected-head", source["head"]]
    data = supervised(command, root, own_group=False)
    receipt = collection.parse(data)
    findings = gate_a(receipt, source, blobs, config, nonce)
    allowed, denied = classify(findings, blobs)
    after, final_blobs = collection.snapshot(root)
    require(after == source and collection.configuration() == config, "SOURCE_OR_CONFIG_DRIFT")
    if enforce_frozen:
        frozen_integrity(final_blobs)
    return {"schema_version": "wolf15-secret-gate/v2", "status": "FAIL" if denied else "PASS",
            "gate_a": "PASS", "gate_b": "FAIL" if denied else "PASS",
            "reason": "UNRECOGNIZED_FINDINGS" if denied else "ALL_GATES_SATISFIED",
            "unknown_occurrences": denied, "policy_binding": policy_binding,
            "effective_configuration_sha256": collection.digest(collection.canonical({"detector_configuration": config, "source_policy_binding": policy_binding})),
            "parent_observed_collector_exit": 0,
            "production_frozen_integrity": "PASS" if enforce_frozen else "NOT_APPLICABLE_FIXTURE",
            "known_evidence_occurrences": allowed, "collection": receipt}


def output_path(root: Path, value: str) -> Path:
    # Output name is fixed, untracked, and outside the scan inventory; no arbitrary overwrite.
    require(value == "secret-scan-receipt.json", "RECEIPT_PATH_NOT_ALLOWED")
    target = root / value
    require(not target.is_symlink() and not target.is_dir(), "UNSAFE_RECEIPT_PATH")
    require(not collection.git(root, "ls-files", "--", value), "TRACKED_RECEIPT_PATH")
    return target


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise BootstrapError("INVALID_ARGUMENTS")


def main(argv: list[str] | None = None) -> int:
    parser = SafeArgumentParser()
    parser.add_argument("legacy_report", nargs="?")
    parser.add_argument("--worker", help=argparse.SUPPRESS)
    parser.add_argument("--collector", help=argparse.SUPPRESS)
    parser.add_argument("--expected-head", help=argparse.SUPPRESS)
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--receipt", default="secret-scan-receipt.json")
    root = Path.cwd().resolve()
    arguments = sys.argv[1:] if argv is None else argv
    # Even malformed private invocations invalidate stale output. Production
    # --worker/--collector are launched only within the outer supervisor; their
    # Git subprocesses inherit that containment and must never detach from it.
    # A directly invoked private mode is not a standalone acceptance command.
    own_bootstrap_group = not any(x in {"--worker", "--collector"} for x in arguments)
    nonce: str = ""
    try:
        _invalidate_receipt_before_bootstrap(root, own_group=own_bootstrap_group)
        args = parser.parse_args(arguments)
        role = "--worker" if args.worker is not None else "--collector" if args.collector is not None else None
        if role is not None:
            candidate_nonce = args.worker if role == "--worker" else args.collector
            if not isinstance(candidate_nonce, str):
                raise BootstrapError("INTERNAL_NONCE")
            nonce = candidate_nonce
            _bootstrap_require(arguments == [role, nonce, "--expected-head", args.expected_head], "INTERNAL_ARGUMENTS")
            _bootstrap_require(isinstance(nonce, str) and re.fullmatch(r"[0-9a-f]{32}", nonce) is not None, "INTERNAL_NONCE")
            _bootstrap_require(isinstance(args.expected_head, str) and
                               re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", args.expected_head) is not None,
                               "EXPECTED_HEAD_REQUIRED")
        else:
            _bootstrap_require(args.expected_head is None, "INTERNAL_ARGUMENTS")
            if not args.scan or args.legacy_report is not None:
                print("Secret scan FAIL: COVERAGE_NOT_PROVEN")
                return 1
        initialize_collection(root, args.expected_head, _own_group=own_bootstrap_group)
    except Exception:  # noqa: BLE001 -- fail closed and sanitize operational failures
        print("Secret scan FAIL: invalid invocation, source binding or output path")
        return 1
    if role is not None:
        logging.disable(logging.CRITICAL)
        try:
            with collection.controlled_errors():
                with open(os.devnull, "w", encoding="utf-8") as sink, contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                    if role == "--worker":
                        result = execute_scan(root)
                        result["worker_nonce"] = nonce
                    else:
                        result = collection.collect(root, nonce)
                        require(result["source"]["head"] == _bootstrap_binding["head"], "BOOTSTRAP_HEAD_MISMATCH")
                        for path, bound in _bootstrap_binding["sources"].items():
                            row = next((x for x in result["source"]["inputs"] if x["path"] == path), None)
                            require(row is not None and all(row[k] == bound[k] for k in bound), "EXECUTED_CODE_NOT_IN_HEAD")
                sys.stdout.buffer.write(collection.canonical(result))
                return 0
        except collection.ScanError:
            sys.stdout.write('{"error":"VALIDATION_FAILED"}')
            return 1
    target: Path | None = None
    temporary: Path | None = None
    try:
        with collection.controlled_errors():
            target = output_path(root, args.receipt)
            target.unlink(missing_ok=True)
            require(args.scan and args.legacy_report is None, "COVERAGE_NOT_PROVEN")
            nonce = secrets.token_hex(16)
            command = [sys.executable, "-I", "-X", "utf8", str(Path(__file__).resolve()), "--worker", nonce,
                       "--expected-head", _bootstrap_binding["head"]]
            result = collection.parse(supervised(command, root, timeout=120.0))
            require(type(result) is dict and result.get("worker_nonce") == nonce, "WORKER_BINDING")
            require(result.get("status") in {"PASS", "FAIL"}, "WORKER_RESULT")
            result["parent_observed_worker_exit"] = 0
            temporary = root / (".secret-scan-" + secrets.token_hex(16) + ".tmp")
            with temporary.open("xb") as handle:
                handle.write(collection.canonical(result))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, target)
            passed = result["status"] == "PASS"
            print("Secret scan PASS" if passed else "Secret scan FAIL; sanitized evidence written to receipt")
            return 0 if passed else 1
    except collection.ScanError as exc:
        # Only this reviewed constant is public; never render exception text or candidate values.
        if type(exc) is collection.ScanError and exc.args == ("COVERAGE_NOT_PROVEN",):
            print("Secret scan FAIL: COVERAGE_NOT_PROVEN")
        else:
            print("Secret scan FAIL: collection, evidence or frozen-integrity gate not satisfied")
        return 1
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
