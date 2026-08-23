"""Fail-closed transition and state invariants for the PR-2 kernel."""

from collections.abc import Mapping, Sequence
from typing import Any

from elite_team.contracts import ProjectMode, TraceNode


class WorkflowInvariantError(RuntimeError):
    """Base error for invalid internal workflow state."""


class MissingStateError(WorkflowInvariantError):
    """Raised when a node cannot find mandatory state."""


class IllegalTransitionError(WorkflowInvariantError):
    """Raised when a node transition is outside the explicit graph policy."""


_ALLOWED_TRANSITIONS: dict[TraceNode | None, frozenset[TraceNode]] = {
    None: frozenset({TraceNode.INTAKE}),
    TraceNode.INTAKE: frozenset({TraceNode.MODE_ROUTER}),
    TraceNode.MODE_ROUTER: frozenset({TraceNode.STATE_CREATION}),
    TraceNode.STATE_CREATION: frozenset({TraceNode.ARCHITECT}),
    TraceNode.ARCHITECT: frozenset(
        {TraceNode.ARCHITECTURE_REVIEW, TraceNode.FINALIZE}
    ),
    TraceNode.ARCHITECTURE_REVIEW: frozenset(
        {TraceNode.ARCHITECT, TraceNode.ENGINEER, TraceNode.FINALIZE}
    ),
    TraceNode.ENGINEER: frozenset({TraceNode.VALIDATION, TraceNode.FINALIZE}),
    TraceNode.VALIDATION: frozenset({TraceNode.REVIEWER, TraceNode.FINALIZE}),
    TraceNode.REVIEWER: frozenset({TraceNode.ENGINEER, TraceNode.FINALIZE}),
    TraceNode.FINALIZE: frozenset(),
}


def assert_transition(previous: TraceNode | None, next_node: TraceNode) -> None:
    """Reject every transition that is not explicitly authorized."""

    if not isinstance(next_node, TraceNode):
        raise IllegalTransitionError("next node is not a recognized TraceNode")
    if previous is not None and not isinstance(previous, TraceNode):
        raise IllegalTransitionError("previous node is not a recognized TraceNode")
    if next_node not in _ALLOWED_TRANSITIONS.get(previous, frozenset()):
        previous_label = "START" if previous is None else previous.value
        raise IllegalTransitionError(
            f"illegal workflow transition: {previous_label} -> {next_node.value}"
        )


def validate_required_state(
    state: Mapping[str, Any],
    fields: Sequence[str],
) -> None:
    """Require named fields and reject absent or ``None`` values."""

    missing = sorted(field for field in fields if state.get(field) is None)
    if missing:
        raise MissingStateError(
            "missing mandatory workflow state: " + ", ".join(missing)
        )


def validate_project_mode(value: object) -> ProjectMode:
    """Return a typed mode or reject unknown internal values."""

    if isinstance(value, ProjectMode):
        return value
    try:
        return ProjectMode(value)
    except (TypeError, ValueError) as exc:
        raise WorkflowInvariantError("unknown project mode") from exc


__all__ = [
    "IllegalTransitionError",
    "MissingStateError",
    "WorkflowInvariantError",
    "assert_transition",
    "validate_project_mode",
    "validate_required_state",
]
