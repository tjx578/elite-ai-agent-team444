"""Task intake, state, and response contracts."""

from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from elite_team.contracts.execution import ExecutionTrace


NonBlankText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Authority(StrEnum):
    """Authority accepted by PR-1.

    Adding an enum member is an authority expansion and must be reviewed as a
    separate change. Unknown or future authority strings fail validation.
    """

    READ_ONLY = "READ_ONLY"


class ProjectMode(StrEnum):
    EXISTING_REPO_MODE = "EXISTING_REPO_MODE"
    GREENFIELD_SYSTEM_MODE = "GREENFIELD_SYSTEM_MODE"
    HYBRID_EVOLUTION_MODE = "HYBRID_EVOLUTION_MODE"


class TaskStatus(StrEnum):
    FOUNDATION_COMPLETE = "FOUNDATION_COMPLETE"


class FinalDecision(StrEnum):
    """Future workflow decisions; PR-1 never selects one."""

    READY_FOR_PRODUCTION = "READY_FOR_PRODUCTION"
    READY_WITH_CONDITIONS = "READY_WITH_CONDITIONS"
    NOT_READY = "NOT_READY"
    BLOCKED_REQUIRES_OWNER = "BLOCKED_REQUIRES_OWNER"


class StrictContract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TaskRequest(StrictContract):
    intent: NonBlankText
    repository: NonBlankText | None = None
    authority: Authority = Authority.READ_ONLY


class TaskState(StrictContract):
    """The complete state produced by PR-1, before any agent workflow exists."""

    schema_version: Literal["1.0"] = "1.0"
    task_id: UUID
    run_id: UUID
    trace_id: UUID
    intent: NonBlankText
    repository: NonBlankText | None
    authority: Authority
    project_mode: ProjectMode
    status: TaskStatus
    final_decision: FinalDecision | None = None


class TaskResponse(StrictContract):
    task_id: UUID
    run_id: UUID
    trace_id: UUID
    project_mode: ProjectMode
    authority: Authority
    status: TaskStatus
    final_decision: FinalDecision | None = None
    current_state: TaskState
    trace: list[ExecutionTrace] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_correlations(self) -> "TaskResponse":
        """Reject inconsistent state or trace correlation data."""

        identifiers = (self.task_id, self.run_id, self.trace_id)
        state_identifiers = (
            self.current_state.task_id,
            self.current_state.run_id,
            self.current_state.trace_id,
        )
        if identifiers != state_identifiers:
            raise ValueError("current_state correlation identifiers do not match response")
        if any(
            (event.task_id, event.run_id, event.trace_id) != identifiers
            for event in self.trace
        ):
            raise ValueError("trace correlation identifiers do not match response")
        if [event.sequence for event in self.trace] != list(
            range(1, len(self.trace) + 1)
        ):
            raise ValueError("trace sequence must be contiguous and start at one")
        if (
            self.current_state.project_mode != self.project_mode
            or self.current_state.authority != self.authority
            or self.current_state.status != self.status
            or self.current_state.final_decision != self.final_decision
        ):
            raise ValueError("current_state outcome fields do not match response")
        return self


class HealthResponse(StrictContract):
    status: Literal["ok"]
    service: Literal["elite-ai-agent-team"]
    version: NonBlankText


__all__ = [
    "Authority",
    "FinalDecision",
    "HealthResponse",
    "ProjectMode",
    "TaskRequest",
    "TaskResponse",
    "TaskState",
    "TaskStatus",
]
