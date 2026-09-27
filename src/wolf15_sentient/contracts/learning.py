"""Non-authoritative learning-plane contracts.

These objects are intentionally not wired into the active workflow. They model
evidence-backed episodes and candidate adaptation without granting mutation
authority.
"""

from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import Field, model_validator

from wolf15_sentient.contracts.models import Authority, NonBlankText, StrictContract


class MemoryClass(StrEnum):
    WORKING = "WORKING"
    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"
    PROCEDURAL = "PROCEDURAL"
    AUDIT = "AUDIT"


class CandidateState(StrEnum):
    DRAFT = "DRAFT"
    REJECTED = "REJECTED"
    OFFLINE_EVALUATED = "OFFLINE_EVALUATED"
    SHADOW = "SHADOW"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    ACTIVE_WORKFLOW = "ACTIVE_WORKFLOW"
    DISABLED = "DISABLED"
    SUPERSEDED = "SUPERSEDED"


class LearningEpisode(StrictContract):
    episode_id: UUID
    task_id: UUID
    run_id: UUID
    context_bundle_id: UUID
    memory_class: MemoryClass = MemoryClass.EPISODIC
    summary: NonBlankText
    evidence_refs: list[NonBlankText] = Field(min_length=1)
    authority: Authority = Authority.READ_ONLY

    @model_validator(mode="after")
    def require_episodic_memory(self) -> "LearningEpisode":
        if self.memory_class is not MemoryClass.EPISODIC:
            raise ValueError("LearningEpisode must be stored as EPISODIC memory")
        return self


class LearningCandidate(StrictContract):
    candidate_id: UUID
    capability_id: NonBlankText
    state: CandidateState = CandidateState.DRAFT
    source_episode_ids: list[UUID] = Field(min_length=1)
    evidence_refs: list[NonBlankText] = Field(min_length=1)
    evaluation_refs: list[NonBlankText] = Field(default_factory=list)
    approval_ref: NonBlankText | None = None
    authority: Authority = Authority.READ_ONLY
    execution_authority: Literal[False] = False
    external_mutation_authorized: Literal[False] = False

    @model_validator(mode="after")
    def validate_promotion_bindings(self) -> "LearningCandidate":
        evaluated_states = {
            CandidateState.OFFLINE_EVALUATED,
            CandidateState.SHADOW,
            CandidateState.APPROVAL_PENDING,
            CandidateState.ACTIVE_WORKFLOW,
            CandidateState.DISABLED,
            CandidateState.SUPERSEDED,
        }
        if self.state in evaluated_states and not self.evaluation_refs:
            raise ValueError("evaluated candidate states require evaluation evidence")
        if self.state is CandidateState.ACTIVE_WORKFLOW and self.approval_ref is None:
            raise ValueError("ACTIVE_WORKFLOW requires a separate approval reference")
        return self


class AdvisoryGeneration(StrictContract):
    advisory_id: UUID
    candidate_id: UUID
    evidence_refs: list[NonBlankText] = Field(min_length=1)
    authority_class: Literal["RESEARCH_ADVISORY"] = "RESEARCH_ADVISORY"
    execution_authority: Literal[False] = False
    external_mutation_authorized: Literal[False] = False
    may_change_authority: Literal[False] = False


__all__ = [
    "AdvisoryGeneration",
    "CandidateState",
    "LearningCandidate",
    "LearningEpisode",
    "MemoryClass",
]
