"""Reject output using fresh host observations; never cancel or dispatch work.

Control owns the window and observer. The gateway does not maintain task state,
grants, cancellation registries or a scheduler. An observation is a trusted-host
assertion at a point in time, not atomic authorization for later consumption.
"""
from __future__ import annotations

import time
from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from types import TracebackType
from typing import Literal

from wolf15_sentient.contracts.model_gateway import GatewayRequest, GatewayResponse
from wolf15_sentient.sentient.model_gateway.canonical import (
    GatewayValidationError,
    canonical,
)
from wolf15_sentient.sentient.model_gateway.validation import (
    validate_request,
    validate_response,
)


@dataclass(frozen=True, slots=True)
class InvocationWindow:
    gateway_invocation_id: str
    gateway_digest_sha256: str
    started_at_ns: int
    deadline_ns: int


@dataclass(frozen=True, slots=True)
class HostObservation:
    gateway_invocation_id: str
    gateway_digest_sha256: str
    observed_at_ns: int
    cancelled: bool
    policy_allowed: bool


class HostOutputRejected(GatewayValidationError):
    """A fixed wire-compatible host rejection category; no provider payload."""

    def __init__(self, failure_code: Literal["CANCELLED", "POLICY", "TIMEOUT"]) -> None:
        super().__init__(failure_code)
        self.failure_code = failure_code


class _ObservationErrors(AbstractContextManager[None]):
    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc_value: BaseException | None,
                 traceback: TracebackType | None) -> Literal[False]:
        if exc_type is not None and issubclass(exc_type, Exception):
            raise GatewayValidationError("HOST_OBSERVATION_FAILED") from None
        return False


def _clock_value(clock: Callable[[], int]) -> int:
    with _ObservationErrors():
        value = clock()
    if type(value) is not int or value < 0:
        raise GatewayValidationError("HOST_CLOCK_INVALID")
    return value


def begin_window(request: GatewayRequest, *, clock: Callable[[], int] = time.monotonic_ns) -> InvocationWindow:
    """Capture a host clock anchor before any future transport dispatch.

    This value is a binding, not a grant. Passing the deadline to a transport and
    proving interruption/cleanup remain the future host/adapter's responsibility.
    """
    bound = validate_request(canonical(request.model_dump(warnings=False)))
    started = _clock_value(clock)
    return InvocationWindow(bound.envelope.gateway_invocation_id, bound.gateway_digest_sha256,
                            started, started + bound.envelope.limits.timeout_ms * 1_000_000)


def admit_response(raw: bytes, request: GatewayRequest, window: InvocationWindow, *,
                   observe: Callable[[], HostObservation],
                   clock: Callable[[], int] = time.monotonic_ns) -> GatewayResponse:
    """Sample Control before and after validation; reject cancellation or lateness.

    The observer must sample current state and timestamp it in this same monotonic
    clock domain. A timestamp outside the measured callback interval is rejected,
    including stale cached observations. No provider timing field substitutes for
    the host clock. Callback/validation duration counts toward output rejection,
    but this synchronous library cannot physically interrupt blocked callbacks,
    transport or cleanup. Control must recheck before any later consumption.
    """
    bound = validate_request(canonical(request.model_dump(warnings=False)))
    if (type(window) is not InvocationWindow
            or type(window.gateway_invocation_id) is not str
            or type(window.gateway_digest_sha256) is not str
            or type(window.started_at_ns) is not int or window.started_at_ns < 0
            or type(window.deadline_ns) is not int
            or window.gateway_invocation_id != bound.envelope.gateway_invocation_id
            or window.gateway_digest_sha256 != bound.gateway_digest_sha256
            or window.deadline_ns != window.started_at_ns + bound.envelope.limits.timeout_ms * 1_000_000):
        raise GatewayValidationError("HOST_INVOCATION_BINDING")

    def sample(previous_ns: int) -> int:
        before = _clock_value(clock)
        with _ObservationErrors():
            observation = observe()
        now = _clock_value(clock)
        if before < previous_ns or now < before:
            raise GatewayValidationError("HOST_CLOCK_REGRESSION")
        if (type(observation) is not HostObservation
                or type(observation.gateway_invocation_id) is not str
                or type(observation.gateway_digest_sha256) is not str
                or type(observation.observed_at_ns) is not int
                or type(observation.cancelled) is not bool or type(observation.policy_allowed) is not bool):
            raise GatewayValidationError("HOST_OBSERVATION_INVALID")
        if (observation.gateway_invocation_id != window.gateway_invocation_id
                or observation.gateway_digest_sha256 != window.gateway_digest_sha256):
            raise GatewayValidationError("HOST_OBSERVATION_BINDING")
        if not before <= observation.observed_at_ns <= now:
            raise GatewayValidationError("HOST_OBSERVATION_STALE_OR_FUTURE")
        if observation.cancelled:
            raise HostOutputRejected("CANCELLED")
        if not observation.policy_allowed:
            raise HostOutputRejected("POLICY")
        if now >= window.deadline_ns:
            raise HostOutputRejected("TIMEOUT")
        return now

    last = sample(window.started_at_ns)
    try:
        response = validate_response(raw, bound)
    except GatewayValidationError:
        sample(last)
        raise
    sample(last)
    return response
