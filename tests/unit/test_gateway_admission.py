"""Synthetic host observations establish output rejection, not interruption."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest
from test_gateway_validation import fixture, rebind

from wolf15_sentient.sentient.model_gateway import admission
from wolf15_sentient.sentient.model_gateway.admission import (
    HostObservation,
    HostOutputRejected,
    admit_response,
    begin_window,
)
from wolf15_sentient.sentient.model_gateway.canonical import (
    GatewayValidationError,
    canonical,
)


@pytest.fixture
def subject():
    request = rebind(fixture("request"))
    window = begin_window(request, clock=lambda: 0)
    raw = canonical(fixture("response"))
    return request, window, raw


def observer(window, timestamps, *, cancellations=(False, False), policies=(True, True)):
    observations = iter(zip(timestamps, cancellations, policies, strict=True))

    def observe():
        timestamp, cancelled, policy = next(observations)
        return HostObservation(window.gateway_invocation_id, window.gateway_digest_sha256,
                               timestamp, cancelled, policy)
    return observe


def test_success_keeps_execution_unauthorized(subject):
    request, window, raw = subject
    ticks = iter([1, 3, 4, 6])
    result = admit_response(raw, request, window, clock=lambda: next(ticks),
                           observe=observer(window, [2, 5]))
    assert result.status == "PROPOSAL_VALIDATED"
    assert result.execution_authorized is False


@pytest.mark.parametrize("phase", ["before", "after"])
@pytest.mark.parametrize("fault", ["cancel", "policy", "deadline"])
def test_host_rejection_overrides_timely_provider_claim(subject, phase, fault):
    request, window, raw = subject
    # Provider receipt claims zero elapsed time. The host never trusts that claim.
    if fault == "deadline":
        times = [window.deadline_ns-1, window.deadline_ns] if phase == "before" else [1, 3, window.deadline_ns-1, window.deadline_ns]
        observed = [window.deadline_ns] if phase == "before" else [2, window.deadline_ns]
        kwargs = {"timestamps": observed, "cancellations": (False,)*len(observed), "policies": (True,)*len(observed)}
        code = "TIMEOUT"
    else:
        times, observed = [1, 3, 4, 6], [2, 5]
        flags = (True, False) if phase == "before" else (False, True)
        kwargs = {"timestamps": observed, "cancellations": flags if fault == "cancel" else (False, False),
                  "policies": tuple(not x for x in flags) if fault == "policy" else (True, True)}
        code = "CANCELLED" if fault == "cancel" else "POLICY"
    ticks = iter(times)
    with pytest.raises(HostOutputRejected, match=code) as caught:
        admit_response(raw, request, window, clock=lambda: next(ticks), observe=observer(window, **kwargs))
    assert caught.value.failure_code == code


def test_cancellation_has_priority_over_policy_timeout_and_malformed_output(subject):
    request, window, _ = subject
    ticks = iter([window.deadline_ns, window.deadline_ns])
    with pytest.raises(HostOutputRejected, match="CANCELLED"):
        admit_response(b"invalid", request, window, clock=lambda: next(ticks),
                       observe=observer(window, [window.deadline_ns], cancellations=(True,), policies=(False,)))


def test_cancellation_during_invalid_output_validation_has_priority(subject):
    request, window, _ = subject
    ticks = iter([1, 3, 4, 6])
    with pytest.raises(HostOutputRejected, match="CANCELLED"):
        admit_response(b"invalid", request, window, clock=lambda: next(ticks),
                       observe=observer(window, [2, 5], cancellations=(False, True)))


@pytest.mark.parametrize("timestamp", [0, 4])
def test_stale_or_future_observation_is_rejected(subject, timestamp):
    request, window, raw = subject
    ticks = iter([1, 3])
    with pytest.raises(GatewayValidationError, match="HOST_OBSERVATION_STALE_OR_FUTURE"):
        admit_response(raw, request, window, clock=lambda: next(ticks),
                       observe=observer(window, [timestamp], cancellations=(False,), policies=(True,)))


@pytest.mark.parametrize("fault", ["clock", "observation_binding", "window_binding", "deadline_binding", "mutable_request"])
def test_invalid_host_or_invocation_binding_fails_closed(subject, fault):
    request, window, raw = subject
    observed_window = window
    ticks = iter([3, 1] if fault == "clock" else [1, 3, 4, 6])
    code = "HOST_INVOCATION_BINDING"
    if fault == "observation_binding":
        observed_window = replace(window, gateway_digest_sha256="a"*64)
        code = "HOST_OBSERVATION_BINDING"
    elif fault == "window_binding":
        window = replace(window, gateway_invocation_id="wrong")
    elif fault == "deadline_binding":
        window = replace(window, deadline_ns=window.deadline_ns+1)
    elif fault == "mutable_request":
        request.envelope.provider.model_id = "changed"
        code = "GATEWAY_DIGEST"
    else:
        code = "HOST_CLOCK_REGRESSION"
    with pytest.raises(GatewayValidationError, match=code):
        admit_response(raw, request, window, clock=lambda: next(ticks),
                       observe=observer(observed_window, [2, 5]))


def test_callback_latency_counts_toward_rejection(subject):
    request, window, raw = subject
    ticks = iter([1, window.deadline_ns+1])
    with pytest.raises(HostOutputRejected, match="TIMEOUT"):
        admit_response(raw, request, window, clock=lambda: next(ticks),
                       observe=observer(window, [2], cancellations=(False,), policies=(True,)))


def test_input_mutation_during_observation_cannot_replace_bound_request(subject):
    request, window, raw = subject
    ticks = iter([1, 3, 4, 6])
    actual = observer(window, [2, 5])

    def observe():
        request.envelope.provider.model_id = "mutation-after-copy"
        return actual()

    result = admit_response(raw, request, window, clock=lambda: next(ticks), observe=observe)
    assert result.gateway_digest_sha256 == window.gateway_digest_sha256


def test_observer_errors_are_sanitized_and_process_control_propagates(subject):
    request, window, raw = subject

    class OperationalFailure(Exception):
        def __str__(self):
            raise AssertionError("never format observer payload")

    def failed():
        raise OperationalFailure()

    with pytest.raises(GatewayValidationError, match="HOST_OBSERVATION_FAILED"):
        admit_response(raw, request, window, clock=lambda: 1, observe=failed)

    def stopped():
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        admit_response(raw, request, window, clock=lambda: 1, observe=stopped)


def test_window_is_immutable(subject):
    _, window, _ = subject
    with pytest.raises(FrozenInstanceError):
        window.deadline_ns = 10


def test_deadline_passed_during_validation_is_checked_again(subject, monkeypatch):
    request, window, raw = subject
    actual = admission.validate_response
    ticks = iter([1, 3, window.deadline_ns, window.deadline_ns])
    visited = []

    def validate(*args, **kwargs):
        visited.append(True)
        return actual(*args, **kwargs)

    monkeypatch.setattr(admission, "validate_response", validate)
    with pytest.raises(HostOutputRejected, match="TIMEOUT"):
        admit_response(raw, request, window, clock=lambda: next(ticks),
                       observe=observer(window, [2, window.deadline_ns]))
    assert visited == [True]


def test_observer_cannot_inject_error_text_using_validation_exception(subject):
    request, window, raw = subject

    def failed():
        raise GatewayValidationError("sensitive-observer-canary")

    with pytest.raises(GatewayValidationError) as caught:
        admit_response(raw, request, window, clock=lambda: 1, observe=failed)
    assert str(caught.value) == "HOST_OBSERVATION_FAILED"
    assert caught.value.__suppress_context__ is True


def test_validation_process_control_is_not_masked_by_second_observation(subject, monkeypatch):
    request, window, raw = subject
    ticks = iter([1, 3])

    def stopped(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(admission, "validate_response", stopped)
    with pytest.raises(KeyboardInterrupt):
        admit_response(raw, request, window, clock=lambda: next(ticks),
                       observe=observer(window, [2], cancellations=(False,), policies=(True,)))


@pytest.mark.parametrize("entry", ["begin", "admit"])
def test_mutated_request_rejection_does_not_emit_payload_warnings(subject, recwarn, capsys, entry):
    request, window, raw = subject
    request.envelope.provider.model_id = {"private": "sensitive-warning-canary"}
    with pytest.raises(GatewayValidationError):
        if entry == "begin":
            begin_window(request, clock=lambda: 0)
        else:
            admit_response(raw, request, window, clock=lambda: 1, observe=observer(window, [1, 1]))
    assert not recwarn
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("field", ["gateway_invocation_id", "gateway_digest_sha256"])
@pytest.mark.parametrize("entry", ["window", "observation"])
def test_malformed_host_identity_never_invokes_payload_equality(subject, field, entry):
    request, window, raw = subject

    class MalformedIdentity:
        def __eq__(self, other):
            raise AssertionError("sensitive-equality-canary")

    observed = HostObservation(window.gateway_invocation_id, window.gateway_digest_sha256, 1, False, True)
    if entry == "window":
        window = replace(window, **{field: MalformedIdentity()})
        code = "HOST_INVOCATION_BINDING"
    else:
        observed = replace(observed, **{field: MalformedIdentity()})
        code = "HOST_OBSERVATION_INVALID"
    with pytest.raises(GatewayValidationError, match=code):
        admit_response(raw, request, window, clock=lambda: 1, observe=lambda: observed)
