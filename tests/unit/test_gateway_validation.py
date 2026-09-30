"""Offline wire and existing-input binding; no provider execution evidence."""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import pytest
from test_reasoning import request as reasoning_request

from wolf15_sentient.reasoning import prepare_reasoning
from wolf15_sentient.sentient.model_gateway.canonical import (
    MAX_SAFE_INTEGER,
    GatewayValidationError,
    canonical,
    parse_canonical,
)
from wolf15_sentient.sentient.model_gateway.validation import (
    bind_reasoning_input,
    validate_request,
    validate_response,
)

FIXTURES = Path(__file__).resolve().parents[2] / "docs/architecture/cp1/fixtures"


def fixture(name: str):
    return json.loads((FIXTURES / (name + ".canonical.json")).read_bytes())


def rebind(value):
    value["gateway_digest_sha256"] = sha256(canonical(value["envelope"])).hexdigest()
    return validate_request(canonical(value))


def test_exact_frozen_fixture_bytes():
    request_raw = (FIXTURES / "request.canonical.json").read_bytes()
    response_raw = (FIXTURES / "response.canonical.json").read_bytes()
    request = validate_request(request_raw)
    response = validate_response(response_raw, request)
    assert canonical(request.model_dump()) == request_raw
    assert canonical(response.model_dump()) == response_raw
    assert canonical(request.envelope.model_dump()) == (FIXTURES / "envelope.canonical.json").read_bytes()
    assert response.execution_authorized is False
    assert response.usage.cost_microunits.status == "NOT_MEASURED"
    assert response.usage.cost_microunits.value is None


@pytest.mark.parametrize("raw", [
    b'{"a":1,"a":2}', b'{"outer":{"a":1,"a":2}}', b'{ "a":1}', b'{"a":1}\n',
    b'{"a":1e0}', b'{"a":1.0}', b'{"a":NaN}', b'{"a":Infinity}',
    b'{"a":-0}', b'{"a":9007199254740992}', b'{"a":"\\ud800"}',
    b'"e\\u0301"', b'{"a":"\\/"}', b'"\\u0061"', b'\xef\xbb\xbf{}', b'\xff',
])
def test_invalid_or_noncanonical_bytes_are_rejected(raw):
    with pytest.raises(GatewayValidationError):
        parse_canonical(raw, max_bytes=1000)


@pytest.mark.parametrize("value", [1.0, float("nan"), (1, 2), {1: "x"}, {"é": "x"},
                                  MAX_SAFE_INTEGER + 1, -MAX_SAFE_INTEGER - 1])
def test_serializer_does_not_coerce_values(value):
    with pytest.raises(GatewayValidationError):
        canonical(value)


def test_canonical_unicode_integer_and_order_boundaries():
    value = {"z": [None, True, False, -MAX_SAFE_INTEGER, MAX_SAFE_INTEGER], "a": "é/\n"}
    raw = canonical(value)
    assert raw.startswith('{"a":"é/\\n","z":'.encode())
    assert parse_canonical(raw, max_bytes=len(raw)) == value
    with pytest.raises(GatewayValidationError, match="WIRE_BYTE_LIMIT"):
        parse_canonical(raw, max_bytes=len(raw)-1)


def test_request_digest_and_declared_limits():
    data = fixture("request")
    data["envelope"]["provider"]["model_id"] = "changed"
    with pytest.raises(GatewayValidationError, match="GATEWAY_DIGEST"):
        validate_request(canonical(data))
    data["envelope"]["limits"]["max_request_bytes"] = 1
    with pytest.raises(GatewayValidationError, match="REQUEST_BYTE_LIMIT"):
        rebind(data)
    data = fixture("request")
    data["envelope"]["limits"]["max_output_tokens"] = 4097
    with pytest.raises(GatewayValidationError, match="CONTEXT_RESERVATION"):
        rebind(data)


@pytest.mark.parametrize(("field", "value", "category"), [
    ("gateway_invocation_id", "00000000-0000-0000-0000-000000000009", "RESPONSE_BINDING"),
    ("gateway_digest_sha256", "a" * 64, "RESPONSE_BINDING"),
])
def test_response_cannot_bind_another_request(field, value, category):
    request = validate_request(canonical(fixture("request")))
    response = fixture("response")
    response[field] = value
    with pytest.raises(GatewayValidationError, match=category):
        validate_response(canonical(response), request)


@pytest.mark.parametrize(("metric", "value"), [("output_tokens", 513), ("input_tokens", 3585),
                                              ("cost_microunits", 1001)])
def test_success_receipt_cannot_exceed_measured_limits(metric, value):
    request = validate_request(canonical(fixture("request")))
    response = fixture("response")
    response["usage"][metric] = {"status": "MEASURED", "value": value, "method_version": "synthetic"}
    with pytest.raises(GatewayValidationError, match="SUCCESS_USAGE_EXCEEDS_LIMIT"):
        validate_response(canonical(response), request)


@pytest.mark.parametrize("fault", ["deadline", "currency", "proposal_digest", "evidence", "byte_limit"])
def test_response_consistency_failures(fault):
    request_data, response = fixture("request"), fixture("response")
    expected = {"deadline": "SUCCESS_AFTER_DEADLINE", "currency": "CURRENCY_BINDING",
                "proposal_digest": "PROPOSAL_BINDING", "evidence": "UNKNOWN_EVIDENCE_REF",
                "byte_limit": "OUTPUT_BYTE_LIMIT"}[fault]
    if fault == "deadline":
        response["usage"]["elapsed_ms"] = 1000
    elif fault == "currency":
        response["usage"]["currency"] = "EUR"
    elif fault == "proposal_digest":
        response["proposal"]["input_digest_sha256"] = "a" * 64
    elif fault == "evidence":
        response["proposal"]["claims"][0]["evidence_refs"] = ["unknown"]
    else:
        request_data["envelope"]["limits"]["max_output_bytes"] = 1
    request = rebind(request_data)
    response["gateway_digest_sha256"] = request.gateway_digest_sha256
    with pytest.raises(GatewayValidationError, match=expected):
        validate_response(canonical(response), request)


def bound_input():
    prepared = prepare_reasoning(reasoning_request())
    raw = prepared.model_dump_json().encode("utf-8")
    data = fixture("request")
    data["envelope"]["correlation"]["input_digest_sha256"] = sha256(raw).hexdigest()
    data["envelope"]["evidence_refs"] = [source.source_id for source in prepared.sources]
    return rebind(data), raw


def test_existing_reasoning_serialization_is_preserved_exactly():
    request, raw = bound_input()
    invocation = bind_reasoning_input(request, raw)
    assert invocation.input.model_dump_json().encode("utf-8") == raw
    assert invocation.input_digest_sha256 == sha256(raw).hexdigest()
    # The existing M3-A order differs from gateway canonical order. Do not migrate it silently.
    assert canonical(json.loads(raw)) != raw


@pytest.mark.parametrize("fault", ["bytes", "correlation", "evidence", "reordered"])
def test_reasoning_binding_rejects_substitution(fault):
    request, raw = bound_input()
    data = request.model_dump()
    if fault == "bytes":
        raw += b" "
    elif fault == "correlation":
        data["envelope"]["correlation"]["task_id"] = "00000000-0000-0000-0000-000000000009"
    elif fault == "evidence":
        data["envelope"]["evidence_refs"] = ["unknown"]
    else:
        raw = canonical(json.loads(raw))
        data["envelope"]["correlation"]["input_digest_sha256"] = sha256(raw).hexdigest()
    with pytest.raises(GatewayValidationError):
        bind_reasoning_input(rebind(data), raw)


def test_mutated_request_is_revalidated_before_binding():
    request, raw = bound_input()
    request.envelope.provider.model_id = "changed-after-validation"
    with pytest.raises(GatewayValidationError, match="GATEWAY_DIGEST"):
        bind_reasoning_input(request, raw)


@pytest.mark.parametrize("fault", ["missing_default", "trimmed_intent", "duplicate_key"])
def test_old_input_contract_cannot_normalize_supplied_bytes(fault):
    request, raw = bound_input()
    value = json.loads(raw)
    if fault == "missing_default":
        del value["authority"]
        raw = json.dumps(value, separators=(",", ":")).encode()
    elif fault == "trimmed_intent":
        value["intent"] = " " + value["intent"] + " "
        raw = json.dumps(value, separators=(",", ":")).encode()
    else:
        raw = b'{"authority":"READ_ONLY",' + raw[1:]
    data = request.model_dump()
    data["envelope"]["correlation"]["input_digest_sha256"] = sha256(raw).hexdigest()
    with pytest.raises(GatewayValidationError, match="INVALID_REASONING_INVOCATION"):
        bind_reasoning_input(rebind(data), raw)
