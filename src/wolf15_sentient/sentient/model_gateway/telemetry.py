"""Project fresh validated wire data to an allowlist, with no logging or sinks.

Descriptor digests bind exact canonical descriptors; they do not anonymize
low-entropy values or establish approval. Do not treat the projection as safe
for publication without a separate disclosure policy.
"""

from hashlib import sha256

from wolf15_sentient.contracts.gateway_telemetry import (
    GatewayTelemetry,
    GatewayTelemetryMetric,
    GatewayTelemetryProfiles,
)
from wolf15_sentient.contracts.model_gateway import GatewayMetric, GatewayRequest
from wolf15_sentient.sentient.model_gateway.canonical import canonical
from wolf15_sentient.sentient.model_gateway.validation import (
    validate_request,
    validate_response,
)


def _metric(metric: GatewayMetric) -> GatewayTelemetryMetric:
    return GatewayTelemetryMetric(
        status=metric.status,
        value=metric.value,
        method_version_sha256=(
            None
            if metric.method_version is None
            else sha256(
                canonical({"method_version": metric.method_version})
            ).hexdigest()
        ),
    )


def project_telemetry(request: GatewayRequest, raw_response: bytes) -> GatewayTelemetry:
    """Revalidate a detached request and raw response before projecting values."""
    # Revalidation rejects mutated shapes; serializer warnings can contain raw
    # field values and must not become an unintended telemetry/logging sink.
    bound = validate_request(canonical(request.model_dump(warnings=False)))
    response = validate_response(raw_response, bound)
    envelope = bound.envelope
    provider = envelope.provider
    correlation = envelope.correlation
    return GatewayTelemetry(
        schema_version="cp1-gateway-telemetry-v0",
        evidence_class="WIRE_REPORTED_NOT_INDEPENDENTLY_MEASURED",
        gateway_invocation_id=envelope.gateway_invocation_id,
        gateway_digest_sha256=bound.gateway_digest_sha256,
        task_id=correlation.task_id,
        run_id=correlation.run_id,
        bundle_id=correlation.bundle_id,
        input_digest_sha256=correlation.input_digest_sha256,
        provider_descriptor_sha256=sha256(canonical(provider.model_dump())).hexdigest(),
        model_descriptor_sha256=sha256(
            canonical(
                {
                    "provider_id": provider.provider_id,
                    "model_id": provider.model_id,
                    "requested_revision": provider.requested_revision,
                    "revision_status": provider.revision_status,
                }
            )
        ).hexdigest(),
        profiles=GatewayTelemetryProfiles(
            technical_descriptor_sha256=sha256(
                canonical(envelope.technical_profile.model_dump())
            ).hexdigest(),
            persona_descriptor_sha256=sha256(
                canonical(envelope.persona_profile.model_dump())
            ).hexdigest(),
            policy_descriptor_sha256=sha256(
                canonical(envelope.policy_profile.model_dump())
            ).hexdigest(),
            pricing_descriptor_sha256=sha256(
                canonical(envelope.limits.pricing_profile.model_dump())
            ).hexdigest(),
        ),
        status=response.status,
        failure_code=response.failure_code,
        execution_authorized=False,
        input_tokens=_metric(response.usage.input_tokens),
        output_tokens=_metric(response.usage.output_tokens),
        cost_microunits=_metric(response.usage.cost_microunits),
        currency=response.usage.currency,
        provider_reported_elapsed_ms=response.usage.elapsed_ms,
    )
