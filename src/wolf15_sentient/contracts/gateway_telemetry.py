"""Allowlisted in-memory telemetry; reported usage is not independent metering."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, model_validator

from wolf15_sentient.contracts.model_gateway import (
    FalseOnly,
    SafeCount,
    WireCurrency,
    WireSha256,
    WireUuid,
)


class _TelemetryModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, frozen=True, revalidate_instances="always"
    )


class GatewayTelemetryMetric(_TelemetryModel):
    status: Literal["MEASURED", "ESTIMATED", "NOT_MEASURED"]
    value: SafeCount | None
    method_version_sha256: WireSha256 | None

    @model_validator(mode="after")
    def measurement_pair(self) -> Self:
        if self.status == "NOT_MEASURED":
            if self.value is not None or self.method_version_sha256 is not None:
                raise ValueError("unmeasured metrics require explicit nulls")
        elif self.value is None or self.method_version_sha256 is None:
            raise ValueError("reported metrics require value and method digest")
        return self


class GatewayTelemetryProfiles(_TelemetryModel):
    technical_descriptor_sha256: WireSha256
    persona_descriptor_sha256: WireSha256
    policy_descriptor_sha256: WireSha256
    pricing_descriptor_sha256: WireSha256


class GatewayTelemetry(_TelemetryModel):
    schema_version: Literal["cp1-gateway-telemetry-v0"]
    evidence_class: Literal["WIRE_REPORTED_NOT_INDEPENDENTLY_MEASURED"]
    gateway_invocation_id: WireUuid
    gateway_digest_sha256: WireSha256
    task_id: WireUuid
    run_id: WireUuid
    bundle_id: WireUuid
    input_digest_sha256: WireSha256
    provider_descriptor_sha256: WireSha256
    model_descriptor_sha256: WireSha256
    profiles: GatewayTelemetryProfiles
    status: Literal[
        "PROPOSAL_VALIDATED", "REJECTED", "PROVIDER_FAILED", "CANCELLED", "TIMED_OUT"
    ]
    failure_code: (
        Literal[
            "AUTH",
            "RATE_LIMIT",
            "POLICY",
            "TRANSPORT",
            "TIMEOUT",
            "CANCELLED",
            "BUDGET_EXCEEDED",
            "BUDGET_NOT_MEASURED",
            "OUTPUT_LIMIT",
            "SCHEMA_INVALID",
            "BINDING_MISMATCH",
            "UNKNOWN_EVIDENCE_REF",
            "CONTEXT_LIMIT",
            "UNSUPPORTED_MODE",
        ]
        | None
    )
    execution_authorized: FalseOnly
    input_tokens: GatewayTelemetryMetric
    output_tokens: GatewayTelemetryMetric
    cost_microunits: GatewayTelemetryMetric
    currency: WireCurrency
    provider_reported_elapsed_ms: SafeCount

    @model_validator(mode="after")
    def outcome_pair(self) -> Self:
        if (self.status == "PROPOSAL_VALIDATED") != (self.failure_code is None):
            raise ValueError("telemetry status and failure disagree")
        if (self.status == "CANCELLED") != (self.failure_code == "CANCELLED"):
            raise ValueError("cancellation status and code must agree")
        if (self.status == "TIMED_OUT") != (self.failure_code == "TIMEOUT"):
            raise ValueError("timeout status and code must agree")
        return self
