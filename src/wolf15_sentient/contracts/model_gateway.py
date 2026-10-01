"""Strict CP1 wire shapes; canonical bytes and cross-binding belong to the gateway.

These models neither select a provider nor grant runtime authority. Every wire
field is required. Use the gateway canonical parser before validating wire bytes;
Pydantic JSON parsing alone does not reject duplicate keys or noncanonical bytes.
"""

from typing import Annotated, Literal, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)


def _untrimmed(value: str) -> str:
    if value != value.strip():
        raise ValueError("wire text must not have surrounding whitespace")
    return value


def _integer_literal(value: object) -> object:
    if type(value) is not int:
        raise ValueError("integer literal requires an integer")
    return value


def _false_literal(value: object) -> object:
    if type(value) is not bool:
        raise ValueError("boolean literal requires a boolean")
    return value


# AfterValidator operates only after strict string validation.
WireIdentifier = Annotated[
    str, StringConstraints(min_length=1, max_length=256), AfterValidator(_untrimmed)
]
WireText = Annotated[
    str, StringConstraints(min_length=1, max_length=8192), AfterValidator(_untrimmed)
]
WireSha256 = Annotated[
    str, StringConstraints(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")
]
WireUuid = Annotated[
    str,
    StringConstraints(
        min_length=36,
        max_length=36,
        pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
    ),
]
WireCurrency = Annotated[
    str, StringConstraints(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
]
SafeCount = Annotated[int, Field(ge=0, le=9007199254740991)]
PositiveCount = Annotated[int, Field(ge=1, le=9007199254740991)]
FalseOnly = Annotated[Literal[False], BeforeValidator(_false_literal)]
OneOnly = Annotated[Literal[1], BeforeValidator(_integer_literal)]
ZeroOnly = Annotated[Literal[0], BeforeValidator(_integer_literal)]


class _WireModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, revalidate_instances="always"
    )


class GatewayProfile(_WireModel):
    id: WireIdentifier
    version: WireIdentifier
    sha256: WireSha256


class GatewayCorrelation(_WireModel):
    task_id: WireUuid
    run_id: WireUuid
    bundle_id: WireUuid
    input_digest_sha256: WireSha256


class GatewayProvider(_WireModel):
    provider_id: WireIdentifier
    adapter_version: WireIdentifier
    endpoint_id: WireIdentifier
    model_id: WireIdentifier
    requested_revision: WireIdentifier | None
    revision_status: Literal["SUPPLIED_NOT_VERIFIED", "NOT_VERIFIED"]

    @model_validator(mode="after")
    def revision_pair(self) -> Self:
        if (self.revision_status == "NOT_VERIFIED") != (
            self.requested_revision is None
        ):
            raise ValueError("revision status and supplied revision disagree")
        return self


class GatewayScope(_WireModel):
    authority: Literal["READ_ONLY"]
    capabilities: Annotated[list[str], Field(min_length=0, max_length=0)]
    data_scope_id: WireIdentifier
    memory_writes_enabled: FalseOnly
    scheduler_enabled: FalseOnly
    repository_mutation_enabled: FalseOnly
    deployment_enabled: FalseOnly
    capability_activation_enabled: FalseOnly
    ree_activation_enabled: FalseOnly


class GatewayLimits(_WireModel):
    timeout_ms: PositiveCount
    max_request_bytes: PositiveCount
    max_output_bytes: PositiveCount
    max_context_tokens: PositiveCount
    max_output_tokens: PositiveCount
    max_requests: OneOnly
    max_retries: ZeroOnly
    cost_limit_microunits: SafeCount
    currency: WireCurrency
    pricing_profile: GatewayProfile


class GatewayOutputContract(_WireModel):
    schema_id: Literal["m3a-v0"]
    schema_sha256: WireSha256
    mode: Literal["NATIVE_JSON_SCHEMA"]
    required_capabilities: Annotated[list[str], Field(min_length=1, max_length=1)]

    @model_validator(mode="after")
    def output_capability(self) -> Self:
        if self.required_capabilities != ["JSON_SCHEMA_OUTPUT"]:
            raise ValueError("native JSON schema output is required")
        return self


class GatewayEnvelope(_WireModel):
    schema_version: Literal["cp1-gateway-draft-v0"]
    gateway_invocation_id: WireUuid
    correlation: GatewayCorrelation
    reasoning_schema_version: Literal["m3a-v0"]
    evidence_refs: Annotated[list[WireIdentifier], Field(max_length=32)]
    provider: GatewayProvider
    technical_profile: GatewayProfile
    persona_profile: GatewayProfile
    policy_profile: GatewayProfile
    scope: GatewayScope
    limits: GatewayLimits
    output_contract: GatewayOutputContract

    @model_validator(mode="after")
    def unique_references(self) -> Self:
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise ValueError("envelope evidence references must be unique")
        return self


class GatewayRequest(_WireModel):
    kind: Literal["REQUEST"]
    envelope: GatewayEnvelope
    gateway_digest_sha256: WireSha256


class GatewayClaim(_WireModel):
    text: WireText
    evidence_status: Literal["SOURCE_CLAIM", "ASSUMPTION", "NOT_MEASURED"]
    evidence_refs: Annotated[list[WireIdentifier], Field(max_length=32)]

    @model_validator(mode="after")
    def source_reference(self) -> Self:
        if self.evidence_status == "SOURCE_CLAIM" and not self.evidence_refs:
            raise ValueError("source claims require evidence references")
        return self


class GatewayProposal(_WireModel):
    schema_version: Literal["m3a-v0"]
    input_digest_sha256: WireSha256
    summary: WireText
    claims: Annotated[list[GatewayClaim], Field(max_length=32)]
    proposed_steps: Annotated[list[WireText], Field(max_length=32)]


class GatewayMetric(_WireModel):
    status: Literal["MEASURED", "ESTIMATED", "NOT_MEASURED"]
    value: SafeCount | None
    method_version: WireIdentifier | None

    @model_validator(mode="after")
    def measurement_pair(self) -> Self:
        if self.status == "NOT_MEASURED":
            if self.value is not None or self.method_version is not None:
                raise ValueError("unmeasured metrics require explicit nulls")
        elif self.value is None or self.method_version is None:
            raise ValueError("measured and estimated metrics require value and method")
        return self


class GatewayUsage(_WireModel):
    input_tokens: GatewayMetric
    output_tokens: GatewayMetric
    cost_microunits: GatewayMetric
    currency: WireCurrency
    elapsed_ms: SafeCount


class GatewayResponse(_WireModel):
    kind: Literal["RESPONSE"]
    schema_version: Literal["cp1-gateway-draft-v0"]
    gateway_invocation_id: WireUuid
    gateway_digest_sha256: WireSha256
    correlation: GatewayCorrelation
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
    proposal: GatewayProposal | None
    execution_authorized: FalseOnly
    validation_scope: Literal["SCHEMA_BINDING_AND_REFERENCES_ONLY"]
    usage: GatewayUsage

    @model_validator(mode="after")
    def outcome_pair(self) -> Self:
        if self.status == "PROPOSAL_VALIDATED":
            if self.proposal is None or self.failure_code is not None:
                raise ValueError(
                    "successful responses require a proposal and no failure"
                )
        elif self.proposal is not None or self.failure_code is None:
            raise ValueError("unsuccessful responses require a failure and no proposal")
        if (self.status == "CANCELLED") != (self.failure_code == "CANCELLED"):
            raise ValueError("cancellation status and code must agree")
        if (self.status == "TIMED_OUT") != (self.failure_code == "TIMEOUT"):
            raise ValueError("timeout status and code must agree")
        return self
