"""Offline gateway schema and content binding, without authorization or dispatch."""
from __future__ import annotations

from hashlib import sha256

from pydantic import ValidationError

from wolf15_sentient.contracts.model_gateway import GatewayRequest, GatewayResponse
from wolf15_sentient.contracts.reasoning import ReasoningInput, ReasoningInvocation
from wolf15_sentient.reasoning.runtime import MAX_OUTPUT_BYTES, MAX_REQUEST_BYTES
from wolf15_sentient.sentient.model_gateway.canonical import (
    GatewayValidationError,
    canonical,
    parse_canonical,
)


def validate_request(raw: bytes, *, max_bytes: int = MAX_REQUEST_BYTES) -> GatewayRequest:
    """Check the wire envelope; hashes alone cannot approve a profile/provider."""
    value = parse_canonical(raw, max_bytes=max_bytes)
    try:
        request = GatewayRequest.model_validate(value)
    except ValidationError:
        raise GatewayValidationError("SCHEMA_INVALID") from None
    envelope = request.envelope
    if len(raw) > envelope.limits.max_request_bytes:
        raise GatewayValidationError("REQUEST_BYTE_LIMIT")
    if request.gateway_digest_sha256 != sha256(canonical(envelope.model_dump())).hexdigest():
        raise GatewayValidationError("GATEWAY_DIGEST")
    if envelope.limits.max_output_tokens > envelope.limits.max_context_tokens:
        raise GatewayValidationError("CONTEXT_RESERVATION")
    return request


def bind_reasoning_input(request: GatewayRequest, raw: bytes) -> ReasoningInvocation:
    """Bind supplied exact M3-A bytes; never fetch a URL or resolve model paths.

    Revalidation takes a fresh copy because returned Pydantic objects can be
    mutated by a caller. Existing M3-A serialization remains independent from
    gateway canonical JSON, including its original field order and defaults.
    """
    bound = validate_request(canonical(request.model_dump(warnings=False)))
    if type(raw) is not bytes or len(raw) > min(
        MAX_REQUEST_BYTES, bound.envelope.limits.max_request_bytes
    ):
        raise GatewayValidationError("REASONING_BYTE_LIMIT")
    correlation = bound.envelope.correlation
    if sha256(raw).hexdigest() != correlation.input_digest_sha256:
        raise GatewayValidationError("INPUT_DIGEST")
    try:
        prepared = ReasoningInput.model_validate_json(raw)
        invocation = ReasoningInvocation(input=prepared, input_digest_sha256=correlation.input_digest_sha256)
    except (ValidationError, ValueError, TypeError):
        raise GatewayValidationError("INVALID_REASONING_INVOCATION") from None
    if prepared.model_dump_json().encode("utf-8") != raw:
        raise GatewayValidationError("REASONING_BYTES_CHANGED")
    if (str(prepared.task_id), str(prepared.run_id), str(prepared.bundle_id)) != (
        correlation.task_id, correlation.run_id, correlation.bundle_id
    ):
        raise GatewayValidationError("INPUT_CORRELATION")
    if set(bound.envelope.evidence_refs) != {source.source_id for source in prepared.sources}:
        raise GatewayValidationError("INPUT_EVIDENCE_REFS")
    return invocation


def validate_response(raw: bytes, request: GatewayRequest,
                      *, max_bytes: int = MAX_OUTPUT_BYTES) -> GatewayResponse:
    """Validate echoed identity, references and receipt consistency, not truth.

    Claimed metering and elapsed time are checked for consistency only. This
    function cannot enforce a transport deadline, measure spend, or cancel work.
    """
    bound = validate_request(canonical(request.model_dump(warnings=False)))
    value = parse_canonical(raw, max_bytes=max_bytes)
    envelope = bound.envelope
    if len(raw) > envelope.limits.max_output_bytes:
        raise GatewayValidationError("OUTPUT_BYTE_LIMIT")
    try:
        response = GatewayResponse.model_validate(value)
    except ValidationError:
        raise GatewayValidationError("SCHEMA_INVALID") from None
    if (response.gateway_invocation_id != envelope.gateway_invocation_id
            or response.gateway_digest_sha256 != bound.gateway_digest_sha256
            or response.correlation != envelope.correlation):
        raise GatewayValidationError("RESPONSE_BINDING")
    if response.usage.currency != envelope.limits.currency:
        raise GatewayValidationError("CURRENCY_BINDING")
    if response.status == "PROPOSAL_VALIDATED":
        limits, usage = envelope.limits, response.usage
        for metric, upper_bound in (
            (usage.output_tokens, limits.max_output_tokens),
            (usage.input_tokens, limits.max_context_tokens - limits.max_output_tokens),
            (usage.cost_microunits, limits.cost_limit_microunits),
        ):
            if metric.status == "MEASURED" and metric.value is not None and metric.value > upper_bound:
                raise GatewayValidationError("SUCCESS_USAGE_EXCEEDS_LIMIT")
        if usage.elapsed_ms >= limits.timeout_ms:
            raise GatewayValidationError("SUCCESS_AFTER_DEADLINE")
    if response.proposal is not None:
        if response.proposal.input_digest_sha256 != envelope.correlation.input_digest_sha256:
            raise GatewayValidationError("PROPOSAL_BINDING")
        known = set(envelope.evidence_refs)
        if any(set(claim.evidence_refs) - known for claim in response.proposal.claims):
            raise GatewayValidationError("UNKNOWN_EVIDENCE_REF")
    return response
