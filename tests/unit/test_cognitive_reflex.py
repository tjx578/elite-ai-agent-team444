"""SCRS observability v0: deterministic, read-only cognitive state estimation."""

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID

import pytest
from pydantic import ValidationError

from wolf15_sentient.cognition import (
    build_reasoning_observation,
    estimate_reflex_state,
)
from wolf15_sentient.contracts.cognition import (
    CognitiveMetric,
    CognitiveMetricEstimate,
    CognitiveObservation,
    CognitiveReflexProfile,
    CognitiveStateEstimate,
    MetricNoiseProfile,
)
from wolf15_sentient.contracts.evidence import (
    ClaimType,
    EvidenceContextInput,
    EvidencePolicy,
    EvidenceStatus,
    GroundedClaim,
    SourceKind,
    SourceRef,
    SuppliedSource,
)
from wolf15_sentient.contracts.reasoning import (
    ReasoningInvocation,
    ReasoningRequest,
    ReasoningResult,
)
from wolf15_sentient.reasoning import run_reasoning


def request(with_claim: bool = True) -> ReasoningRequest:
    now = datetime(2026, 9, 29, tzinfo=UTC)
    content = "measured evidence"
    evidence = EvidenceContextInput(
        task_id=UUID(int=11),
        run_id=UUID(int=12),
        bundle_id=UUID(int=13),
        policy=EvidencePolicy(
            scope="cognitive-fixture",
            revision="v1",
            evaluated_at=now,
            max_age_seconds=60,
        ),
        source_refs=[
            SourceRef(
                source_id="doc",
                source_kind=SourceKind.DOCUMENT,
                locator="offline:cognitive-fixture",
                revision="v1",
                scope="cognitive-fixture",
                observed_at=now,
                digest_sha256=sha256(content.encode()).hexdigest(),
            )
        ],
        supplied_sources=[SuppliedSource(source_id="doc", content=content)],
        claims=(
            [
                GroundedClaim(
                    claim_id="c1",
                    text=content,
                    evidence_status=EvidenceStatus.SOURCE_CLAIM,
                    claim_type=ClaimType.FACT,
                    evidence_refs=["doc"],
                )
            ]
            if with_claim
            else []
        ),
    )
    return ReasoningRequest(intent="Jelaskan bukti ini", evidence=evidence)


def noise() -> MetricNoiseProfile:
    return MetricNoiseProfile(
        process_noise=0.05,
        observation_noise=0.20,
        initial_covariance=0.50,
    )


def profile(version: str = "test-v1") -> CognitiveReflexProfile:
    metric_noise = noise()
    return CognitiveReflexProfile(
        profile_id="unit-test-profile",
        version=version,
        evidence_coverage=metric_noise,
        claim_acceptance=metric_noise,
        conflict_free=metric_noise,
        proposal_contract_valid=metric_noise,
        adapter_operational=metric_noise,
    )


def observe(result: ReasoningResult, sequence: int = 1) -> CognitiveObservation:
    return build_reasoning_observation(
        result,
        observation_id=UUID(int=100 + sequence),
        sequence=sequence,
        observed_at=datetime(2026, 9, 29, tzinfo=UTC),
        producer_id="offline-test",
    )


def metric(
    state: CognitiveStateEstimate, name: CognitiveMetric
) -> CognitiveMetricEstimate:
    return next(item for item in state.metrics if item.metric is name)


def test_reasoning_observation_uses_controller_owned_facts() -> None:
    result = run_reasoning(request())
    observation = observe(result)

    assert observation.evidence_coverage == 1.0
    assert observation.claim_acceptance == 1.0
    assert observation.conflict_free == 1.0
    assert observation.proposal_contract_valid == 1.0
    assert observation.adapter_operational == 1.0
    assert observation.missing_metrics == []
    assert observation.authority_effect == "NONE"
    assert not observation.factual_truth_verified


def test_unmeasured_claim_metric_stays_explicit() -> None:
    result = run_reasoning(request(with_claim=False))
    observation = observe(result)

    assert observation.claim_acceptance is None
    assert observation.missing_metrics == [CognitiveMetric.CLAIM_ACCEPTANCE]


def test_adapter_failure_is_operational_signal_not_authority() -> None:
    class FailedAdapter:
        adapter_id = "failed-test"

        def generate(self, invocation: ReasoningInvocation) -> object:
            raise RuntimeError("private")

    result = run_reasoning(request(), FailedAdapter())
    observation = observe(result)

    assert observation.adapter_operational == 0.0
    assert observation.proposal_contract_valid == 0.0
    assert observation.authority_effect == "NONE"


def test_first_estimate_bootstraps_from_measurement_without_fake_prior_mean() -> None:
    observation = observe(run_reasoning(request()))
    state = estimate_reflex_state(observation, profile())

    evidence = metric(state, CognitiveMetric.EVIDENCE_COVERAGE)
    assert evidence.status == "MEASURED"
    assert evidence.observation == 1.0
    assert evidence.predicted_state == 1.0
    assert evidence.state == 1.0
    assert evidence.innovation == 0.0
    assert evidence.gain is not None
    assert 0.0 < evidence.gain < 1.0
    assert state.advisory_only
    assert not state.modulation_authorized
    assert state.authority_effect == "NONE"
    assert state.factual_truth_effect == "NONE"
    assert state.calibration_status == "UNVALIDATED"


def test_second_observation_is_smoothed_between_prior_and_measurement() -> None:
    first_observation = observe(run_reasoning(request()))
    first = estimate_reflex_state(first_observation, profile())

    second_observation = CognitiveObservation(
        observation_id=UUID(int=102),
        sequence=2,
        observed_at=first.observed_at,
        producer_id=first.producer_id,
        task_id=first.task_id,
        run_id=first.run_id,
        input_digest_sha256="1" * 64,
        evidence_coverage=0.0,
        claim_acceptance=0.0,
        conflict_free=0.0,
        proposal_contract_valid=0.0,
        adapter_operational=1.0,
        missing_metrics=[],
    )
    second = estimate_reflex_state(second_observation, profile(), first)
    evidence = metric(second, CognitiveMetric.EVIDENCE_COVERAGE)

    assert evidence.status == "MEASURED"
    assert evidence.state is not None
    assert 0.0 < evidence.state < 1.0
    assert evidence.innovation == -1.0


def test_missing_measurement_predicts_only_when_prior_exists() -> None:
    first_observation = observe(run_reasoning(request()))
    first = estimate_reflex_state(first_observation, profile())
    previous = metric(first, CognitiveMetric.CLAIM_ACCEPTANCE)
    assert previous.covariance is not None

    missing = CognitiveObservation(
        observation_id=UUID(int=102),
        sequence=2,
        observed_at=first.observed_at,
        producer_id=first.producer_id,
        task_id=first.task_id,
        run_id=first.run_id,
        input_digest_sha256="2" * 64,
        evidence_coverage=1.0,
        claim_acceptance=None,
        conflict_free=1.0,
        proposal_contract_valid=1.0,
        adapter_operational=1.0,
        missing_metrics=[CognitiveMetric.CLAIM_ACCEPTANCE],
    )
    second = estimate_reflex_state(missing, profile(), first)
    claim = metric(second, CognitiveMetric.CLAIM_ACCEPTANCE)

    assert claim.status == "PREDICTED_ONLY"
    assert claim.observation is None
    assert claim.state == previous.state
    assert claim.covariance is not None
    assert claim.covariance > previous.covariance


def test_missing_without_prior_remains_not_measured() -> None:
    observation = CognitiveObservation(
        observation_id=UUID(int=101),
        sequence=1,
        observed_at=datetime(2026, 9, 29, tzinfo=UTC),
        producer_id="offline-test",
        task_id=UUID(int=21),
        run_id=UUID(int=22),
        input_digest_sha256="3" * 64,
        evidence_coverage=None,
        claim_acceptance=None,
        conflict_free=None,
        proposal_contract_valid=1.0,
        adapter_operational=1.0,
        missing_metrics=[
            CognitiveMetric.EVIDENCE_COVERAGE,
            CognitiveMetric.CLAIM_ACCEPTANCE,
            CognitiveMetric.CONFLICT_FREE,
        ],
    )
    state = estimate_reflex_state(observation, profile())

    assert metric(state, CognitiveMetric.EVIDENCE_COVERAGE).status == "NOT_MEASURED"
    assert metric(state, CognitiveMetric.CLAIM_ACCEPTANCE).status == "NOT_MEASURED"
    assert metric(state, CognitiveMetric.CONFLICT_FREE).status == "NOT_MEASURED"


def test_previous_state_must_match_run_and_profile() -> None:
    observation = observe(run_reasoning(request()))
    first = estimate_reflex_state(observation, profile())

    wrong_run = CognitiveObservation(
        observation_id=UUID(int=102),
        sequence=2,
        observed_at=first.observed_at,
        producer_id=first.producer_id,
        task_id=first.task_id,
        run_id=UUID(int=999),
        input_digest_sha256="4" * 64,
        evidence_coverage=1.0,
        claim_acceptance=1.0,
        conflict_free=1.0,
        proposal_contract_valid=1.0,
        adapter_operational=1.0,
        missing_metrics=[],
    )
    with pytest.raises(ValueError, match="different task or run"):
        estimate_reflex_state(wrong_run, profile(), first)
    with pytest.raises(ValueError, match="different profile"):
        estimate_reflex_state(observation, profile("test-v2"), first)


def test_same_inputs_are_deterministic() -> None:
    observation = observe(run_reasoning(request()))
    first = estimate_reflex_state(observation, profile())
    second = estimate_reflex_state(observation, profile())

    assert first.model_dump_json() == second.model_dump_json()


@pytest.mark.parametrize(
    "channel", [metric.value.lower() for metric in CognitiveMetric]
)
@pytest.mark.parametrize(
    "parameter",
    [
        "process_noise",
        "observation_noise",
        "initial_covariance",
    ],
)
def test_previous_state_rejects_changed_parameters_with_same_labels(
    channel: str,
    parameter: str,
) -> None:
    observation = observe(run_reasoning(request()))
    original = profile()
    first = estimate_reflex_state(observation, original)
    changed = original.model_dump(mode="json")
    changed[channel][parameter] = 0.75
    replacement = CognitiveReflexProfile.model_validate(changed)
    assert (replacement.profile_id, replacement.version) == (
        original.profile_id,
        original.version,
    )
    with pytest.raises(ValueError, match="different profile configuration"):
        estimate_reflex_state(observation, replacement, first)


def test_profile_roundtrip_retains_digest_and_accepts_update() -> None:
    observation = observe(run_reasoning(request()))
    original = profile()
    first = estimate_reflex_state(observation, original)
    # Mapping insertion order is not part of the canonical configuration identity.
    reordered = dict(reversed(list(original.model_dump(mode="json").items())))
    restored = CognitiveReflexProfile.model_validate(reordered)
    second = estimate_reflex_state(
        observe(run_reasoning(request()), 2), restored, first
    )
    assert first.profile_digest_sha256 == second.profile_digest_sha256
    assert first.profile_digest_sha256 != first.input_digest_sha256


def test_old_state_without_profile_digest_is_rejected() -> None:
    observation = observe(run_reasoning(request()))
    data = estimate_reflex_state(observation, profile()).model_dump(mode="json")
    del data["profile_digest_sha256"]
    with pytest.raises(ValidationError, match="profile_digest_sha256"):
        CognitiveStateEstimate.model_validate(data)


def test_profile_and_nested_parameters_are_immutable() -> None:
    original = profile()
    with pytest.raises(ValidationError, match="frozen"):
        original.version = "changed"
    with pytest.raises(ValidationError, match="frozen"):
        original.evidence_coverage.process_noise = 0.9


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
@pytest.mark.parametrize(
    "field",
    [
        "observation",
        "predicted_state",
        "state",
        "innovation",
        "gain",
        "covariance",
    ],
)
def test_estimate_contract_rejects_nonfinite_numbers(field: str, value: float) -> None:
    observation = observe(run_reasoning(request()))
    state = estimate_reflex_state(observation, profile())
    data = state.model_dump(mode="python")
    data["metrics"][0][field] = value
    with pytest.raises(ValidationError, match="finite"):
        CognitiveStateEstimate.model_validate(data)


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
@pytest.mark.parametrize(
    "field",
    [
        "process_noise",
        "observation_noise",
        "initial_covariance",
    ],
)
def test_noise_contract_rejects_nonfinite_numbers(field: str, value: float) -> None:
    data = noise().model_dump(mode="python")
    data[field] = value
    with pytest.raises(ValidationError, match="finite"):
        MetricNoiseProfile.model_validate(data)


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
@pytest.mark.parametrize("field", [metric.value.lower() for metric in CognitiveMetric])
def test_observation_contract_rejects_nonfinite_numbers(
    field: str, value: float
) -> None:
    data = observe(run_reasoning(request())).model_dump(mode="python")
    data[field] = value
    with pytest.raises(ValidationError, match="finite"):
        CognitiveObservation.model_validate(data)


def test_replay_is_idempotent_even_after_later_observation() -> None:
    event = observe(run_reasoning(request()))
    first = estimate_reflex_state(event, profile())
    assert estimate_reflex_state(event, profile(), first) == first
    next_event = observe(run_reasoning(request()), 2)
    assert next_event.input_digest_sha256 == event.input_digest_sha256
    second = estimate_reflex_state(next_event, profile(), first)
    assert second.sequence == 2
    assert second.metrics != first.metrics
    assert estimate_reflex_state(event, profile(), second) == second
    assert estimate_reflex_state(next_event, profile(), second) == second


@pytest.mark.parametrize(
    "field,value",
    [
        ("evidence_coverage", 0.25),
        ("input_digest_sha256", "a" * 64),
        ("sequence", 2),
        ("producer_id", "another-producer"),
    ],
)
def test_reused_event_id_cannot_change_payload(field: str, value: object) -> None:
    event = observe(run_reasoning(request()))
    first = estimate_reflex_state(event, profile())
    data = event.model_dump(mode="python")
    data[field] = value
    with pytest.raises(ValueError):
        estimate_reflex_state(
            CognitiveObservation.model_validate(data), profile(), first
        )


@pytest.mark.parametrize("sequence", [1, 3])
def test_new_event_rejects_old_or_skipped_sequence(sequence: int) -> None:
    first = estimate_reflex_state(observe(run_reasoning(request())), profile())
    data = observe(run_reasoning(request()), sequence).model_dump(mode="python")
    data["observation_id"] = UUID(int=999)
    with pytest.raises(ValueError, match="next sequence"):
        estimate_reflex_state(
            CognitiveObservation.model_validate(data), profile(), first
        )


def test_bootstrap_requires_first_sequence() -> None:
    with pytest.raises(ValueError, match="sequence one"):
        estimate_reflex_state(observe(run_reasoning(request()), 2), profile())


def test_event_time_cannot_move_backwards() -> None:
    first = estimate_reflex_state(observe(run_reasoning(request())), profile())
    data = observe(run_reasoning(request()), 2).model_dump(mode="python")
    data["observed_at"] = first.observed_at - timedelta(seconds=1)
    with pytest.raises(ValueError, match="backwards"):
        estimate_reflex_state(
            CognitiveObservation.model_validate(data), profile(), first
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("sequence", 0),
        ("sequence", True),
        ("sequence", 1025),
        ("observed_at", "2026-09-29T00:00:00"),
        ("producer_id", " "),
    ],
)
def test_invalid_lifecycle_metadata_is_rejected(field: str, value: object) -> None:
    data = observe(run_reasoning(request())).model_dump(mode="python")
    data[field] = value
    with pytest.raises(ValidationError):
        CognitiveObservation.model_validate(data)


def test_history_cannot_be_truncated() -> None:
    first = estimate_reflex_state(observe(run_reasoning(request())), profile())
    second = estimate_reflex_state(
        observe(run_reasoning(request()), 2), profile(), first
    )
    data = second.model_dump(mode="python")
    data["observation_history"] = data["observation_history"][1:]
    with pytest.raises(ValidationError, match="contiguous"):
        CognitiveStateEstimate.model_validate(data)
