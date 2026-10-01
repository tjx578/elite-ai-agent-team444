"""The frozen cp1-json-integer-nfc-v0 profile, not general RFC 8785 JSON."""
from __future__ import annotations

import json
import unicodedata
from typing import Any

MAX_SAFE_INTEGER = 9007199254740991


class GatewayValidationError(ValueError):
    """Fixed validation category without arbitrary input or exception payloads."""


def _inspect(value: Any) -> None:
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > MAX_SAFE_INTEGER:
            raise GatewayValidationError("INTEGER_RANGE")
        return
    if type(value) is str:
        value.encode("utf-8", errors="strict")
        if unicodedata.normalize("NFC", value) != value:
            raise GatewayValidationError("NON_NFC")
        return
    if type(value) is list:
        for item in value:
            _inspect(item)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or not key.isascii():
                raise GatewayValidationError("NON_ASCII_KEY")
            _inspect(item)
        return
    raise GatewayValidationError("NON_INTEGER_NUMBER_OR_NON_JSON_TYPE")


def canonical(value: Any) -> bytes:
    """Reject unsupported values; never normalize, trim, or insert defaults."""
    try:
        _inspect(value)
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (UnicodeError, RecursionError):
        raise GatewayValidationError("INVALID_UNICODE_OR_NESTING") from None


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise GatewayValidationError("DUPLICATE_KEY")
        result[key] = value
    return result


def parse_canonical(raw: bytes, *, max_bytes: int) -> Any:
    """Parse bounded exact bytes and require byte-for-byte canonical identity."""
    if type(raw) is not bytes or type(max_bytes) is not int or max_bytes < 1:
        raise GatewayValidationError("INVALID_WIRE_ARGUMENT")
    if len(raw) > max_bytes:
        raise GatewayValidationError("WIRE_BYTE_LIMIT")
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs)
    except GatewayValidationError:
        raise
    except (ValueError, UnicodeError, RecursionError):
        raise GatewayValidationError("INVALID_JSON_BYTES") from None
    if canonical(value) != raw:
        raise GatewayValidationError("NON_CANONICAL_BYTES")
    return value
