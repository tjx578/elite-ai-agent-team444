"""Correlated execution evidence emitted by deterministic workflow nodes."""

from datetime import datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Reference = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class TraceNode(StrEnum):
    INTAKE = "INTAKE"
    MODE_ROUTER = "MODE_ROUTER"
    STATE_CREATION = "STATE_CREATION"
    ARCHITECT = "ARCHITECT"
    ARCHITECTURE_REVIEW = "ARCHITECTURE_REVIEW"
    ENGINEER = "ENGINEER"
    VALIDATION = "VALIDATION"
    REVIEWER = "REVIEWER"
    FINALIZE = "FINALIZE"


class TraceStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


class ExecutionErrorCode(StrEnum):
    INVALID_AGENT_OUTPUT = "INVALID_AGENT_OUTPUT"
    MISSING_STATE = "MISSING_STATE"
    ILLEGAL_TRANSITION = "ILLEGAL_TRANSITION"
    REVISION_LIMIT_EXHAUSTED = "REVISION_LIMIT_EXHAUSTED"
    VALIDATION_FAILED = "VALIDATION_FAILED"


# Concise compatibility name for callers that used the design-document term.
ErrorCode = ExecutionErrorCode


class ExecutionEvent(BaseModel):
    """One immutable, correlated workflow transition record."""

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
    revision_count: int = Field(default=0, ge=0, le=2)
    error: str | None = None
    error_code: ExecutionErrorCode | None = None
    decision: str | None = None

    @model_validator(mode="after")
    def validate_timing(self) -> "ExecutionEvent":
        if self.finished_at < self.started_at:
            raise ValueError("finished_at must not precede started_at")
        return self


# PR-1 imported this name directly; retain it as a true alias so old and new
# trace lists accept the same immutable event objects.
ExecutionTrace = ExecutionEvent


__all__ = [
    "ErrorCode",
    "ExecutionErrorCode",
    "ExecutionEvent",
    "ExecutionTrace",
    "TraceNode",
    "TraceStatus",
]
