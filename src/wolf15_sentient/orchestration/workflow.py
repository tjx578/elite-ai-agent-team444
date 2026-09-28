"""Deterministic LangGraph orchestration kernel for PR-2."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from operator import add
from typing import Annotated, Any, TypedDict, TypeVar
from uuid import UUID, uuid4

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from wolf15_sentient.agents import ArchitectStub, EngineerStub, ReviewerStub
from wolf15_sentient.contracts import (
    ArchitectureReport,
    Authority,
    ErrorCode,
    ExecutionEvent,
    FinalDecision,
    GateDecision,
    GateName,
    GateStatus,
    ImplementationPlan,
    ProjectMode,
    ReviewDecision,
    RoutingReason,
    TaskRequest,
    TaskState,
    TaskStatus,
    TraceNode,
    TraceStatus,
    ValidationReport,
    ValidationStatus,
    WorkflowResult,
)
from wolf15_sentient.orchestration.mode_router import select_project_mode
from wolf15_sentient.orchestration.transitions import (
    WorkflowInvariantError,
    assert_transition,
    validate_project_mode,
    validate_required_state,
)

MAX_ARCHITECT_REVISIONS = 2
MAX_ENGINEER_REVISIONS = 2
WORKFLOW_RECURSION_LIMIT = 32
ModelT = TypeVar("ModelT", bound=BaseModel)
StateT = TypeVar("StateT")


class WorkflowGraphState(TypedDict, total=False):
    request: TaskRequest
    task_id: UUID
    run_id: UUID
    trace_id: UUID
    authority: Authority
    project_mode: ProjectMode
    routing_reason: RoutingReason
    trace: Annotated[list[ExecutionEvent], add]
    architecture_revision_count: int
    engineer_revision_count: int
    architecture_report: ArchitectureReport
    architecture_gate: GateDecision
    implementation_plan: ImplementationPlan
    validation_report: ValidationReport
    implementation_gate: GateDecision
    terminal_status: TaskStatus
    final_decision: FinalDecision
    failure_code: ErrorCode
    failure_reason: str


def _required(state: WorkflowGraphState, key: str, expected: type[StateT]) -> StateT:
    """Read a graph field only after checking its presence and runtime type."""

    value = state.get(key)
    validate_required_state(state, (key,))
    if not isinstance(value, expected):
        raise WorkflowInvariantError(f"invalid workflow state type: {key}")
    return value


@dataclass(frozen=True, slots=True)
class WorkflowDependencies:
    """Side-effect-free role adapters injected into one compiled graph."""

    architect: ArchitectStub
    engineer: EngineerStub
    reviewer: ReviewerStub


def _default_dependencies() -> WorkflowDependencies:
    return WorkflowDependencies(
        architect=ArchitectStub(),
        engineer=EngineerStub(),
        reviewer=ReviewerStub(),
    )


def _previous_node(state: WorkflowGraphState) -> TraceNode | None:
    trace = state.get("trace", [])
    return trace[-1].node if trace else None


def _event(
    state: WorkflowGraphState,
    *,
    node: TraceNode,
    started_at: datetime,
    status: TraceStatus,
    input_reference: str,
    output_reference: str,
    revision_count: int = 0,
    decision: str | None = None,
    error_code: ErrorCode | None = None,
    error: str | None = None,
) -> ExecutionEvent:
    validate_required_state(state, ("task_id", "run_id", "trace_id"))
    return ExecutionEvent(
        sequence=len(state.get("trace", [])) + 1,
        task_id=_required(state, "task_id", UUID),
        run_id=_required(state, "run_id", UUID),
        trace_id=_required(state, "trace_id", UUID),
        node=node,
        started_at=started_at,
        finished_at=datetime.now(UTC),
        status=status,
        input_reference=input_reference,
        output_reference=output_reference,
        revision_count=revision_count,
        decision=decision,
        error_code=error_code,
        error=error,
    )


def _typed_output(value: object, contract: type[ModelT]) -> ModelT:
    """Validate every role output, including already-instantiated models."""

    if isinstance(value, BaseModel) and isinstance(value, contract):
        return contract.model_validate(value.model_dump())
    return contract.model_validate(value)


def _blocked_update(
    state: WorkflowGraphState,
    *,
    node: TraceNode,
    started_at: datetime,
    revision_count: int,
    error_code: ErrorCode,
    reason: str,
) -> WorkflowGraphState:
    return {
        "failure_code": error_code,
        "failure_reason": reason,
        "terminal_status": TaskStatus.WORKFLOW_BLOCKED,
        "final_decision": FinalDecision.BLOCKED_REQUIRES_OWNER,
        "trace": [
            _event(
                state,
                node=node,
                started_at=started_at,
                status=TraceStatus.FAIL,
                input_reference=f"workflow.{node.value.lower()}.input",
                output_reference="workflow.blocked",
                revision_count=revision_count,
                decision=FinalDecision.BLOCKED_REQUIRES_OWNER.value,
                error_code=error_code,
                error=reason,
            )
        ],
    }


def _guard(state: WorkflowGraphState, node: TraceNode, fields: tuple[str, ...]) -> None:
    assert_transition(_previous_node(state), node)
    validate_required_state(state, fields)


def _route_failure_or(state: WorkflowGraphState, next_node: str) -> str:
    return "finalize" if state.get("failure_code") is not None else next_node


def build_workflow(dependencies: WorkflowDependencies | None = None) -> Any:
    """Build and compile the bounded deterministic StateGraph."""

    deps = dependencies or _default_dependencies()

    def intake(state: WorkflowGraphState) -> WorkflowGraphState:
        started = datetime.now(UTC)
        _guard(state, TraceNode.INTAKE, ("request", "task_id", "run_id", "trace_id"))
        request = TaskRequest.model_validate(_required(state, "request", TaskRequest).model_dump())
        return {
            "request": request,
            "authority": request.authority,
            "trace": [
                _event(
                    state,
                    node=TraceNode.INTAKE,
                    started_at=started,
                    status=TraceStatus.PASS,
                    input_reference="http.task_request",
                    output_reference="validated.task_request",
                    decision=request.authority.value,
                )
            ],
        }

    def mode_router(state: WorkflowGraphState) -> WorkflowGraphState:
        started = datetime.now(UTC)
        _guard(state, TraceNode.MODE_ROUTER, ("request", "authority"))
        request = _required(state, "request", TaskRequest)
        selection = select_project_mode(request.intent, request.repository)
        return {
            "project_mode": selection.mode,
            "routing_reason": selection.reason,
            "trace": [
                _event(
                    state,
                    node=TraceNode.MODE_ROUTER,
                    started_at=started,
                    status=TraceStatus.PASS,
                    input_reference="validated.task_request",
                    output_reference="routing.project_mode",
                    decision=f"{selection.mode.value}:{selection.reason.value}",
                )
            ],
        }

    def state_creation(state: WorkflowGraphState) -> WorkflowGraphState:
        started = datetime.now(UTC)
        _guard(
            state,
            TraceNode.STATE_CREATION,
            ("request", "authority", "project_mode"),
        )
        mode = validate_project_mode(_required(state, "project_mode", ProjectMode))
        return {
            "architecture_revision_count": 0,
            "engineer_revision_count": 0,
            "trace": [
                _event(
                    state,
                    node=TraceNode.STATE_CREATION,
                    started_at=started,
                    status=TraceStatus.PASS,
                    input_reference="routing.project_mode",
                    output_reference="workflow.initial_state",
                    decision=mode.value,
                )
            ],
        }

    def architect(state: WorkflowGraphState) -> WorkflowGraphState:
        started = datetime.now(UTC)
        revision = state.get("architecture_revision_count", 0)
        try:
            _guard(
                state,
                TraceNode.ARCHITECT,
                ("request", "authority", "project_mode"),
            )
            mode = validate_project_mode(_required(state, "project_mode", ProjectMode))
            raw = deps.architect.run(
                intent=_required(state, "request", TaskRequest).intent,
                project_mode=mode,
                revision_count=revision,
            )
            report = _typed_output(raw, ArchitectureReport)
        except (AttributeError, RuntimeError, TypeError, ValueError):
            return _blocked_update(
                state,
                node=TraceNode.ARCHITECT,
                started_at=started,
                revision_count=revision,
                error_code=ErrorCode.INVALID_AGENT_OUTPUT,
                reason="Architect output failed typed validation.",
            )
        return {
            "architecture_report": report,
            "trace": [
                _event(
                    state,
                    node=TraceNode.ARCHITECT,
                    started_at=started,
                    status=TraceStatus.PASS,
                    input_reference="workflow.task_and_mode",
                    output_reference="report.architecture",
                    revision_count=revision,
                    decision=report.status.value,
                )
            ],
        }

    def architecture_review(state: WorkflowGraphState) -> WorkflowGraphState:
        started = datetime.now(UTC)
        revision = _required(state, "architecture_revision_count", int)
        try:
            _guard(
                state,
                TraceNode.ARCHITECTURE_REVIEW,
                ("architecture_report", "architecture_revision_count"),
            )
            raw = deps.reviewer.review_architecture(
                report=_required(state, "architecture_report", ArchitectureReport),
                revision_count=revision,
            )
            review = _typed_output(raw, ReviewDecision)
        except (AttributeError, RuntimeError, TypeError, ValueError):
            return _blocked_update(
                state,
                node=TraceNode.ARCHITECTURE_REVIEW,
                started_at=started,
                revision_count=revision,
                error_code=ErrorCode.INVALID_AGENT_OUTPUT,
                reason="Architecture review output failed typed validation.",
            )

        decision = review.decision
        if (
            decision is GateStatus.REVISION_REQUIRED
            and revision >= MAX_ARCHITECT_REVISIONS
        ):
            gate = GateDecision(
                gate=GateName.ARCHITECTURE,
                status=GateStatus.BLOCKED_REQUIRES_OWNER,
                reason="Architecture revision limit exhausted.",
                evidence=["Maximum architecture revisions reached."],
                blocking_findings=review.blocking_findings,
                revision_count=revision,
            )
            return {
                "architecture_gate": gate,
                "failure_code": ErrorCode.REVISION_LIMIT_EXHAUSTED,
                "failure_reason": gate.reason,
                "terminal_status": TaskStatus.WORKFLOW_BLOCKED,
                "final_decision": FinalDecision.BLOCKED_REQUIRES_OWNER,
                "trace": [
                    _event(
                        state,
                        node=TraceNode.ARCHITECTURE_REVIEW,
                        started_at=started,
                        status=TraceStatus.BLOCKED,
                        input_reference="report.architecture",
                        output_reference="gate.architecture",
                        revision_count=revision,
                        decision=gate.status.value,
                        error_code=ErrorCode.REVISION_LIMIT_EXHAUSTED,
                        error=gate.reason,
                    )
                ],
            }

        gate = GateDecision(
            gate=GateName.ARCHITECTURE,
            status=decision,
            reason=review.reason,
            evidence=["Typed deterministic architecture review completed."],
            blocking_findings=review.blocking_findings,
            revision_count=revision,
        )
        update: WorkflowGraphState = {"architecture_gate": gate}
        event_status = TraceStatus.PASS
        if decision is GateStatus.REVISION_REQUIRED:
            update["architecture_revision_count"] = revision + 1
        elif decision is GateStatus.BLOCKED_REQUIRES_OWNER:
            update.update(
                failure_code=ErrorCode.VALIDATION_FAILED,
                failure_reason=gate.reason,
                terminal_status=TaskStatus.WORKFLOW_BLOCKED,
                final_decision=FinalDecision.BLOCKED_REQUIRES_OWNER,
            )
            event_status = TraceStatus.BLOCKED
        update["trace"] = [
            _event(
                state,
                node=TraceNode.ARCHITECTURE_REVIEW,
                started_at=started,
                status=event_status,
                input_reference="report.architecture",
                output_reference="gate.architecture",
                revision_count=revision,
                decision=gate.status.value,
            )
        ]
        return update

    def engineer(state: WorkflowGraphState) -> WorkflowGraphState:
        started = datetime.now(UTC)
        revision = state.get("engineer_revision_count", 0)
        try:
            _guard(
                state,
                TraceNode.ENGINEER,
                ("architecture_report", "architecture_gate", "project_mode"),
            )
            mode = validate_project_mode(_required(state, "project_mode", ProjectMode))
            raw = deps.engineer.run(
                architecture=_required(state, "architecture_report", ArchitectureReport),
                project_mode=mode,
                revision_count=revision,
            )
            plan = _typed_output(raw, ImplementationPlan)
        except (AttributeError, RuntimeError, TypeError, ValueError):
            return _blocked_update(
                state,
                node=TraceNode.ENGINEER,
                started_at=started,
                revision_count=revision,
                error_code=ErrorCode.INVALID_AGENT_OUTPUT,
                reason="Engineer output failed typed validation.",
            )
        return {
            "implementation_plan": plan,
            "trace": [
                _event(
                    state,
                    node=TraceNode.ENGINEER,
                    started_at=started,
                    status=TraceStatus.PASS,
                    input_reference="gate.architecture",
                    output_reference="plan.implementation",
                    revision_count=revision,
                    decision=plan.status.value,
                )
            ],
        }

    def validation(state: WorkflowGraphState) -> WorkflowGraphState:
        started = datetime.now(UTC)
        revision = _required(state, "engineer_revision_count", int)
        try:
            _guard(
                state,
                TraceNode.VALIDATION,
                ("implementation_plan", "engineer_revision_count"),
            )
            ImplementationPlan.model_validate(
                _required(state, "implementation_plan", ImplementationPlan).model_dump()
            )
        except (AttributeError, RuntimeError, TypeError, ValueError):
            return _blocked_update(
                state,
                node=TraceNode.VALIDATION,
                started_at=started,
                revision_count=revision,
                error_code=ErrorCode.VALIDATION_FAILED,
                reason="Implementation plan failed deterministic validation.",
            )
        report = ValidationReport(
            status=ValidationStatus.PASS,
            summary="Typed implementation plan passed deterministic validation.",
            checks=[
                "Implementation plan schema is valid.",
                "No external executor or side-effecting adapter was invoked.",
            ],
        )
        return {
            "validation_report": report,
            "trace": [
                _event(
                    state,
                    node=TraceNode.VALIDATION,
                    started_at=started,
                    status=TraceStatus.PASS,
                    input_reference="plan.implementation",
                    output_reference="report.validation",
                    revision_count=revision,
                    decision=report.status.value,
                )
            ],
        }

    def reviewer(state: WorkflowGraphState) -> WorkflowGraphState:
        started = datetime.now(UTC)
        revision = _required(state, "engineer_revision_count", int)
        try:
            _guard(
                state,
                TraceNode.REVIEWER,
                ("implementation_plan", "validation_report"),
            )
            raw = deps.reviewer.review_implementation(
                plan=_required(state, "implementation_plan", ImplementationPlan),
                validation=_required(state, "validation_report", ValidationReport),
                revision_count=revision,
            )
            review = _typed_output(raw, ReviewDecision)
        except (AttributeError, RuntimeError, TypeError, ValueError):
            return _blocked_update(
                state,
                node=TraceNode.REVIEWER,
                started_at=started,
                revision_count=revision,
                error_code=ErrorCode.INVALID_AGENT_OUTPUT,
                reason="Implementation review output failed typed validation.",
            )

        decision = review.decision
        if (
            decision is GateStatus.REVISION_REQUIRED
            and revision >= MAX_ENGINEER_REVISIONS
        ):
            gate = GateDecision(
                gate=GateName.IMPLEMENTATION,
                status=GateStatus.BLOCKED_REQUIRES_OWNER,
                reason="Engineering revision limit exhausted.",
                evidence=["Maximum engineering revisions reached."],
                blocking_findings=review.blocking_findings,
                revision_count=revision,
            )
            return {
                "implementation_gate": gate,
                "failure_code": ErrorCode.REVISION_LIMIT_EXHAUSTED,
                "failure_reason": gate.reason,
                "terminal_status": TaskStatus.WORKFLOW_BLOCKED,
                "final_decision": FinalDecision.BLOCKED_REQUIRES_OWNER,
                "trace": [
                    _event(
                        state,
                        node=TraceNode.REVIEWER,
                        started_at=started,
                        status=TraceStatus.BLOCKED,
                        input_reference="report.validation",
                        output_reference="gate.implementation",
                        revision_count=revision,
                        decision=gate.status.value,
                        error_code=ErrorCode.REVISION_LIMIT_EXHAUSTED,
                        error=gate.reason,
                    )
                ],
            }

        gate = GateDecision(
            gate=GateName.IMPLEMENTATION,
            status=decision,
            reason=review.reason,
            evidence=["Typed deterministic implementation review completed."],
            blocking_findings=review.blocking_findings,
            revision_count=revision,
        )
        update: WorkflowGraphState = {"implementation_gate": gate}
        event_status = TraceStatus.PASS
        if decision is GateStatus.APPROVED:
            update.update(
                terminal_status=TaskStatus.WORKFLOW_COMPLETE,
                final_decision=FinalDecision.READY_WITH_CONDITIONS,
            )
        elif decision is GateStatus.REVISION_REQUIRED:
            update["engineer_revision_count"] = revision + 1
        else:
            update.update(
                failure_code=ErrorCode.VALIDATION_FAILED,
                failure_reason=gate.reason,
                terminal_status=TaskStatus.WORKFLOW_BLOCKED,
                final_decision=FinalDecision.BLOCKED_REQUIRES_OWNER,
            )
            event_status = TraceStatus.BLOCKED
        update["trace"] = [
            _event(
                state,
                node=TraceNode.REVIEWER,
                started_at=started,
                status=event_status,
                input_reference="report.validation",
                output_reference="gate.implementation",
                revision_count=revision,
                decision=gate.status.value,
            )
        ]
        return update

    def finalize(state: WorkflowGraphState) -> WorkflowGraphState:
        started = datetime.now(UTC)
        _guard(
            state,
            TraceNode.FINALIZE,
            ("terminal_status", "final_decision"),
        )
        decision = _required(state, "final_decision", FinalDecision)
        status = (
            TraceStatus.PASS
            if decision is FinalDecision.READY_WITH_CONDITIONS
            else TraceStatus.BLOCKED
        )
        return {
            "trace": [
                _event(
                    state,
                    node=TraceNode.FINALIZE,
                    started_at=started,
                    status=status,
                    input_reference="workflow.terminal_state",
                    output_reference="workflow.result",
                    revision_count=max(
                        state.get("architecture_revision_count", 0),
                        state.get("engineer_revision_count", 0),
                    ),
                    decision=decision.value,
                    error_code=state.get("failure_code"),
                    error=state.get("failure_reason"),
                )
            ]
        }

    def route_after_architect(state: WorkflowGraphState) -> str:
        return _route_failure_or(state, "architecture_review")

    def route_after_architecture_review(state: WorkflowGraphState) -> str:
        if state.get("failure_code") is not None:
            return "finalize"
        gate = _required(state, "architecture_gate", GateDecision).status
        if gate is GateStatus.REVISION_REQUIRED:
            return "architect"
        if gate is GateStatus.APPROVED:
            return "engineer"
        return "finalize"

    def route_after_engineer(state: WorkflowGraphState) -> str:
        return _route_failure_or(state, "validation")

    def route_after_validation(state: WorkflowGraphState) -> str:
        return _route_failure_or(state, "reviewer")

    def route_after_reviewer(state: WorkflowGraphState) -> str:
        if state.get("failure_code") is not None:
            return "finalize"
        gate = _required(state, "implementation_gate", GateDecision).status
        return "engineer" if gate is GateStatus.REVISION_REQUIRED else "finalize"

    builder = StateGraph(WorkflowGraphState)
    builder.add_node("intake", intake)
    builder.add_node("mode_router", mode_router)
    builder.add_node("state_creation", state_creation)
    builder.add_node("architect", architect)
    builder.add_node("architecture_review", architecture_review)
    builder.add_node("engineer", engineer)
    builder.add_node("validation", validation)
    builder.add_node("reviewer", reviewer)
    builder.add_node("finalize", finalize)
    builder.add_edge(START, "intake")
    builder.add_edge("intake", "mode_router")
    builder.add_edge("mode_router", "state_creation")
    builder.add_edge("state_creation", "architect")
    builder.add_conditional_edges(
        "architect",
        route_after_architect,
        {"architecture_review": "architecture_review", "finalize": "finalize"},
    )
    builder.add_conditional_edges(
        "architecture_review",
        route_after_architecture_review,
        {
            "architect": "architect",
            "engineer": "engineer",
            "finalize": "finalize",
        },
    )
    builder.add_conditional_edges(
        "engineer",
        route_after_engineer,
        {"validation": "validation", "finalize": "finalize"},
    )
    builder.add_conditional_edges(
        "validation",
        route_after_validation,
        {"reviewer": "reviewer", "finalize": "finalize"},
    )
    builder.add_conditional_edges(
        "reviewer",
        route_after_reviewer,
        {"engineer": "engineer", "finalize": "finalize"},
    )
    builder.add_edge("finalize", END)
    return builder.compile()


DEFAULT_WORKFLOW = build_workflow()


def run_workflow(
    request: TaskRequest,
    dependencies: WorkflowDependencies | None = None,
) -> WorkflowResult:
    """Run one isolated workflow and return its typed terminal result."""

    validated_request = TaskRequest.model_validate(request.model_dump())
    initial: WorkflowGraphState = {
        "request": validated_request,
        "task_id": uuid4(),
        "run_id": uuid4(),
        "trace_id": uuid4(),
        "authority": validated_request.authority,
        "trace": [],
        "architecture_revision_count": 0,
        "engineer_revision_count": 0,
    }
    workflow = (
        DEFAULT_WORKFLOW if dependencies is None else build_workflow(dependencies)
    )
    result: WorkflowGraphState = workflow.invoke(
        initial,
        {"recursion_limit": WORKFLOW_RECURSION_LIMIT},
    )
    validate_required_state(
        result,
        (
            "task_id",
            "run_id",
            "trace_id",
            "authority",
            "project_mode",
            "routing_reason",
            "terminal_status",
            "final_decision",
            "trace",
        ),
    )
    project_mode = validate_project_mode(_required(result, "project_mode", ProjectMode))
    task_id = _required(result, "task_id", UUID)
    run_id = _required(result, "run_id", UUID)
    trace_id = _required(result, "trace_id", UUID)
    authority = _required(result, "authority", Authority)
    routing_reason = _required(result, "routing_reason", RoutingReason)
    terminal_status = _required(result, "terminal_status", TaskStatus)
    final_decision = _required(result, "final_decision", FinalDecision)
    trace = result.get("trace")
    if trace is None:
        validate_required_state(result, ("trace",))
        raise WorkflowInvariantError("invalid workflow state type: trace")
    current_state = TaskState(
        task_id=task_id,
        run_id=run_id,
        trace_id=trace_id,
        intent=validated_request.intent,
        repository=validated_request.repository,
        authority=authority,
        project_mode=project_mode,
        routing_reason=routing_reason,
        status=terminal_status,
        final_decision=final_decision,
    )
    return WorkflowResult(
        task_id=task_id,
        run_id=run_id,
        trace_id=trace_id,
        project_mode=project_mode,
        routing_reason=routing_reason,
        authority=authority,
        status=terminal_status,
        final_decision=final_decision,
        current_state=current_state,
        trace=trace,
        architecture_report=result.get("architecture_report"),
        architecture_gate=result.get("architecture_gate"),
        implementation_plan=result.get("implementation_plan"),
        validation_report=result.get("validation_report"),
        implementation_gate=result.get("implementation_gate"),
    )


__all__ = [
    "DEFAULT_WORKFLOW",
    "MAX_ARCHITECT_REVISIONS",
    "MAX_ENGINEER_REVISIONS",
    "WORKFLOW_RECURSION_LIMIT",
    "WorkflowDependencies",
    "WorkflowGraphState",
    "build_workflow",
    "run_workflow",
]
