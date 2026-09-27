"""Deterministic orchestration primitives for the executable kernel."""

from wolf15_sentient.orchestration.mode_router import detect_project_mode
from wolf15_sentient.orchestration.state import create_task_foundation
from wolf15_sentient.orchestration.transitions import (
    IllegalTransitionError,
    MissingStateError,
    WorkflowInvariantError,
    assert_transition,
    validate_project_mode,
    validate_required_state,
)
from wolf15_sentient.orchestration.workflow import (
    DEFAULT_WORKFLOW,
    MAX_ARCHITECT_REVISIONS,
    MAX_ENGINEER_REVISIONS,
    WorkflowDependencies,
    build_workflow,
    run_workflow,
)

__all__ = [
    "DEFAULT_WORKFLOW",
    "MAX_ARCHITECT_REVISIONS",
    "MAX_ENGINEER_REVISIONS",
    "IllegalTransitionError",
    "MissingStateError",
    "WorkflowDependencies",
    "WorkflowInvariantError",
    "assert_transition",
    "build_workflow",
    "create_task_foundation",
    "detect_project_mode",
    "run_workflow",
    "validate_project_mode",
    "validate_required_state",
]
