"""PR-1 task state creation without agents, tools, or persistence."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from elite_team.contracts.execution import ExecutionTrace, TraceNode, TraceStatus
from elite_team.contracts.task import TaskRequest, TaskResponse, TaskState, TaskStatus
from elite_team.orchestration.mode_router import detect_project_mode


def _trace_step(
    *,
    sequence: int,
    task_id: UUID,
    run_id: UUID,
    trace_id: UUID,
    node: TraceNode,
    started_at: datetime,
    input_reference: str,
    output_reference: str,
    decision: str | None = None,
) -> ExecutionTrace:
    return ExecutionTrace(
        sequence=sequence,
        task_id=task_id,
        run_id=run_id,
        trace_id=trace_id,
        node=node,
        started_at=started_at,
        finished_at=datetime.now(UTC),
        status=TraceStatus.PASS,
        input_reference=input_reference,
        output_reference=output_reference,
        decision=decision,
    )


def create_task_foundation(request: TaskRequest) -> TaskResponse:
    """Validate intake, route its mode, create state, and return evidence.

    Pydantic has already validated ``request`` at the API boundary. This
    function performs no repository access, agent execution, persistence,
    revision loop, LLM call, or readiness decision.
    """

    task_id = uuid4()
    run_id = uuid4()
    trace_id = uuid4()
    trace: list[ExecutionTrace] = []

    intake_started = datetime.now(UTC)
    trace.append(
        _trace_step(
            sequence=1,
            task_id=task_id,
            run_id=run_id,
            trace_id=trace_id,
            node=TraceNode.INTAKE,
            started_at=intake_started,
            input_reference="http.task_request",
            output_reference="validated.task_request",
            decision=request.authority.value,
        )
    )

    routing_started = datetime.now(UTC)
    project_mode = detect_project_mode(request.intent, request.repository)
    trace.append(
        _trace_step(
            sequence=2,
            task_id=task_id,
            run_id=run_id,
            trace_id=trace_id,
            node=TraceNode.MODE_ROUTER,
            started_at=routing_started,
            input_reference="validated.task_request",
            output_reference="routing.project_mode",
            decision=project_mode.value,
        )
    )

    state_started = datetime.now(UTC)
    current_state = TaskState(
        task_id=task_id,
        run_id=run_id,
        trace_id=trace_id,
        intent=request.intent,
        repository=request.repository,
        authority=request.authority,
        project_mode=project_mode,
        status=TaskStatus.FOUNDATION_COMPLETE,
        final_decision=None,
    )
    trace.append(
        _trace_step(
            sequence=3,
            task_id=task_id,
            run_id=run_id,
            trace_id=trace_id,
            node=TraceNode.STATE_CREATION,
            started_at=state_started,
            input_reference="routing.project_mode",
            output_reference="task.current_state",
            decision=TaskStatus.FOUNDATION_COMPLETE.value,
        )
    )

    return TaskResponse(
        task_id=task_id,
        run_id=run_id,
        trace_id=trace_id,
        project_mode=project_mode,
        authority=request.authority,
        status=TaskStatus.FOUNDATION_COMPLETE,
        final_decision=None,
        current_state=current_state,
        trace=trace,
    )


__all__ = ["create_task_foundation"]
