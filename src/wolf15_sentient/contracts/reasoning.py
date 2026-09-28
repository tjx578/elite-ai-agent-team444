"""M3-A proposals are untrusted data, never execution decisions."""

from enum import StrEnum
from hashlib import sha256
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, StringConstraints, model_validator

from wolf15_sentient.contracts.evidence import (
    EvidenceContextInput,
    EvidenceContextResult,
    Sha256,
    SuppliedSource,
)
from wolf15_sentient.contracts.models import (
    Authority,
    IntentText,
    NonBlankText,
    ProjectMode,
    RepositoryReference,
    StrictContract,
)

BoundedText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=8192)
]


class TaskKind(StrEnum):
    CONVERSATION = "CONVERSATION"
    RESEARCH = "RESEARCH"
    ENGINEERING = "ENGINEERING"
    INCIDENT = "INCIDENT"


class ReasoningRequest(StrictContract):
    intent: IntentText
    evidence: EvidenceContextInput
    repository: RepositoryReference | None = None
    task_kind: TaskKind | None = None
    authority: Literal[Authority.READ_ONLY] = Authority.READ_ONLY


class TaskRoute(StrictContract):
    task_kind: TaskKind
    reason: NonBlankText
    project_mode: ProjectMode | None = None

    @model_validator(mode="after")
    def engineering_mode_only(self) -> "TaskRoute":
        if (self.task_kind is TaskKind.ENGINEERING) != (self.project_mode is not None):
            raise ValueError("only engineering routes require a project mode")
        return self


class ReasoningInput(StrictContract):
    schema_version: Literal["m3a-v0"] = "m3a-v0"
    task_id: UUID
    run_id: UUID
    bundle_id: UUID
    intent: IntentText
    repository: RepositoryReference | None = None
    route: TaskRoute
    authority: Literal[Authority.READ_ONLY] = Authority.READ_ONLY
    context: EvidenceContextResult
    sources: list[SuppliedSource]
    source_policy: Literal["UNTRUSTED_DATA_ONLY"] = "UNTRUSTED_DATA_ONLY"
    limitations: list[NonBlankText]

    @model_validator(mode="after")
    def validate_context_binding(self) -> "ReasoningInput":
        bundle = self.context.bundle
        if bundle is not None and (self.task_id, self.run_id, self.bundle_id) != (
            bundle.task_id,
            bundle.run_id,
            bundle.bundle_id,
        ):
            raise ValueError("context correlation does not match reasoning input")
        return self


class ReasoningInvocation(StrictContract):
    input_digest_sha256: Sha256
    input: ReasoningInput

    @model_validator(mode="after")
    def validate_digest(self) -> "ReasoningInvocation":
        if (
            sha256(self.input.model_dump_json().encode("utf-8")).hexdigest()
            != self.input_digest_sha256
        ):
            raise ValueError("input digest does not match invocation")
        return self


class ProposedClaim(StrictContract):
    text: BoundedText
    evidence_status: Literal["SOURCE_CLAIM", "ASSUMPTION", "NOT_MEASURED"]
    evidence_refs: list[NonBlankText] = Field(default_factory=list, max_length=32)

    @model_validator(mode="after")
    def source_claim_requires_reference(self) -> "ProposedClaim":
        if self.evidence_status == "SOURCE_CLAIM" and not self.evidence_refs:
            raise ValueError("source claims require references")
        return self


class ReasoningProposal(StrictContract):
    """Provider output cannot supply authority, validation, or execution state."""

    schema_version: Literal["m3a-v0"] = "m3a-v0"
    input_digest_sha256: Sha256
    summary: BoundedText
    claims: list[ProposedClaim] = Field(default_factory=list, max_length=32)
    proposed_steps: list[BoundedText] = Field(default_factory=list, max_length=32)


class ReasoningResult(StrictContract):
    input: ReasoningInput
    input_digest_sha256: Sha256
    adapter_id: NonBlankText
    evidence_class: Literal["STUB", "OFFLINE_ADAPTER"]
    status: Literal["PROPOSAL_VALIDATED", "REJECTED", "ADAPTER_FAILED"]
    validation_scope: Literal["SCHEMA_BINDING_AND_REFERENCES_ONLY"] = (
        "SCHEMA_BINDING_AND_REFERENCES_ONLY"
    )
    execution_authorized: Literal[False] = False
    issues: list[NonBlankText]
    proposal: ReasoningProposal | None = None

    @model_validator(mode="after")
    def validate_outcome(self) -> "ReasoningResult":
        if (
            sha256(self.input.model_dump_json().encode("utf-8")).hexdigest()
            != self.input_digest_sha256
        ):
            raise ValueError("input digest does not match result")
        if self.status == "PROPOSAL_VALIDATED":
            if self.proposal is None or self.issues:
                raise ValueError("validated result requires a proposal without issues")
            if self.proposal.input_digest_sha256 != self.input_digest_sha256:
                raise ValueError("proposal must bind to result input")
        elif self.proposal is not None or not self.issues:
            raise ValueError("unsuccessful result requires issues and no proposal")
        return self
