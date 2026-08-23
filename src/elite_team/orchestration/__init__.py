"""Deterministic orchestration primitives for PR-1."""

from elite_team.orchestration.mode_router import detect_project_mode
from elite_team.orchestration.state import create_task_foundation

__all__ = ["create_task_foundation", "detect_project_mode"]

