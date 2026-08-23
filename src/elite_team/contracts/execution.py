"""Execution evidence emitted by the deterministic foundation steps."""

from datetime import datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


Reference = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class TraceNode(StrEnum):
    """The only nodes executed by the PR-1 foundation."""

    INTAKE = "INTAKE"
    MODE_ROUTER = "MODE_ROUTER"
    STATE_CREATION = "STATE_CREATION"


class TraceStatus(StrEnum):
    PASS = "PASS"


class ExecutionTrace(BaseModel):
    """One completed, correlated foundation step.

    References are logical names instead of raw payload copies, keeping the
    trace useful without duplicating potentially sensitive owner input.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    sequence: int = Field(ge=1)
    task_id: UUID
    run_id: UUID
    trace_id: UUID
    node: TraceNode
    started_at: datetime
    finished_at: datetime
    status: TraceStatus
    input_reference: Reference
    output_reference: Reference
    error: str | None = None
    decision: str | None = None


__all__ = ["ExecutionTrace", "TraceNode", "TraceStatus"]

