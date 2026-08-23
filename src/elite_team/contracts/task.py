"""Backward-compatible task contract imports.

PR-2 keeps the public ``elite_team.contracts.task`` surface from PR-1 while
the complete workflow contract set lives in :mod:`elite_team.contracts.models`.
"""

from elite_team.contracts.models import (
    Authority,
    FinalDecision,
    HealthResponse,
    NonBlankText,
    ProjectMode,
    StrictContract,
    TaskRequest,
    TaskResponse,
    TaskState,
    TaskStatus,
)

__all__ = [
    "Authority",
    "FinalDecision",
    "HealthResponse",
    "NonBlankText",
    "ProjectMode",
    "StrictContract",
    "TaskRequest",
    "TaskResponse",
    "TaskState",
    "TaskStatus",
]
