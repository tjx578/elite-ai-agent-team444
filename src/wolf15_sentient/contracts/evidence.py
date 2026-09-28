"""Evidence and context contracts for WOLF15 Sentient."""

from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, Field, StringConstraints, model_validator

from wolf15_sentient.contracts.models import NonBlankText, StrictContract

Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class EvidenceStatus(StrEnum):
    VERIFIED = "VERIFIED"
    SOURCE_CLAIM = "SOURCE_CLAIM"
    DERIVED = "DERIVED"
    ASSUMPTION = "ASSUMPTION"
    NOT_MEASURED = "NOT_MEASURED"


class ClaimType(StrEnum):
    FACT = "FACT"
    ESTIMATE = "ESTIMATE"
    SCENARIO = "SCENARIO"
    UNKNOWN = "UNKNOWN"


class SourceKind(StrEnum):
    REPOSITORY = "REPOSITORY"
    DOCUMENT = "DOCUMENT"
    RUNTIME = "RUNTIME"
    TOOL_RECEIPT = "TOOL_RECEIPT"
    EXTERNAL_REFERENCE = "EXTERNAL_REFERENCE"


class SourceRef(StrictContract):
    source_id: NonBlankText
    source_kind: SourceKind
    locator: NonBlankText
    revision: NonBlankText
    digest_sha256: Sha256
    observed_at: AwareDatetime
    scope: NonBlankText


class GroundedClaim(StrictContract):
    claim_id: NonBlankText
    text: NonBlankText
    evidence_status: EvidenceStatus
    claim_type: ClaimType
    evidence_refs: list[NonBlankText] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_evidence_semantics(self) -> "GroundedClaim":
        if self.evidence_status is EvidenceStatus.VERIFIED and not self.evidence_refs:
            raise ValueError("VERIFIED claims require at least one evidence reference")
        if (
            self.evidence_status is EvidenceStatus.NOT_MEASURED
            and self.claim_type is not ClaimType.UNKNOWN
        ):
            raise ValueError("NOT_MEASURED claims must use UNKNOWN claim type")
        return self


class ContextBundle(StrictContract):
    bundle_id: UUID
    task_id: UUID
    run_id: UUID
    source_refs: list[SourceRef] = Field(min_length=1)
    claims: list[GroundedClaim] = Field(default_factory=list)
    conflicts: list[NonBlankText] = Field(default_factory=list)
    missing_evidence: list[NonBlankText] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_internal_references(self) -> "ContextBundle":
        source_ids = [source.source_id for source in self.source_refs]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source_id values must be unique inside a ContextBundle")

        claim_ids = [claim.claim_id for claim in self.claims]
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("claim_id values must be unique inside a ContextBundle")

        known_sources = set(source_ids)
        for claim in self.claims:
            unknown = set(claim.evidence_refs) - known_sources
            if unknown:
                raise ValueError(
                    "claim evidence references must resolve inside the ContextBundle"
                )
        return self


__all__ = [
    "ClaimType",
    "ContextBundle",
    "EvidenceStatus",
    "GroundedClaim",
    "Sha256",
    "SourceKind",
    "SourceRef",
]
