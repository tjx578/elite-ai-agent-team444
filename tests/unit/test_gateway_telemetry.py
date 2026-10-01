"""Synthetic telemetry projection tests; no provider or logging is involved."""

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from wolf15_sentient.contracts.gateway_telemetry import (
    GatewayTelemetry,
    GatewayTelemetryMetric,
)
from wolf15_sentient.contracts.model_gateway import GatewayRequest
from wolf15_sentient.sentient.model_gateway import telemetry
from wolf15_sentient.sentient.model_gateway.canonical import (
    GatewayValidationError,
    canonical,
)
from wolf15_sentient.sentient.model_gateway.validation import validate_request

FIXTURES = Path(__file__).resolve().parents[2] / "docs/architecture/cp1/fixtures"


def sample() -> tuple[dict[str, Any], dict[str, Any]]:
    return tuple(
        json.loads((FIXTURES / f"{kind}.canonical.json").read_bytes())
        for kind in ("request", "response")
    )


def bind(request: dict[str, Any], response: dict[str, Any]) -> GatewayRequest:
    digest = sha256(canonical(request["envelope"])).hexdigest()
    request["gateway_digest_sha256"] = digest
    response["gateway_digest_sha256"] = digest
    return validate_request(canonical(request))


def test_all_free_text_canaries_are_excluded_from_projection() -> None:
    request, response = sample()
    envelope = request["envelope"]
    canaries: list[str] = []

    def canary(label: str) -> str:
        text = f"sensitive-canary-{label}"
        canaries.append(text)
        return text

    for field in (
        "provider_id",
        "adapter_version",
        "endpoint_id",
        "model_id",
        "requested_revision",
    ):
        envelope["provider"][field] = canary(field)
    envelope["provider"]["revision_status"] = "SUPPLIED_NOT_VERIFIED"
    profiles = [
        envelope[field]
        for field in ("technical_profile", "persona_profile", "policy_profile")
    ]
    profiles.append(envelope["limits"]["pricing_profile"])
    for index, profile in enumerate(profiles):
        for field in ("id", "version"):
            profile[field] = canary(f"profile-{index}-{field}")
    envelope["scope"]["data_scope_id"] = canary("data-scope")
    evidence_ref = canary("evidence-reference")
    envelope["evidence_refs"] = [evidence_ref]
    response["proposal"]["claims"][0]["evidence_refs"] = [evidence_ref]
    response["proposal"]["claims"][0]["text"] = canary("claim-text")
    response["proposal"]["summary"] = canary("summary")
    response["proposal"]["proposed_steps"] = [canary("step")]
    for field, status in (
        ("input_tokens", "MEASURED"),
        ("output_tokens", "ESTIMATED"),
        ("cost_microunits", "MEASURED"),
    ):
        response["usage"][field] = {
            "status": status,
            "value": 0,
            "method_version": canary(field),
        }
    result = telemetry.project_telemetry(bind(request, response), canonical(response))
    encoded = result.model_dump_json()
    assert all(value not in encoded for value in canaries)
    assert result.evidence_class == "WIRE_REPORTED_NOT_INDEPENDENTLY_MEASURED"
    assert result.input_tokens.status == "MEASURED"
    assert result.output_tokens.status == "ESTIMATED"
    assert result.cost_microunits.value == 0
    assert (
        result.provider_descriptor_sha256
        == sha256(canonical(envelope["provider"])).hexdigest()
    )
    assert (
        result.profiles.pricing_descriptor_sha256
        == sha256(canonical(profiles[-1])).hexdigest()
    )
    assert (
        result.output_tokens.method_version_sha256
        == sha256(
            canonical(
                {"method_version": response["usage"]["output_tokens"]["method_version"]}
            )
        ).hexdigest()
    )
    assert "host_elapsed_ms" not in result.model_dump()


def test_unmeasured_usage_is_preserved_and_nested_models_are_frozen() -> None:
    request, response = sample()
    result = telemetry.project_telemetry(bind(request, response), canonical(response))
    assert result.input_tokens.status == "NOT_MEASURED"
    assert result.input_tokens.value is None
    assert result.input_tokens.method_version_sha256 is None
    assert result.provider_reported_elapsed_ms == response["usage"]["elapsed_ms"]
    with pytest.raises(ValidationError):
        result.input_tokens.value = 1
    with pytest.raises(ValidationError):
        result.currency = "EUR"


@pytest.mark.parametrize("status", ["MEASURED", "ESTIMATED", "NOT_MEASURED"])
@pytest.mark.parametrize(
    "value,digest",
    [
        (None, None),
        (0, "a" * 64),
        (None, "a" * 64),
        (1, None),
        (True, "a" * 64),
        (1.0, "a" * 64),
    ],
)
def test_metric_shape_preserves_unknown_vs_reported(
    status: str, value: object, digest: str | None
) -> None:
    data = {"status": status, "value": value, "method_version_sha256": digest}
    valid = (status == "NOT_MEASURED" and value is None and digest is None) or (
        status != "NOT_MEASURED" and type(value) is int and digest is not None
    )
    if valid:
        assert GatewayTelemetryMetric.model_validate(data).model_dump() == data
    else:
        with pytest.raises(ValidationError):
            GatewayTelemetryMetric.model_validate(data)


def test_mutated_request_and_unbound_response_are_rejected() -> None:
    request, response = sample()
    model = bind(request, response)
    model.envelope.provider.model_id = "changed-sensitive-value"
    with pytest.raises(GatewayValidationError, match="GATEWAY_DIGEST"):
        telemetry.project_telemetry(model, canonical(response))
    model = bind(request, response)
    response["correlation"]["task_id"] = "00000000-0000-0000-0000-000000000099"
    with pytest.raises(GatewayValidationError, match="RESPONSE_BINDING"):
        telemetry.project_telemetry(model, canonical(response))


def test_invalid_mutation_does_not_emit_serializer_payload_warning(
    recwarn: pytest.WarningsRecorder, capsys: pytest.CaptureFixture[str]
) -> None:
    request, response = sample()
    model = bind(request, response)
    object.__setattr__(model.envelope.provider, "model_id", {"private-canary": 1})
    with pytest.raises(GatewayValidationError, match="SCHEMA_INVALID"):
        telemetry.project_telemetry(model, canonical(response))
    assert not recwarn
    captured = capsys.readouterr()
    assert captured.out == captured.err == ""


def test_projection_uses_detached_request_after_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, response = sample()
    original = bind(request, response)
    expected = sha256(canonical(original.envelope.provider.model_dump())).hexdigest()
    real_validate = telemetry.validate_response

    def mutate_original(raw: bytes, bound: GatewayRequest):
        original.envelope.provider.provider_id = "post-validation-sensitive-canary"
        return real_validate(raw, bound)

    monkeypatch.setattr(telemetry, "validate_response", mutate_original)
    result = telemetry.project_telemetry(original, canonical(response))
    assert result.provider_descriptor_sha256 == expected
    assert "post-validation-sensitive-canary" not in result.model_dump_json()


def test_unknown_fields_and_missing_fields_are_rejected() -> None:
    request, response = sample()
    model = bind(request, response)
    result = telemetry.project_telemetry(model, canonical(response)).model_dump()
    for key in result:
        incomplete = dict(result)
        del incomplete[key]
        with pytest.raises(ValidationError):
            GatewayTelemetry.model_validate(incomplete)
    result["raw_error"] = "sensitive-error-canary"
    with pytest.raises(ValidationError):
        GatewayTelemetry.model_validate(result)
    response["raw_error"] = "sensitive-error-canary"
    with pytest.raises(GatewayValidationError, match="SCHEMA_INVALID"):
        telemetry.project_telemetry(model, canonical(response))


@pytest.mark.parametrize(
    "status,code",
    [
        ("PROVIDER_FAILED", "TRANSPORT"),
        ("CANCELLED", "CANCELLED"),
        ("TIMED_OUT", "TIMEOUT"),
        ("REJECTED", "SCHEMA_INVALID"),
    ],
)
def test_failure_projection_contains_only_closed_code(status: str, code: str) -> None:
    request, response = sample()
    response.update(status=status, failure_code=code, proposal=None)
    result = telemetry.project_telemetry(bind(request, response), canonical(response))
    assert result.status == status
    assert result.failure_code == code
    assert result.execution_authorized is False
