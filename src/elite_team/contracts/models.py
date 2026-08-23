"""Strict typed contracts for deterministic PR-2 workflows."""

from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from elite_team.contracts.execution import ExecutionEvent, TraceNode, TraceStatus

NonBlankText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class StrictContract(BaseModel):
    """Base for fail-closed workflow protocol objects."""

    model_config = ConfigDict(extra="forbid")


class Authority(StrEnum):
    """Authority accepted by the current non-mutating runtime."""

    READ_ONLY = "READ_ONLY"


class ProjectMode(StrEnum):
    EXISTING_REPO_MODE = "EXISTING_REPO_MODE"
    GREENFIELD_SYSTEM_MODE = "GREENFIELD_SYSTEM_MODE"
    HYBRID_EVOLUTION_MODE = "HYBRID_EVOLUTION_MODE"


class TaskStatus(StrEnum):
    """Observable lifecycle outcomes for PR-1 and PR-2."""

    FOUNDATION_COMPLETE = "FOUNDATION_COMPLETE"
    WORKFLOW_COMPLETE = "WORKFLOW_COMPLETE"
    WORKFLOW_BLOCKED = "WORKFLOW_BLOCKED"
    WORKFLOW_NOT_READY = "WORKFLOW_NOT_READY"


class FinalDecision(StrEnum):
    """Assessment outcomes; none confers production authority."""

    READY_WITH_CONDITIONS = "READY_WITH_CONDITIONS"
    NOT_READY = "NOT_READY"
    BLOCKED_REQUIRES_OWNER = "BLOCKED_REQUIRES_OWNER"


class AgentRunStatus(StrEnum):
    COMPLETED = "COMPLETED"


class ValidationStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"


class GateStatus(StrEnum):
    APPROVED = "APPROVED"
    REVISION_REQUIRED = "REVISION_REQUIRED"
    BLOCKED_REQUIRES_OWNER = "BLOCKED_REQUIRES_OWNER"


class GateName(StrEnum):
    ARCHITECTURE = "ARCHITECTURE"
    IMPLEMENTATION = "IMPLEMENTATION"


class TaskRequest(StrictContract):
    intent: NonBlankText
    repository: NonBlankText | None = None
    authority: Authority = Authority.READ_ONLY


class TaskState(StrictContract):
    """Correlated state shared by foundation and workflow responses."""

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


class ArchitectureReport(StrictContract):
    status: AgentRunStatus
    summary: NonBlankText
    risks: list[NonBlankText]
    acceptance_criteria: list[NonBlankText]


class ImplementationPlan(StrictContract):
    status: AgentRunStatus
    summary: NonBlankText
    steps: list[NonBlankText]


class ValidationReport(StrictContract):
    status: ValidationStatus
    summary: NonBlankText
    checks: list[NonBlankText]


class ReviewDecision(StrictContract):
    decision: GateStatus
    reason: NonBlankText
    blocking_findings: list[NonBlankText]


class GateDecision(StrictContract):
    gate: GateName
    status: GateStatus
    reason: NonBlankText
    evidence: list[NonBlankText]
    blocking_findings: list[NonBlankText]
    revision_count: int = Field(ge=0, le=2)


class WorkflowResult(StrictContract):
    """Terminal typed result with complete correlation guarantees."""

    task_id: UUID
    run_id: UUID
    trace_id: UUID
    project_mode: ProjectMode
    authority: Authority
    status: TaskStatus
    final_decision: FinalDecision
    current_state: TaskState
    trace: list[ExecutionEvent] = Field(min_length=1)
    architecture_report: ArchitectureReport | None = None
    architecture_gate: GateDecision | None = None
    implementation_plan: ImplementationPlan | None = None
    validation_report: ValidationReport | None = None
    implementation_gate: GateDecision | None = None

    @model_validator(mode="after")
    def validate_correlations(self) -> "WorkflowResult":
        """Reject mismatched state, trace, ordering, and named gates."""

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
        if (
            self.architecture_gate is not None
            and self.architecture_gate.gate is not GateName.ARCHITECTURE
        ):
            raise ValueError("architecture_gate must identify the architecture gate")
        if (
            self.implementation_gate is not None
            and self.implementation_gate.gate is not GateName.IMPLEMENTATION
        ):
            raise ValueError("implementation_gate must identify the implementation gate")

        # TaskResponse retains a nullable decision solely for the frozen PR-1
        # compatibility helper. Every PR-2 WorkflowResult has a decision and
        # must prove a coherent terminal state before it can be serialized.
        if self.final_decision is None:
            return self
        if self.trace[-1].node is not TraceNode.FINALIZE:
            raise ValueError("terminal workflow trace must end at FINALIZE")

        if self.final_decision is FinalDecision.READY_WITH_CONDITIONS:
            if self.status is not TaskStatus.WORKFLOW_COMPLETE:
                raise ValueError("ready result must be WORKFLOW_COMPLETE")
            if any(
                artifact is None
                for artifact in (
                    self.architecture_report,
                    self.architecture_gate,
                    self.implementation_plan,
                    self.validation_report,
                    self.implementation_gate,
                )
            ):
                raise ValueError("ready result requires every workflow artifact")
            if (
                self.architecture_gate.status is not GateStatus.APPROVED
                or self.implementation_gate.status is not GateStatus.APPROVED
                or self.validation_report.status is not ValidationStatus.PASS
                or self.trace[-1].status is not TraceStatus.PASS
            ):
                raise ValueError("ready result requires passing validation and gates")
        elif self.final_decision is FinalDecision.BLOCKED_REQUIRES_OWNER:
            if (
                self.status is not TaskStatus.WORKFLOW_BLOCKED
                or self.trace[-1].status is not TraceStatus.BLOCKED
            ):
                raise ValueError("blocked result must be terminally blocked")
        elif (
            self.status is not TaskStatus.WORKFLOW_NOT_READY
            or self.trace[-1].status not in (TraceStatus.FAIL, TraceStatus.BLOCKED)
        ):
            raise ValueError("not-ready result must terminate without a passing trace")
        return self


class TaskResponse(WorkflowResult):
    """PR-1-compatible response; foundation requests have no final decision."""

    final_decision: FinalDecision | None = None


class HealthResponse(StrictContract):
    status: Literal["ok"]
    service: Literal["elite-ai-agent-team"]
    version: NonBlankText


__all__ = [
    "AgentRunStatus",
    "ArchitectureReport",
    "Authority",
    "FinalDecision",
    "GateDecision",
    "GateName",
    "GateStatus",
    "HealthResponse",
    "ImplementationPlan",
    "NonBlankText",
    "ProjectMode",
    "ReviewDecision",
    "StrictContract",
    "TaskRequest",
    "TaskResponse",
    "TaskState",
    "TaskStatus",
    "ValidationReport",
    "ValidationStatus",
    "WorkflowResult",
]
