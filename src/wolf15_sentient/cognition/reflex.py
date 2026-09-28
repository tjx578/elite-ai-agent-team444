"""Read-only Sentient Cognitive Reflex observability over M3-A controller telemetry."""

import json
from datetime import datetime
from hashlib import sha256
from uuid import UUID

from wolf15_sentient.contracts.cognition import (
    CognitiveMetric,
    CognitiveMetricEstimate,
    CognitiveObservation,
    CognitiveReflexProfile,
    CognitiveStateEstimate,
    MetricNoiseProfile,
    ObservationReceipt,
)
from wolf15_sentient.contracts.evidence import ClaimOutcome
from wolf15_sentient.contracts.reasoning import ReasoningResult


def profile_digest(profile: CognitiveReflexProfile) -> str:
    """Bind all validated profile fields using the v0 canonical JSON encoding."""
    payload = json.dumps(
        profile.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def build_reasoning_observation(
    result: ReasoningResult,
    *,
    observation_id: UUID,
    sequence: int,
    observed_at: datetime,
    producer_id: str,
) -> CognitiveObservation:
    """Translate controller-owned M3-A facts into bounded observability metrics."""

    context = result.input.context
    source_count = len(context.source_assessments)
    usable_source_count = sum(item.usable for item in context.source_assessments)
    evidence_coverage = usable_source_count / source_count if source_count else None

    claim_count = len(context.claim_assessments)
    accepted_claim_count = sum(
        item.outcome is not ClaimOutcome.REJECTED for item in context.claim_assessments
    )
    claim_acceptance = accepted_claim_count / claim_count if claim_count else None

    conflict_free = None
    if source_count:
        conflict_free = 1.0 if not context.conflicts else 0.0

    missing: list[CognitiveMetric] = []
    if evidence_coverage is None:
        missing.append(CognitiveMetric.EVIDENCE_COVERAGE)
    if claim_acceptance is None:
        missing.append(CognitiveMetric.CLAIM_ACCEPTANCE)
    if conflict_free is None:
        missing.append(CognitiveMetric.CONFLICT_FREE)

    return CognitiveObservation(
        observation_id=observation_id,
        sequence=sequence,
        observed_at=observed_at,
        producer_id=producer_id,
        task_id=result.input.task_id,
        run_id=result.input.run_id,
        input_digest_sha256=result.input_digest_sha256,
        evidence_coverage=evidence_coverage,
        claim_acceptance=claim_acceptance,
        conflict_free=conflict_free,
        proposal_contract_valid=1.0 if result.status == "PROPOSAL_VALIDATED" else 0.0,
        adapter_operational=0.0 if result.status == "ADAPTER_FAILED" else 1.0,
        missing_metrics=missing,
    )


def _measurement(
    observation: CognitiveObservation, metric: CognitiveMetric
) -> float | None:
    if metric is CognitiveMetric.EVIDENCE_COVERAGE:
        return observation.evidence_coverage
    if metric is CognitiveMetric.CLAIM_ACCEPTANCE:
        return observation.claim_acceptance
    if metric is CognitiveMetric.CONFLICT_FREE:
        return observation.conflict_free
    if metric is CognitiveMetric.PROPOSAL_CONTRACT_VALID:
        return observation.proposal_contract_valid
    return observation.adapter_operational


def _noise(
    profile: CognitiveReflexProfile, metric: CognitiveMetric
) -> MetricNoiseProfile:
    if metric is CognitiveMetric.EVIDENCE_COVERAGE:
        return profile.evidence_coverage
    if metric is CognitiveMetric.CLAIM_ACCEPTANCE:
        return profile.claim_acceptance
    if metric is CognitiveMetric.CONFLICT_FREE:
        return profile.conflict_free
    if metric is CognitiveMetric.PROPOSAL_CONTRACT_VALID:
        return profile.proposal_contract_valid
    return profile.adapter_operational


def _previous_metric(
    previous: CognitiveStateEstimate | None,
    metric: CognitiveMetric,
) -> CognitiveMetricEstimate | None:
    if previous is None:
        return None
    return next(item for item in previous.metrics if item.metric is metric)


def _estimate_metric(
    metric: CognitiveMetric,
    measurement: float | None,
    noise: MetricNoiseProfile,
    previous: CognitiveMetricEstimate | None,
) -> CognitiveMetricEstimate:
    previous_state = previous.state if previous is not None else None
    previous_covariance = previous.covariance if previous is not None else None

    if measurement is None and (previous_state is None or previous_covariance is None):
        return CognitiveMetricEstimate(metric=metric, status="NOT_MEASURED")

    if previous_state is None or previous_covariance is None:
        # Bootstrap from the first actual observation instead of inventing a prior mean.
        predicted_state = measurement
        prior_covariance = noise.initial_covariance
    else:
        predicted_state = previous_state
        prior_covariance = previous_covariance

    if predicted_state is None:
        return CognitiveMetricEstimate(metric=metric, status="NOT_MEASURED")

    predicted_covariance = prior_covariance + noise.process_noise
    if measurement is None:
        return CognitiveMetricEstimate(
            metric=metric,
            status="PREDICTED_ONLY",
            predicted_state=predicted_state,
            state=predicted_state,
            covariance=predicted_covariance,
        )

    gain = predicted_covariance / (predicted_covariance + noise.observation_noise)
    innovation = measurement - predicted_state
    state = predicted_state + gain * innovation
    posterior_covariance = (1.0 - gain) * predicted_covariance
    state = min(1.0, max(0.0, state))

    return CognitiveMetricEstimate(
        metric=metric,
        status="MEASURED",
        observation=measurement,
        predicted_state=predicted_state,
        state=state,
        innovation=innovation,
        gain=gain,
        covariance=posterior_covariance,
    )


def estimate_reflex_state(
    observation: CognitiveObservation,
    profile: CognitiveReflexProfile,
    previous: CognitiveStateEstimate | None = None,
) -> CognitiveStateEstimate:
    """Apply independent scalar Kalman updates without changing runtime behavior."""

    # Revalidate detached snapshots, including mutable nested state/observations.
    observation = CognitiveObservation.model_validate(
        observation.model_dump(mode="python")
    )
    profile = CognitiveReflexProfile.model_validate(profile.model_dump(mode="python"))
    if previous is not None:
        previous = CognitiveStateEstimate.model_validate(
            previous.model_dump(mode="python")
        )
    digest = profile_digest(profile)
    event_digest = sha256(
        json.dumps(
            observation.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    history: tuple[ObservationReceipt, ...] = ()
    if previous is not None:
        if (previous.task_id, previous.run_id) != (
            observation.task_id,
            observation.run_id,
        ):
            raise ValueError(
                "previous cognitive state belongs to a different task or run"
            )
        if (previous.profile_id, previous.profile_version) != (
            profile.profile_id,
            profile.version,
        ):
            raise ValueError("previous cognitive state uses a different profile")
        if previous.profile_digest_sha256 != digest:
            raise ValueError(
                "previous cognitive state uses a different profile configuration"
            )
        if previous.producer_id != observation.producer_id:
            raise ValueError("observation producer cannot change within a run")
        history = previous.observation_history
        recorded = next(
            (
                item
                for item in history
                if item.observation_id == observation.observation_id
            ),
            None,
        )
        if recorded is not None:
            if recorded.digest_sha256 != event_digest:
                raise ValueError("observation ID reused with different payload")
            return previous
        if observation.sequence != previous.sequence + 1:
            raise ValueError("new observation must have the next sequence")
        if observation.observed_at < previous.observed_at:
            raise ValueError("observation time cannot move backwards")
    elif observation.sequence != 1:
        raise ValueError("first observation must have sequence one")

    estimates = [
        _estimate_metric(
            metric,
            _measurement(observation, metric),
            _noise(profile, metric),
            _previous_metric(previous, metric),
        )
        for metric in CognitiveMetric
    ]
    return CognitiveStateEstimate(
        observation_id=observation.observation_id,
        sequence=observation.sequence,
        observed_at=observation.observed_at,
        producer_id=observation.producer_id,
        observation_digest_sha256=event_digest,
        observation_history=history
        + (
            ObservationReceipt(
                observation_id=observation.observation_id,
                sequence=observation.sequence,
                digest_sha256=event_digest,
            ),
        ),
        task_id=observation.task_id,
        run_id=observation.run_id,
        input_digest_sha256=observation.input_digest_sha256,
        profile_id=profile.profile_id,
        profile_version=profile.version,
        profile_digest_sha256=digest,
        metrics=estimates,
    )


__all__ = ["build_reasoning_observation", "estimate_reflex_state", "profile_digest"]
