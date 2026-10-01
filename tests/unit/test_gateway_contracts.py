"""Offline shape validation; fixtures confer no provider or runtime approval."""

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from wolf15_sentient.contracts.model_gateway import GatewayRequest, GatewayResponse
from wolf15_sentient.contracts.reasoning import ReasoningProposal

FIXTURES = Path(__file__).resolve().parents[2] / "docs/architecture/cp1/fixtures"


def fixture(kind: str) -> dict[str, Any]:
    return json.loads((FIXTURES / f"{kind}.canonical.json").read_bytes())


def validate(value: dict[str, Any]) -> GatewayRequest | GatewayResponse:
    model = GatewayRequest if value["kind"] == "REQUEST" else GatewayResponse
    return model.model_validate(value)


def objects(value: Any, path: tuple[str | int, ...] = ()):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from objects(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from objects(child, (*path, index))


def at(value: Any, path: tuple[str | int, ...]) -> Any:
    for key in path:
        value = value[key]
    return value


@pytest.mark.parametrize("kind", ["request", "response"])
def test_fixture_values_are_preserved(kind: str) -> None:
    value = fixture(kind)
    assert validate(value).model_dump(mode="json") == value


@pytest.mark.parametrize("kind", ["request", "response"])
def test_every_object_rejects_missing_and_extra_fields(kind: str) -> None:
    original = fixture(kind)
    model = GatewayRequest if kind == "request" else GatewayResponse
    for path, obj in objects(original):
        for key in obj:
            value = copy.deepcopy(original)
            del at(value, path)[key]
            with pytest.raises(ValidationError):
                model.model_validate(value)
        value = copy.deepcopy(original)
        at(value, path)["unexpected"] = None
        with pytest.raises(ValidationError):
            model.model_validate(value)


@pytest.mark.parametrize("bad", [0, 1, True, "false", None])
def test_false_literals_reject_non_boolean_values(bad: object) -> None:
    value = fixture("request")
    scope = value["envelope"]["scope"]
    for key in scope:
        if key.endswith("_enabled"):
            mutated = copy.deepcopy(value)
            mutated["envelope"]["scope"][key] = bad
            with pytest.raises(ValidationError):
                validate(mutated)
    response = fixture("response")
    response["execution_authorized"] = bad
    with pytest.raises(ValidationError):
        validate(response)


@pytest.mark.parametrize(
    "field", ["max_requests", "max_retries", "timeout_ms", "cost_limit_microunits"]
)
@pytest.mark.parametrize("bad", [True, False, 1.0, "1", -1, 9007199254740992])
def test_limits_reject_coercion_and_out_of_range(field: str, bad: object) -> None:
    value = fixture("request")
    value["envelope"]["limits"][field] = bad
    with pytest.raises(ValidationError):
        validate(value)


@pytest.mark.parametrize(
    "path,bad",
    [
        (("envelope", "provider", "provider_id"), " padded"),
        (("envelope", "provider", "model_id"), "trailing\n"),
        (("envelope", "provider", "model_id"), ""),
        (("envelope", "provider", "model_id"), "x" * 257),
        (("envelope", "gateway_invocation_id"), "A" * 36),
        (("envelope", "gateway_invocation_id"), "0" * 35),
        (("envelope", "technical_profile", "sha256"), "A" * 64),
        (("envelope", "technical_profile", "sha256"), "a" * 64 + "\n"),
        (("envelope", "limits", "currency"), "usd"),
        (("envelope", "scope", "capabilities"), ["READ"]),
        (("envelope", "output_contract", "required_capabilities"), ["OTHER"]),
        (("envelope", "evidence_refs"), ["duplicate", "duplicate"]),
        (("envelope", "evidence_refs"), [f"ref-{n}" for n in range(33)]),
    ],
)
def test_request_wire_constraints(path: tuple[str, ...], bad: object) -> None:
    value = fixture("request")
    at(value, path[:-1])[path[-1]] = bad
    with pytest.raises(ValidationError):
        validate(value)


@pytest.mark.parametrize(
    "status,revision,valid",
    [
        ("NOT_VERIFIED", None, True),
        ("NOT_VERIFIED", "revision", False),
        ("SUPPLIED_NOT_VERIFIED", "revision", True),
        ("SUPPLIED_NOT_VERIFIED", None, False),
        ("SUPPLIED_NOT_VERIFIED", " revision", False),
    ],
)
def test_provider_revision_pair(status: str, revision: str | None, valid: bool) -> None:
    value = fixture("request")
    value["envelope"]["provider"].update(
        revision_status=status, requested_revision=revision
    )
    if valid:
        assert validate(value).model_dump(mode="json") == value
    else:
        with pytest.raises(ValidationError):
            validate(value)


@pytest.mark.parametrize("status", ["MEASURED", "ESTIMATED", "NOT_MEASURED"])
@pytest.mark.parametrize(
    "number,method",
    [(None, None), (0, "v1"), (None, "v1"), (1, None), (True, "v1"), (1.0, "v1")],
)
def test_metric_pair(status: str, number: object, method: str | None) -> None:
    value = fixture("response")
    value["usage"]["input_tokens"] = {
        "status": status,
        "value": number,
        "method_version": method,
    }
    valid = (status == "NOT_MEASURED" and number is None and method is None) or (
        status != "NOT_MEASURED" and type(number) is int and method is not None
    )
    if valid:
        assert validate(value).model_dump(mode="json") == value
    else:
        with pytest.raises(ValidationError):
            validate(value)


@pytest.mark.parametrize(
    "status",
    ["PROPOSAL_VALIDATED", "REJECTED", "PROVIDER_FAILED", "CANCELLED", "TIMED_OUT"],
)
@pytest.mark.parametrize("code", [None, "AUTH", "CANCELLED", "TIMEOUT"])
def test_status_failure_pair(status: str, code: str | None) -> None:
    value = fixture("response")
    value.update(status=status, failure_code=code)
    if status != "PROPOSAL_VALIDATED":
        value["proposal"] = None
    valid = (
        (status == "PROPOSAL_VALIDATED" and code is None)
        or (status in {"REJECTED", "PROVIDER_FAILED"} and code == "AUTH")
        or (status == "CANCELLED" and code == "CANCELLED")
        or (status == "TIMED_OUT" and code == "TIMEOUT")
    )
    if valid:
        validate(value)
    else:
        with pytest.raises(ValidationError):
            validate(value)


def test_claim_and_proposal_constraints_preserve_m3a_compatibility() -> None:
    value = fixture("response")
    assert ReasoningProposal.model_validate(value["proposal"])
    value["proposal"]["claims"][0]["evidence_refs"] = []
    with pytest.raises(ValidationError):
        validate(value)
    value["proposal"]["claims"][0]["evidence_status"] = "ASSUMPTION"
    validate(value)
    value["proposal"]["summary"] = " padded"
    with pytest.raises(ValidationError):
        validate(value)


def test_tuple_arrays_and_mutated_model_instances_are_rejected() -> None:
    value = fixture("request")
    value["envelope"]["evidence_refs"] = ("ref",)
    with pytest.raises(ValidationError):
        validate(value)
    model = GatewayRequest.model_validate(fixture("request"))
    model.envelope.evidence_refs.extend(["duplicate", "duplicate"])
    with pytest.raises(ValidationError):
        GatewayRequest.model_validate(model)


@pytest.mark.parametrize("field", ["summary", "proposed_steps", "claims"])
def test_proposal_size_boundaries(field: str) -> None:
    value = fixture("response")
    proposal = value["proposal"]
    if field == "summary":
        proposal[field] = "x" * 8192
    elif field == "proposed_steps":
        proposal[field] = ["step"] * 32
    else:
        proposal[field] *= 32
    validate(value)
    proposal[field] += "x" if field == "summary" else [proposal[field][0]]
    with pytest.raises(ValidationError):
        validate(value)


def test_success_and_failure_cannot_exchange_proposal_presence() -> None:
    value = fixture("response")
    value.update(status="PROVIDER_FAILED", failure_code="AUTH")
    with pytest.raises(ValidationError):
        validate(value)
    value.update(status="PROPOSAL_VALIDATED", failure_code=None, proposal=None)
    with pytest.raises(ValidationError):
        validate(value)


def test_claim_reference_duplicates_are_permitted_by_frozen_schema() -> None:
    value = fixture("response")
    value["proposal"]["claims"][0]["evidence_refs"] *= 2
    assert validate(value).model_dump(mode="json") == value
