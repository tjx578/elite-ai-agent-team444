"""Evidence and context contracts for WOLF15 Sentient."""

from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, Field, StringConstraints, model_validator

from wolf15_sentient.contracts.models import Authority, NonBlankText, StrictContract

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


class EvidencePolicy(StrictContract):
    """Frozen, task-scoped policy for a deterministic offline evaluation."""

    version: Literal["m2-v0"] = "m2-v0"
    scope: NonBlankText
    revision: NonBlankText
    evaluated_at: AwareDatetime
    max_age_seconds: int = Field(ge=0, le=31_536_000)


class SuppliedSource(StrictContract):
    """Caller-provided UTF-8 text; the locator is never dereferenced."""

    source_id: NonBlankText
    content: str


class DeclaredConflict(StrictContract):
    """A reported disagreement; the evaluator never chooses a winner."""

    left_source_id: NonBlankText
    right_source_id: NonBlankText
    reason: NonBlankText

    @model_validator(mode="after")
    def require_distinct_sources(self) -> "DeclaredConflict":
        if self.left_source_id == self.right_source_id:
            raise ValueError("a declared conflict requires two distinct source IDs")
        return self


class EvidenceContextInput(StrictContract):
    bundle_id: UUID
    task_id: UUID
    run_id: UUID
    policy: EvidencePolicy
    source_refs: list[SourceRef] = Field(default_factory=list)
    supplied_sources: list[SuppliedSource] = Field(default_factory=list)
    claims: list[GroundedClaim] = Field(default_factory=list)
    declared_conflicts: list[DeclaredConflict] = Field(default_factory=list)


class SourceIssue(StrEnum):
    MISSING_CONTENT = "MISSING_CONTENT"
    DUPLICATE_REFERENCE_CONFLICT = "DUPLICATE_REFERENCE_CONFLICT"
    DUPLICATE_CONTENT_CONFLICT = "DUPLICATE_CONTENT_CONFLICT"
    PROVENANCE_CONFLICT = "PROVENANCE_CONFLICT"
    CONTENT_TOO_LARGE = "CONTENT_TOO_LARGE"
    INVALID_UTF8 = "INVALID_UTF8"
    DIGEST_MISMATCH = "DIGEST_MISMATCH"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"
    REVISION_MISMATCH = "REVISION_MISMATCH"
    OBSERVED_IN_FUTURE = "OBSERVED_IN_FUTURE"
    STALE = "STALE"


class SourceAssessment(StrictContract):
    source_id: NonBlankText
    usable: bool
    issues: list[SourceIssue] = Field(default_factory=list)
    actual_digest_sha256: Sha256 | None = None


class ConflictKind(StrEnum):
    DECLARED = "DECLARED"
    PROVENANCE = "PROVENANCE"


class EvidenceConflict(StrictContract):
    kind: ConflictKind
    left_source_id: NonBlankText
    right_source_id: NonBlankText
    reason: NonBlankText
    precedence: Literal["NONE"] = "NONE"


class ClaimIssue(StrEnum):
    DUPLICATE_CLAIM_ID = "DUPLICATE_CLAIM_ID"
    UNKNOWN_EVIDENCE_REF = "UNKNOWN_EVIDENCE_REF"
    UNUSABLE_EVIDENCE_REF = "UNUSABLE_EVIDENCE_REF"
    MISSING_EVIDENCE_REF = "MISSING_EVIDENCE_REF"
    NO_LITERAL_SUPPORT = "NO_LITERAL_SUPPORT"
    INDEPENDENT_VERIFICATION_MISSING = "INDEPENDENT_VERIFICATION_MISSING"
    DERIVATION_NOT_EVALUATED = "DERIVATION_NOT_EVALUATED"


class ClaimOutcome(StrEnum):
    INCLUDED = "INCLUDED"
    DOWNGRADED = "DOWNGRADED"
    REJECTED = "REJECTED"


class ClaimAssessment(StrictContract):
    claim_id: NonBlankText
    outcome: ClaimOutcome
    submitted_status: EvidenceStatus
    effective_status: EvidenceStatus | None = None
    issues: list[ClaimIssue] = Field(default_factory=list)


class ContextResultStatus(StrEnum):
    READY = "READY"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"


class EvidenceContextResult(StrictContract):
    policy_version: Literal["m2-v0"] = "m2-v0"
    policy: EvidencePolicy
    evaluated_at: AwareDatetime
    authority: Literal[Authority.READ_ONLY] = Authority.READ_ONLY
    status: ContextResultStatus
    bundle: ContextBundle | None = None
    source_assessments: list[SourceAssessment] = Field(default_factory=list)
    claim_assessments: list[ClaimAssessment] = Field(default_factory=list)
    conflicts: list[EvidenceConflict] = Field(default_factory=list)
    missing_evidence: list[NonBlankText] = Field(default_factory=list)


__all__ = [
    "ClaimAssessment",
    "ClaimIssue",
    "ClaimOutcome",
    "ClaimType",
    "ConflictKind",
    "ContextBundle",
    "ContextResultStatus",
    "DeclaredConflict",
    "EvidenceConflict",
    "EvidenceContextInput",
    "EvidenceContextResult",
    "EvidencePolicy",
    "EvidenceStatus",
    "GroundedClaim",
    "Sha256",
    "SourceAssessment",
    "SourceIssue",
    "SourceKind",
    "SourceRef",
    "SuppliedSource",
]
