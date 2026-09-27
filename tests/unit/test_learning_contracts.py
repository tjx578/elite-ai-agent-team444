"""Evidence and non-authoritative learning contract tests."""

from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from wolf15_sentient.contracts.evidence import (
    ClaimType,
    ContextBundle,
    EvidenceStatus,
    GroundedClaim,
    SourceKind,
    SourceRef,
)
from wolf15_sentient.contracts.learning import (
    AdvisoryGeneration,
    CandidateState,
    LearningCandidate,
)


TASK_ID = UUID("00000000-0000-0000-0000-000000000001")
RUN_ID = UUID("00000000-0000-0000-0000-000000000002")
BUNDLE_ID = UUID("00000000-0000-0000-0000-000000000003")
CANDIDATE_ID = UUID("00000000-0000-0000-0000-000000000004")
EPISODE_ID = UUID("00000000-0000-0000-0000-000000000005")
ADVISORY_ID = UUID("00000000-0000-0000-0000-000000000006")
DIGEST = "a" * 64


def _source(source_id: str = "src-1") -> SourceRef:
    return SourceRef(
        source_id=source_id,
        source_kind=SourceKind.DOCUMENT,
        locator="private-research-corpus",
        revision="v1",
        digest_sha256=DIGEST,
        observed_at=datetime(2026, 9, 28, tzinfo=UTC),
        scope="learning-architecture",
    )


def test_verified_claim_requires_evidence_reference() -> None:
    with pytest.raises(ValidationError, match="VERIFIED claims require"):
        GroundedClaim(
            claim_id="claim-1",
            text="Observed behavior",
            evidence_status=EvidenceStatus.VERIFIED,
            claim_type=ClaimType.FACT,
        )


def test_not_measured_claim_must_be_unknown() -> None:
    with pytest.raises(ValidationError, match="NOT_MEASURED claims must use UNKNOWN"):
        GroundedClaim(
            claim_id="claim-1",
            text="Runtime capability exists",
            evidence_status=EvidenceStatus.NOT_MEASURED,
            claim_type=ClaimType.FACT,
        )


def test_context_bundle_rejects_unresolved_evidence_reference() -> None:
    claim = GroundedClaim(
        claim_id="claim-1",
        text="The source states a five-node learning loop",
        evidence_status=EvidenceStatus.SOURCE_CLAIM,
        claim_type=ClaimType.FACT,
        evidence_refs=["missing-source"],
    )

    with pytest.raises(ValidationError, match="must resolve inside"):
        ContextBundle(
            bundle_id=BUNDLE_ID,
            task_id=TASK_ID,
            run_id=RUN_ID,
            source_refs=[_source()],
            claims=[claim],
        )


def test_context_bundle_rejects_duplicate_source_ids() -> None:
    with pytest.raises(ValidationError, match="source_id values must be unique"):
        ContextBundle(
            bundle_id=BUNDLE_ID,
            task_id=TASK_ID,
            run_id=RUN_ID,
            source_refs=[_source(), _source()],
        )


def test_active_candidate_requires_evaluation_and_approval() -> None:
    with pytest.raises(ValidationError, match="evaluation evidence"):
        LearningCandidate(
            candidate_id=CANDIDATE_ID,
            capability_id="research.source-ranking",
            state=CandidateState.ACTIVE_WORKFLOW,
            source_episode_ids=[EPISODE_ID],
            evidence_refs=["src-1"],
        )

    with pytest.raises(ValidationError, match="separate approval reference"):
        LearningCandidate(
            candidate_id=CANDIDATE_ID,
            capability_id="research.source-ranking",
            state=CandidateState.ACTIVE_WORKFLOW,
            source_episode_ids=[EPISODE_ID],
            evidence_refs=["src-1"],
            evaluation_refs=["eval-1"],
        )


def test_learning_candidate_cannot_escalate_runtime_authority() -> None:
    with pytest.raises(ValidationError):
        LearningCandidate.model_validate(
            {
                "candidate_id": str(CANDIDATE_ID),
                "capability_id": "research.source-ranking",
                "source_episode_ids": [str(EPISODE_ID)],
                "evidence_refs": ["src-1"],
                "authority": "WRITE",
                "execution_authority": True,
                "external_mutation_authorized": True,
            }
        )


def test_advisory_contract_is_intrinsically_non_mutating() -> None:
    advisory = AdvisoryGeneration(
        advisory_id=ADVISORY_ID,
        candidate_id=CANDIDATE_ID,
        evidence_refs=["eval-1"],
    )

    assert advisory.authority_class == "RESEARCH_ADVISORY"
    assert advisory.execution_authority is False
    assert advisory.external_mutation_authorized is False
    assert advisory.may_change_authority is False
