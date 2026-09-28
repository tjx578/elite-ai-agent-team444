"""Strict typed contracts for deterministic PR-2 workflows."""

from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from wolf15_sentient.contracts.execution import ExecutionEvent, TraceNode, TraceStatus

NonBlankText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
IntentText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4096)
]
RepositoryReference = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2048)
]


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


class RoutingReason(StrEnum):
    NO_REPOSITORY = "NO_REPOSITORY"
    EXPLICIT_EVOLUTION_INTENT = "EXPLICIT_EVOLUTION_INTENT"
    NO_EXPLICIT_EVOLUTION_INTENT = "NO_EXPLICIT_EVOLUTION_INTENT"


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
    intent: IntentText
    repository: RepositoryReference | None = None
    authority: Authority


class TaskState(StrictContract):
    """Correlated state shared by foundation and workflow responses."""

    schema_version: Literal["1.0"] = "1.0"
    task_id: UUID
    run_id: UUID
    trace_id: UUID
    intent: IntentText
    repository: RepositoryReference | None
    authority: Authority
    project_mode: ProjectMode
    routing_reason: RoutingReason
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
    routing_reason: RoutingReason
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

        _validate_result(self)
        return self


class TaskResponse(StrictContract):
    """PR-1-compatible response; foundation requests have no final decision."""

    task_id: UUID
    run_id: UUID
    trace_id: UUID
    project_mode: ProjectMode
    routing_reason: RoutingReason
    authority: Authority
    status: TaskStatus
    final_decision: FinalDecision | None = None
    current_state: TaskState
    trace: list[ExecutionEvent] = Field(min_length=1)
    architecture_report: ArchitectureReport | None = None
    architecture_gate: GateDecision | None = None
    implementation_plan: ImplementationPlan | None = None
    validation_report: ValidationReport | None = None
    implementation_gate: GateDecision | None = None

    @model_validator(mode="after")
    def validate_correlations(self) -> "TaskResponse":
        """Apply the same correlation checks to the foundation response."""

        _validate_result(self)
        return self


def _validate_result(result: WorkflowResult | TaskResponse) -> None:
    identifiers = (result.task_id, result.run_id, result.trace_id)
    state_identifiers = (
        result.current_state.task_id,
        result.current_state.run_id,
        result.current_state.trace_id,
    )
    if identifiers != state_identifiers:
        raise ValueError(
            "current_state correlation identifiers do not match response"
        )
    if any(
        (event.task_id, event.run_id, event.trace_id) != identifiers
        for event in result.trace
    ):
        raise ValueError("trace correlation identifiers do not match response")
    if [event.sequence for event in result.trace] != list(
        range(1, len(result.trace) + 1)
    ):
        raise ValueError("trace sequence must be contiguous and start at one")
    if (
        result.current_state.project_mode != result.project_mode
        or result.current_state.routing_reason != result.routing_reason
        or result.current_state.authority != result.authority
        or result.current_state.status != result.status
        or result.current_state.final_decision != result.final_decision
    ):
        raise ValueError("current_state outcome fields do not match response")
    if (
        result.architecture_gate is not None
        and result.architecture_gate.gate is not GateName.ARCHITECTURE
    ):
        raise ValueError("architecture_gate must identify the architecture gate")
    if (
        result.implementation_gate is not None
        and result.implementation_gate.gate is not GateName.IMPLEMENTATION
    ):
        raise ValueError(
            "implementation_gate must identify the implementation gate"
        )

    # TaskResponse retains a nullable decision solely for the frozen PR-1
    # compatibility helper. Every PR-2 WorkflowResult has a decision and
    # must prove a coherent terminal state before it can be serialized.
    decision = result.final_decision
    if decision is None:
        return
    if result.trace[-1].node is not TraceNode.FINALIZE:
        raise ValueError("terminal workflow trace must end at FINALIZE")

    if decision is FinalDecision.READY_WITH_CONDITIONS:
        if result.status is not TaskStatus.WORKFLOW_COMPLETE:
            raise ValueError("ready result must be WORKFLOW_COMPLETE")
        architecture_report = result.architecture_report
        architecture_gate = result.architecture_gate
        implementation_plan = result.implementation_plan
        validation_report = result.validation_report
        implementation_gate = result.implementation_gate
        if (
            architecture_report is None
            or architecture_gate is None
            or implementation_plan is None
            or validation_report is None
            or implementation_gate is None
        ):
            raise ValueError("ready result requires every workflow artifact")
        if (
            architecture_gate.status is not GateStatus.APPROVED
            or implementation_gate.status is not GateStatus.APPROVED
            or validation_report.status is not ValidationStatus.PASS
            or result.trace[-1].status is not TraceStatus.PASS
        ):
            raise ValueError("ready result requires passing validation and gates")
    elif decision is FinalDecision.BLOCKED_REQUIRES_OWNER:
        if (
            result.status is not TaskStatus.WORKFLOW_BLOCKED
            or result.trace[-1].status is not TraceStatus.BLOCKED
        ):
            raise ValueError("blocked result must be terminally blocked")
    elif result.status is not TaskStatus.WORKFLOW_NOT_READY or result.trace[
        -1
    ].status not in (TraceStatus.FAIL, TraceStatus.BLOCKED):
        raise ValueError("not-ready result must terminate without a passing trace")


class HealthResponse(StrictContract):
    status: Literal["ok"]
    service: Literal["wolf15-sentient"]
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
    "IntentText",
    "NonBlankText",
    "ProjectMode",
    "RepositoryReference",
    "ReviewDecision",
    "RoutingReason",
    "StrictContract",
    "TaskRequest",
    "TaskResponse",
    "TaskState",
    "TaskStatus",
    "ValidationReport",
    "ValidationStatus",
    "WorkflowResult",
]
