"""Offline collection of every regular tracked Git blob, with completion evidence.

No file/line/candidate suppression. Raw plus supported transformed views are
scanned; extra occurrences fail Gate B rather than being admitted automatically.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.metadata
import io
import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
import unicodedata
from collections.abc import Iterator
from pathlib import Path, PurePosixPath
from types import TracebackType
from typing import Any, Literal, NoReturn, cast

VERSION = "wolf15-secret-collector-v2"
SCHEMA = "wolf15-secret-scan/v2"
SCANNER_VERSION = "1.5.0"
MAX_FILES = 4096
MAX_FILE_BYTES = 4 * 1024 * 1024
MAX_TOTAL_BYTES = 16 * 1024 * 1024
MAX_OUTPUT_BYTES = 16 * 1024 * 1024
MAX_LINES = 100000
GIT_TIMEOUT = 15
# Payload and protocol framing have independent bounds. SHA-256 is the longest
# supported Git object ID; sizes are canonical decimal integers.
MAX_BATCH_HEADER_BYTES = 64 + len(b" blob ") + len(str(MAX_FILE_BYTES)) + 1
TRANSFORMS = ["YAMLTransformer", "ConfigFileTransformer", "EagerConfigFileTransformer"]
PLUGIN_CONFIG = [{'name': 'ArtifactoryDetector'}, {'name': 'AWSKeyDetector'}, {'name': 'AzureStorageKeyDetector'}, {'name': 'Base64HighEntropyString', 'limit': 4.5}, {'name': 'BasicAuthDetector'}, {'name': 'CloudantDetector'}, {'name': 'DiscordBotTokenDetector'}, {'name': 'GitHubTokenDetector'}, {'name': 'GitLabTokenDetector'}, {'name': 'HexHighEntropyString', 'limit': 3.0}, {'name': 'IbmCloudIamDetector'}, {'name': 'IbmCosHmacDetector'}, {'name': 'IPPublicDetector'}, {'name': 'JwtTokenDetector'}, {'name': 'KeywordDetector', 'keyword_exclude': ''}, {'name': 'MailchimpDetector'}, {'name': 'NpmDetector'}, {'name': 'OpenAIDetector'}, {'name': 'PrivateKeyDetector'}, {'name': 'PypiTokenDetector'}, {'name': 'SendGridDetector'}, {'name': 'SlackDetector'}, {'name': 'SoftlayerDetector'}, {'name': 'SquareOAuthDetector'}, {'name': 'StripeDetector'}, {'name': 'TelegramBotTokenDetector'}, {'name': 'TwilioKeyDetector'}]


class ScanError(ValueError):
    """A fixed, sanitized failure category."""


class _ControlledErrors(contextlib.AbstractContextManager[None]):
    """Classify an operation's exit without suppressing any failure.

    The protocol supplies the pending exception. Domain errors and process-control
    exceptions propagate unchanged; other Exception instances become a fixed
    public category. The original error is never logged or formatted here.
    """

    def __enter__(self) -> None:
        return None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        if (
            exc_type is not None
            and issubclass(exc_type, Exception)
            and not issubclass(exc_type, ScanError)
        ):
            raise ScanError("UNEXPECTED_OPERATION_FAILURE") from None
        return False


def controlled_errors() -> _ControlledErrors:
    """Create the fail-closed translation boundary used by typed CLI handlers."""
    return _ControlledErrors()


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ScanError(code)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def parse(data: bytes) -> Any:
    require(len(data) <= MAX_OUTPUT_BYTES, "OUTPUT_LIMIT")
    return json.loads(data.decode("utf-8", errors="strict"), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ScanError("NONFINITE_JSON")))


def git(root: Path, *args: str) -> bytes:
    env = os.environ.copy()
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_NO_LAZY_FETCH"] = "1"
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_OPTIONAL_LOCKS"] = "0"
    child = subprocess.Popen(["git", "-c", "core.fsmonitor=false", "-C", str(root), *args], stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
    data = bytearray()
    failure = threading.Event()
    def read() -> None:
        try:
            with controlled_errors():
                stream = child.stdout
                if stream is None:
                    raise ScanError("GIT_PIPE")
                while True:
                    chunk = stream.read(4096)
                    if not chunk:
                        return
                    if len(data) + len(chunk) > MAX_OUTPUT_BYTES:
                        failure.set()
                        child.kill()
                        return
                    data.extend(chunk)
        except ScanError:
            failure.set()
        finally:
            if child.stdout is not None:
                child.stdout.close()
    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    try:
        child.wait(timeout=GIT_TIMEOUT)
        reader.join(timeout=1)
        require(not reader.is_alive() and not failure.is_set(), "GIT_OUTPUT_FAILURE")
        require(child.returncode == 0, "GIT_FAILURE")
        return bytes(data)
    finally:
        if child.poll() is None:
            child.kill()
        child.wait(timeout=5)
        reader.join(timeout=1)



class _BatchReader:
    """Bound wire consumption separately from the raw-blob payload budget."""

    def __init__(self, stream: Any, limit: int) -> None:
        self.stream = stream
        self.limit = limit
        self.consumed = 0

    def _account(self, data: bytes) -> bytes:
        self.consumed += len(data)
        require(self.consumed <= self.limit, "GIT_BATCH_WIRE_LIMIT")
        return data

    def header(self) -> bytes:
        data = self._account(self.stream.readline(MAX_BATCH_HEADER_BYTES + 1))
        require(len(data) <= MAX_BATCH_HEADER_BYTES and data.endswith(b"\n"),
                "GIT_BATCH_HEADER")
        return data

    def exact(self, size: int) -> bytes:
        data = bytearray()
        while len(data) < size:
            chunk = self._account(self.stream.read(min(size - len(data), 65536)))
            require(bool(chunk), "GIT_BATCH_TRUNCATED")
            data.extend(chunk)
        return bytes(data)

    def eof(self) -> None:
        require(not self._account(self.stream.read(1)), "GIT_BATCH_TRAILING_DATA")


def _read_batch_frame(reader: _BatchReader, expected_oid: str, remaining: int) -> bytes:
    """Validate one response before allocating or accepting its blob bytes."""
    fields = reader.header()[:-1].split(b" ")
    require(len(fields) == 3, "GIT_BATCH_HEADER")
    oid, kind, encoded_size = fields
    require(oid == expected_oid.encode("ascii"), "GIT_BATCH_OID")
    require(kind == b"blob", "GIT_BATCH_TYPE")
    require(bool(encoded_size) and encoded_size.isdigit(), "GIT_BATCH_SIZE")
    size = int(encoded_size)
    require(encoded_size == str(size).encode("ascii"), "GIT_BATCH_SIZE")
    require(size <= MAX_FILE_BYTES, "INPUT_SIZE_LIMIT")
    require(size <= remaining, "SCOPE_LIMIT")
    raw = reader.exact(size)
    require(reader.exact(1) == b"\n", "GIT_BATCH_FRAMING")
    object_hash = hashlib.sha1() if len(expected_oid) == 40 else hashlib.sha256()
    object_hash.update(b"blob " + str(size).encode("ascii") + b"\0")
    object_hash.update(raw)
    require(object_hash.hexdigest() == expected_oid, "GIT_BATCH_OBJECT_HASH")
    return raw


def git_blobs(root: Path, oids: list[str]) -> list[bytes]:
    """One fresh cat-file session, bounded by the whole 15-second Git budget.

    Alternate one short request and one complete response to avoid pipe
    deadlock. Git inherits the outer worker's Windows Job or POSIX process
    group; never detach it from that containment.
    """
    require(len(oids) <= MAX_FILES, "SCOPE_LIMIT")
    require(all(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", oid) for oid in oids),
            "GIT_BATCH_REQUEST")
    require(len({len(oid) for oid in oids}) <= 1, "GIT_BATCH_OBJECT_FORMAT")
    env = os.environ.copy()
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_NO_LAZY_FETCH"] = "1"
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_OPTIONAL_LOCKS"] = "0"
    deadline = time.monotonic() + GIT_TIMEOUT
    try:
        child = subprocess.Popen(["git", "-c", "core.fsmonitor=false", "-C", str(root), "cat-file", "--batch"],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL, env=env, shell=False, bufsize=0)
    except Exception:  # noqa: BLE001 -- cleanup must fail closed without leaking content
        raise ScanError("GIT_BATCH_SPAWN_FAILURE") from None
    blobs: list[bytes] = []
    errors: list[str] = []
    finished = threading.Event()

    def exchange() -> None:
        try:
            with controlled_errors():
                source, sink = child.stdout, child.stdin
                require(source is not None and sink is not None, "GIT_BATCH_PIPE")
                if source is None or sink is None:
                    return  # Type narrowing; require above always rejects.
                wire_limit = MAX_TOTAL_BYTES + len(oids) * (MAX_BATCH_HEADER_BYTES + 1)
                reader = _BatchReader(source, wire_limit)
                total = 0
                for oid in oids:
                    request = oid.encode("ascii") + b"\n"
                    require(sink.write(request) == len(request), "GIT_BATCH_WRITE")
                    raw = _read_batch_frame(reader, oid, MAX_TOTAL_BYTES - total)
                    total += len(raw)  # Every path counts, including repeated OIDs.
                    blobs.append(raw)
                sink.close()
                reader.eof()
        except ScanError as exc:
            errors.append(str(exc))
        finally:
            for stream in (child.stdin, child.stdout):
                if stream is not None:
                    try:
                        stream.close()
                    except Exception:  # noqa: BLE001 -- cleanup must fail closed without leaking content
                        errors.append("GIT_BATCH_CLOSE_FAILURE")
            finished.set()

    reader_thread = threading.Thread(target=exchange, daemon=True)
    started = False
    try:
        reader_thread.start()
        started = True
        while not finished.is_set() or child.poll() is None:
            require(not errors, errors[0] if errors else "GIT_BATCH_READ_FAILURE")
            remaining = deadline - time.monotonic()
            require(remaining > 0, "GIT_BATCH_TIMEOUT")
            time.sleep(min(remaining, 0.01))
        require(not errors, errors[0] if errors else "GIT_BATCH_READ_FAILURE")
        require(time.monotonic() < deadline, "GIT_BATCH_TIMEOUT")
        require(child.wait(timeout=5) == 0, "GIT_BATCH_EXIT_FAILURE")
        require(len(blobs) == len(oids), "GIT_BATCH_INCOMPLETE")
        return blobs
    finally:
        # Killing/reaping Git unblocks its pipes. The outer supervisor also
        # terminates the inherited containment on every normal/error exit.
        cleanup_ok = True
        try:
            if child.poll() is None:
                child.kill()
            child.wait(timeout=5)
        except Exception:  # noqa: BLE001 -- cleanup must fail closed without leaking content
            cleanup_ok = False
        if started:
            reader_thread.join(timeout=1)
            cleanup_ok = cleanup_ok and not reader_thread.is_alive()
        else:
            for stream in (child.stdin, child.stdout):
                if stream is not None:
                    try:
                        stream.close()
                    except Exception:  # noqa: BLE001 -- cleanup must fail closed without leaking content
                        cleanup_ok = False
        require(cleanup_ok, "GIT_BATCH_CLEANUP_FAILURE")


def safe_path(path: str) -> None:
    require(bool(path) and not path.startswith("/") and "\\" not in path, "INVALID_PATH")
    require(all(x not in ("", ".", "..") for x in path.split("/")), "INVALID_PATH")
    require(not PurePosixPath(path).is_absolute() and ":" not in path, "INVALID_PATH")
    require(all(ord(c) >= 32 and ord(c) != 127 for c in path), "INVALID_PATH")
    require(unicodedata.normalize("NFC", path) == path, "NONCANONICAL_PATH")


def snapshot(root: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    top = Path(git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    require(top == root.resolve(), "ROOT_MISMATCH")
    require(not git(root, "status", "--porcelain=v1", "--untracked-files=no"), "DIRTY_TRACKED_TREE")
    head = git(root, "rev-parse", "HEAD").decode("ascii").strip()
    require(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", head) is not None, "SNAPSHOT_HEAD_FORMAT")
    tree = git(root, "rev-parse", head + "^{tree}").decode("ascii").strip()
    require(re.fullmatch(r"[0-9a-f]{" + str(len(head)) + r"}", tree) is not None,
            "SNAPSHOT_TREE_FORMAT")
    # Resolve inventory through the captured commit, not a second mutable HEAD.
    inventory_bytes = git(root, "ls-tree", "-rz", "--full-tree", head)
    require(not inventory_bytes or inventory_bytes.endswith(b"\0"), "SNAPSHOT_INVENTORY_FRAMING")
    records = inventory_bytes.split(b"\0")[:-1] if inventory_bytes else []
    require(all(records), "SNAPSHOT_INVENTORY_FRAMING")
    inventory: list[dict[str, Any]] = []
    blobs: dict[str, bytes] = {}
    aliases: set[str] = set()
    entries: list[tuple[str, str, str]] = []
    for record in records:
        meta, encoded = record.split(b"\t", 1)
        fields = meta.decode("ascii").split(" ")
        require(len(fields) == 3 and all(fields), "SNAPSHOT_INVENTORY_FRAMING")
        mode, kind, oid = fields
        require(re.fullmatch(r"[0-9a-f]{" + str(len(head)) + r"}", oid) is not None,
                "GIT_BATCH_OBJECT_FORMAT")
        path = encoded.decode("utf-8", errors="strict")
        safe_path(path)
        require(path.casefold() not in aliases, "DUPLICATE_PATH")
        aliases.add(path.casefold())
        require(mode in {"100644", "100755"} and kind == "blob", "UNSUPPORTED_GIT_MODE")
        require(len(entries) < MAX_FILES, "SCOPE_LIMIT")
        entries.append((path, mode, oid))
    require(all(len(oid) == len(head) for _, _, oid in entries), "GIT_BATCH_OBJECT_FORMAT")
    raw_blobs = git_blobs(root, [oid for _, _, oid in entries])
    for (path, mode, oid), raw in zip(entries, raw_blobs, strict=True):
        size = len(raw)
        require(b"\0" not in raw, "UNSUPPORTED_INPUT")
        raw.decode("utf-8", errors="strict")
        target = root / path
        require(not target.is_symlink() and target.is_file(), "MISSING_OR_LINKED_INPUT")
        require(target.resolve().is_relative_to(root.resolve()), "PATH_ESCAPES_ROOT")
        for component in (target, *target.parents):
            if component == root:
                break
            require(not component.is_symlink() and not (getattr(component.lstat(), "st_file_attributes", 0) & 1024), "REPARSE_INPUT")
        with target.open("rb") as handle:
            working = handle.read(MAX_FILE_BYTES * 2 + 1)
        require(len(working) <= MAX_FILE_BYTES * 2, "WORKTREE_INPUT_LIMIT")
        require(working == raw or working.replace(b"\r\n", b"\n") == raw, "WORKTREE_BLOB_MISMATCH")
        blobs[path] = raw
        inventory.append({"path": path, "mode": mode, "blob_oid": oid,
                          "raw_sha256": digest(raw), "byte_length": size})
    inventory.sort(key=lambda row: row["path"].encode("utf-8"))
    require(git(root, "rev-parse", "HEAD").decode().strip() == head, "SNAPSHOT_DRIFT")
    require(not git(root, "status", "--porcelain=v1", "--untracked-files=no"), "SNAPSHOT_DRIFT")
    return {"head": head, "tree": tree, "inputs": inventory}, blobs


def package_identity() -> dict[str, Any]:
    dist = importlib.metadata.distribution("detect-secrets")
    require(dist.version == SCANNER_VERSION, "SCANNER_VERSION_MISMATCH")
    members: dict[str, str] = {}
    for member in dist.files or []:
        name = str(member).replace("\\", "/")
        if name.startswith("detect_secrets/") and name.endswith(".py"):
            members[name] = digest(Path(str(dist.locate_file(member))).read_bytes())
    require(bool(members), "SCANNER_PROVENANCE_MISSING")
    return {"version": dist.version, "python_sources_sha256": digest(canonical(members))}


def configuration() -> dict[str, Any]:
    return {"collector": VERSION, "scanner": package_identity(),
            "python": list(sys.version_info[:3]), "utf8_mode": sys.flags.utf8_mode,
            "plugins": PLUGIN_CONFIG, "filters": [], "network_verification": False,
            "transformers": TRANSFORMS, "passes": "raw-plus-all-applicable",
            "dedup": "path-line-type-fingerprint", "line_mapping": "physical-source-lines-v1",
            "scope": "all-regular-tracked-head-blobs-v1",
            "encoding": "strict-utf8", "max_files": MAX_FILES, "max_file_bytes": MAX_FILE_BYTES,
            "max_total_bytes": MAX_TOTAL_BYTES, "max_output_bytes": MAX_OUTPUT_BYTES}


@contextlib.contextmanager
def engine() -> Iterator[tuple[list[Any], list[Any]]]:
    from detect_secrets.settings import get_plugins, transient_settings
    from detect_secrets.transformers.config import (
        ConfigFileTransformer,
        EagerConfigFileTransformer,
    )
    from detect_secrets.transformers.yaml import YAMLTransformer
    with transient_settings({"plugins_used": PLUGIN_CONFIG, "filters_used": []}) as settings:
        # No file skip, pragma suppression or remote verification; conservative policy.
        settings.filters.clear()
        plugins = sorted(get_plugins(), key=lambda obj: obj.__class__.__name__)
        actual = sorted([plugin.json() for plugin in plugins], key=lambda obj: obj["name"])
        require(actual == sorted(PLUGIN_CONFIG, key=lambda obj: obj["name"]), "PLUGIN_CONFIG_DRIFT")
        yield plugins, [YAMLTransformer(), ConfigFileTransformer(), EagerConfigFileTransformer()]


class NamedText(io.StringIO):
    def __init__(self, value: str, name: str):
        super().__init__(value)
        self.name = name


class MappedLines(list[str]):
    """A transformed view with an explicit physical source line for each row."""

    def __init__(self, lines: list[str], source_line_numbers: list[int]):
        super().__init__(lines)
        self.source_line_numbers = source_line_numbers


def line_numbers(lines: list[str]) -> list[int]:
    if isinstance(lines, MappedLines):
        return list(lines.source_line_numbers)
    return list(range(1, len(lines) + 1))


def yaml_source_lines(path: str, text: str, transformed: list[str]) -> MappedLines:
    """Replay the pinned YAML transformer's ordering without inventing locations.

    Its output includes padding rows and one row per distinct scalar, so multiple
    scalars on one source line do not necessarily occupy that index in the view.
    """
    from detect_secrets.transformers.yaml import YAMLFileParser
    from detect_secrets.types import NamedIO

    locations: list[int] = []
    seen = set()
    # NamedText supplies the text stream and name expected by the nominal NamedIO type.
    stream = cast(NamedIO, NamedText(text, path))
    for item in sorted(YAMLFileParser(stream), key=lambda value: value.line_number):
        if item in seen:
            continue
        seen.add(item)
        while len(locations) < item.line_number - 1:
            locations.append(len(locations) + 1)
        locations.append(item.line_number)
    require(len(locations) == len(transformed), "TRANSFORM_MAPPING_UNPROVEN")
    source_count = len(text.splitlines())
    require(all(type(number) is int and 1 <= number <= source_count for number in locations),
            "TRANSFORM_MAPPING_UNPROVEN")
    return MappedLines(transformed, locations)


def views(path: str, text: str, transformers: list[Any]) -> tuple[list[tuple[str, list[str]]], list[dict[str, str]]]:
    from detect_secrets.transformers.exceptions import ParsingError
    raw_lines = text.splitlines()
    result = [("raw", raw_lines)]
    attempts: list[dict[str, str]] = []
    for transformer in transformers:
        name = transformer.__class__.__name__
        if not transformer.should_parse_file(path):
            attempts.append({"name": name, "status": "NOT_APPLICABLE_TYPE"})
            continue
        try:
            transformed = transformer.parse_file(NamedText(text, path))
        except ParsingError:
            require(name != "YAMLTransformer", "REQUIRED_TRANSFORM_FAILED")
            attempts.append({"name": name, "status": "NOT_APPLICABLE_FORMAT"})
            continue
        require(isinstance(transformed, list) and all(isinstance(x, str) for x in transformed),
                "INVALID_TRANSFORM_OUTPUT")
        if name == "YAMLTransformer":
            transformed = yaml_source_lines(path, text, transformed)
        else:
            require(len(transformed) <= len(raw_lines), "TRANSFORM_MAPPING_UNPROVEN")
        require(len(transformed) <= MAX_LINES, "TRANSFORM_LINE_LIMIT")
        require(sum(len(x.encode("utf-8")) for x in transformed) <= MAX_FILE_BYTES, "TRANSFORM_SIZE_LIMIT")
        attempts.append({"name": name, "status": "PROCESSED"})
        result.append((name, transformed))
    return result, attempts


def scan_text(path: str, raw: bytes, plugins: list[Any], transformers: list[Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from detect_secrets.util.code_snippet import get_code_snippet
    text = raw.decode("utf-8", errors="strict")
    require(b"\0" not in raw, "UNSUPPORTED_INPUT")
    source_lines = text.splitlines()
    require(len(source_lines) <= MAX_LINES, "LINE_LIMIT")
    all_views, attempts = views(path, text, transformers)
    required = [plugin.__class__.__name__ for plugin in plugins]
    results: dict[tuple[int, str, str], dict[str, Any]] = {}
    passes: list[dict[str, Any]] = []
    for name, lines in all_views:
        work = lines or [""]  # Defined empty-input detector protocol.
        locations = line_numbers(lines)
        require(len(locations) == len(lines) and all(
            type(number) is int and 1 <= number <= len(source_lines) for number in locations
        ), "TRANSFORM_MAPPING_UNPROVEN")
        work_locations = locations or [1]
        completed = []
        for plugin in plugins:
            calls = 0
            for view_number, (number, line) in enumerate(zip(work_locations, work), 1):
                found = plugin.analyze_line(filename=path, line=line.rstrip(), line_number=number,
                                            context=get_code_snippet(work, view_number))
                require(found is not None, "DETECTOR_RETURN_INVALID")
                for secret in found:
                    require(secret.filename.replace("\\", "/") == path, "FINDING_PATH_MISMATCH")
                    require(secret.line_number == number, "FINDING_LINE_MISMATCH")
                    require(isinstance(secret.secret_value, str), "FINDING_VALUE_MISSING")
                    require(number <= len(source_lines) and secret.secret_value in source_lines[number - 1],
                            "TRANSFORM_LOCATION_UNPROVEN")
                    require(re.fullmatch(r"[0-9a-f]{40}", secret.secret_hash) is not None, "FINGERPRINT_INVALID")
                    require(secret.type == plugin.secret_type, "FINDING_TYPE_MISMATCH")
                    key = (number, secret.type, secret.secret_hash)
                    results[key] = {"path": path, "line": number, "type": secret.type,
                                    "fingerprint": secret.secret_hash}
                calls += 1  # Only after the iterator has been fully drained.
            completed.append({"name": plugin.__class__.__name__, "calls": calls})
        passes.append({"name": name, "view_sha256": digest(canonical(lines)),
                       "lines": len(lines), "line_numbers": locations, "detectors": completed})
    row = {"path": path, "input_status": "PROCESSED", "raw_sha256": digest(raw),
           "byte_length": len(raw), "source_lines": len(source_lines),
           "required_detectors": required, "required_passes": [x[0] for x in all_views],
           "passes": passes, "transform_attempts": attempts, "filter_decisions": [],
           "filter_decisions_digest": digest(canonical([]))}
    return row, [results[key] for key in sorted(results)]


def collect(root: Path, nonce: str) -> dict[str, Any]:
    require(re.fullmatch(r"[0-9a-f]{32}", nonce) is not None, "NONCE_INVALID")
    require(sys.flags.utf8_mode == 1, "UTF8_MODE_REQUIRED")
    before, blobs = snapshot(root)
    config = configuration()
    rows = []
    findings = []
    with engine() as (plugins, transformers):
        for item in before["inputs"]:
            row, discovered = scan_text(item["path"], blobs[item["path"]], plugins, transformers)
            row.update(mode=item["mode"], blob_oid=item["blob_oid"])
            rows.append(row)
            findings.extend(discovered)
    after, _ = snapshot(root)
    require(after == before and configuration() == config, "COLLECTION_DRIFT")
    receipt = {"schema_version": SCHEMA, "run_nonce": nonce, "source": before,
               "scope_policy": config["scope"], "config": config,
               "config_sha256": digest(canonical(config)),
               "inventory_sha256": digest(canonical(before["inputs"])),
               "processed_inputs": rows, "findings": findings, "completion": "COMPLETE"}
    require(len(canonical(receipt)) <= MAX_OUTPUT_BYTES, "OUTPUT_LIMIT")
    return receipt


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ScanError("INVALID_ARGUMENTS")


def main() -> int:
    parser = SafeArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--nonce", required=True)
    try:
        with controlled_errors():
            args = parser.parse_args()
    except ScanError:
        sys.stdout.write('{"error":"INVALID_ARGUMENTS"}')
        return 1
    logging.disable(logging.CRITICAL)
    try:
        with controlled_errors():
            with open(os.devnull, "w", encoding="utf-8") as sink, contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                value = collect(args.root.resolve(), args.nonce)
            sys.stdout.buffer.write(canonical(value))
            return 0
    except ScanError:
        sys.stdout.write('{"error":"COLLECTION_FAILED"}')
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
