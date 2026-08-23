"""Bounded workflow, dependency-injection, and fail-closed invariant tests."""

from __future__ import annotations

import builtins
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from elite_team.agents import ArchitectStub, EngineerStub, ReviewerStub
from elite_team.contracts import (
    ErrorCode,
    FinalDecision,
    GateStatus,
    TaskRequest,
    TaskResponse,
    TaskStatus,
    TraceNode,
)
from elite_team.orchestration.transitions import (
    IllegalTransitionError,
    MissingStateError,
    assert_transition,
    validate_project_mode,
    validate_required_state,
)
from elite_team.orchestration.workflow import WorkflowDependencies, run_workflow

FOUNDATION_NODES = (
    "INTAKE",
    "MODE_ROUTER",
    "STATE_CREATION",
)
HAPPY_WORKFLOW_NODES = (
    "ARCHITECT",
    "ARCHITECTURE_REVIEW",
    "ENGINEER",
    "VALIDATION",
    "REVIEWER",
    "FINALIZE",
)


def _request(**overrides: Any) -> TaskRequest:
    values: dict[str, Any] = {
        "intent": "Design a deterministic service kernel",
        "authority": "READ_ONLY",
    }
    values.update(overrides)
    return TaskRequest.model_validate(values)


def _dependencies(
    *,
    architect: ArchitectStub | None = None,
    engineer: EngineerStub | None = None,
    reviewer: ReviewerStub | None = None,
) -> WorkflowDependencies:
    return WorkflowDependencies(
        architect=architect or ArchitectStub(),
        engineer=engineer or EngineerStub(),
        reviewer=reviewer or ReviewerStub(),
    )


def _nodes(result: TaskResponse) -> tuple[str, ...]:
    return tuple(event.node.value for event in result.trace)


def _assert_blocked(
    result: TaskResponse,
    *,
    error_code: ErrorCode,
    failed_node: TraceNode,
) -> None:
    assert result.status is TaskStatus.WORKFLOW_BLOCKED
    assert result.final_decision is FinalDecision.BLOCKED_REQUIRES_OWNER
    assert result.trace[-1].node is TraceNode.FINALIZE
    assert result.trace[-1].error_code is error_code
    matching = [event for event in result.trace if event.node is failed_node]
    assert matching
    assert matching[-1].error_code is error_code


def test_architecture_revision_once_then_completes() -> None:
    dependencies = _dependencies(
        reviewer=ReviewerStub(
            architecture_decisions=(
                GateStatus.REVISION_REQUIRED,
                GateStatus.APPROVED,
            )
        )
    )

    result = run_workflow(_request(), dependencies)

    assert result.final_decision is FinalDecision.READY_WITH_CONDITIONS
    assert result.architecture_gate is not None
    assert result.architecture_gate.status is GateStatus.APPROVED
    assert result.architecture_gate.revision_count == 1
    assert _nodes(result) == FOUNDATION_NODES + (
        "ARCHITECT",
        "ARCHITECTURE_REVIEW",
        "ARCHITECT",
        "ARCHITECTURE_REVIEW",
    ) + HAPPY_WORKFLOW_NODES[2:]


def test_architecture_revision_limit_exhaustion_blocks_before_engineering() -> None:
    dependencies = _dependencies(
        reviewer=ReviewerStub(
            architecture_decisions=(GateStatus.REVISION_REQUIRED,) * 3
        )
    )

    result = run_workflow(_request(), dependencies)

    _assert_blocked(
        result,
        error_code=ErrorCode.REVISION_LIMIT_EXHAUSTED,
        failed_node=TraceNode.ARCHITECTURE_REVIEW,
    )
    assert result.architecture_gate is not None
    assert result.architecture_gate.revision_count == 2
    assert result.implementation_plan is None
    assert _nodes(result).count("ARCHITECT") == 3
    assert "ENGINEER" not in _nodes(result)


def test_engineering_revision_once_then_completes() -> None:
    dependencies = _dependencies(
        reviewer=ReviewerStub(
            implementation_decisions=(
                GateStatus.REVISION_REQUIRED,
                GateStatus.APPROVED,
            )
        )
    )

    result = run_workflow(_request(), dependencies)

    assert result.final_decision is FinalDecision.READY_WITH_CONDITIONS
    assert result.implementation_gate is not None
    assert result.implementation_gate.status is GateStatus.APPROVED
    assert result.implementation_gate.revision_count == 1
    assert _nodes(result) == FOUNDATION_NODES + HAPPY_WORKFLOW_NODES[:-1] + (
        "ENGINEER",
        "VALIDATION",
        "REVIEWER",
        "FINALIZE",
    )


def test_engineering_revision_limit_exhaustion_blocks() -> None:
    dependencies = _dependencies(
        reviewer=ReviewerStub(
            implementation_decisions=(GateStatus.REVISION_REQUIRED,) * 3
        )
    )

    result = run_workflow(_request(), dependencies)

    _assert_blocked(
        result,
        error_code=ErrorCode.REVISION_LIMIT_EXHAUSTED,
        failed_node=TraceNode.REVIEWER,
    )
    assert result.implementation_gate is not None
    assert result.implementation_gate.revision_count == 2
    assert _nodes(result).count("ENGINEER") == 3
    assert _nodes(result).count("REVIEWER") == 3


class _MalformedArchitect(ArchitectStub):
    def run(self, **_: Any) -> Any:
        return {"status": "COMPLETED"}


class _MalformedEngineer(EngineerStub):
    def run(self, **_: Any) -> Any:
        return {"status": "COMPLETED"}


class _MalformedReviewer(ReviewerStub):
    def review_implementation(self, **_: Any) -> Any:
        return {"decision": "APPROVED"}


@pytest.mark.parametrize(
    ("dependency_factory", "failed_node"),
    [
        (
            lambda: _dependencies(architect=_MalformedArchitect()),
            TraceNode.ARCHITECT,
        ),
        (
            lambda: _dependencies(engineer=_MalformedEngineer()),
            TraceNode.ENGINEER,
        ),
        (
            lambda: _dependencies(reviewer=_MalformedReviewer()),
            TraceNode.REVIEWER,
        ),
    ],
)
def test_malformed_role_output_fails_closed(
    dependency_factory: Callable[[], WorkflowDependencies],
    failed_node: TraceNode,
) -> None:
    result = run_workflow(_request(), dependency_factory())

    _assert_blocked(
        result,
        error_code=ErrorCode.INVALID_AGENT_OUTPUT,
        failed_node=failed_node,
    )


def test_missing_mandatory_internal_state_fails_closed() -> None:
    with pytest.raises(MissingStateError, match="run_id, trace_id"):
        validate_required_state(
            {"task_id": "present", "run_id": None},
            ("task_id", "run_id", "trace_id"),
        )


@pytest.mark.parametrize(
    ("previous", "next_node"),
    [
        (None, TraceNode.FINALIZE),
        (TraceNode.INTAKE, TraceNode.ARCHITECT),
        (TraceNode.FINALIZE, TraceNode.INTAKE),
    ],
)
def test_illegal_transition_is_rejected(
    previous: TraceNode | None, next_node: TraceNode
) -> None:
    with pytest.raises(IllegalTransitionError, match="illegal workflow transition"):
        assert_transition(previous, next_node)


def test_unknown_project_mode_is_rejected() -> None:
    with pytest.raises(RuntimeError, match="unknown project mode"):
        validate_project_mode("UNRECOGNIZED_MODE")


def test_independent_runs_have_deterministic_trace_semantics() -> None:
    request = _request()

    first = run_workflow(request)
    second = run_workflow(request)

    def semantics(result: TaskResponse) -> list[tuple[object, ...]]:
        return [
            (
                event.node,
                event.status,
                event.revision_count,
                event.decision,
                event.error_code,
            )
            for event in result.trace
        ]

    assert semantics(first) == semantics(second)
    assert [event.sequence for event in first.trace] == list(
        range(1, len(first.trace) + 1)
    )
    assert [event.sequence for event in second.trace] == list(
        range(1, len(second.trace) + 1)
    )


def test_reused_dependencies_do_not_share_or_corrupt_execution_state() -> None:
    dependencies = _dependencies(
        reviewer=ReviewerStub(
            architecture_decisions=(
                GateStatus.REVISION_REQUIRED,
                GateStatus.APPROVED,
            )
        )
    )

    first = run_workflow(_request(intent="Design isolated alpha"), dependencies)
    second = run_workflow(_request(intent="Design isolated beta"), dependencies)

    first_ids = {first.task_id, first.run_id, first.trace_id}
    second_ids = {second.task_id, second.run_id, second.trace_id}
    assert len(first_ids) == len(second_ids) == 3
    assert first_ids.isdisjoint(second_ids)
    assert first.current_state.intent == "Design isolated alpha"
    assert second.current_state.intent == "Design isolated beta"
    assert _nodes(first) == _nodes(second)
    assert first.architecture_gate is not second.architecture_gate


def test_read_only_workflow_performs_zero_external_side_effects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*_: Any, **__: Any) -> Any:
        raise AssertionError("external side effect attempted")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)

    result = run_workflow(
        _request(
            intent="Audit this repository without mutation",
            repository="C:/definitely-not-accessed/repository",
        )
    )

    assert result.authority.value == "READ_ONLY"
    assert result.current_state.authority.value == "READ_ONLY"
    assert result.final_decision is FinalDecision.READY_WITH_CONDITIONS
