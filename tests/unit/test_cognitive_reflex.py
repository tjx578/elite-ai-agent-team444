"""SCRS observability v0: deterministic, read-only cognitive state estimation."""

from datetime import UTC, datetime
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


def metric(
    state: CognitiveStateEstimate, name: CognitiveMetric
) -> CognitiveMetricEstimate:
    return next(item for item in state.metrics if item.metric is name)


def test_reasoning_observation_uses_controller_owned_facts() -> None:
    result = run_reasoning(request())
    observation = build_reasoning_observation(result)

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
    observation = build_reasoning_observation(result)

    assert observation.claim_acceptance is None
    assert observation.missing_metrics == [CognitiveMetric.CLAIM_ACCEPTANCE]


def test_adapter_failure_is_operational_signal_not_authority() -> None:
    class FailedAdapter:
        adapter_id = "failed-test"

        def generate(self, invocation: ReasoningInvocation) -> object:
            raise RuntimeError("private")

    result = run_reasoning(request(), FailedAdapter())
    observation = build_reasoning_observation(result)

    assert observation.adapter_operational == 0.0
    assert observation.proposal_contract_valid == 0.0
    assert observation.authority_effect == "NONE"


def test_first_estimate_bootstraps_from_measurement_without_fake_prior_mean() -> None:
    observation = build_reasoning_observation(run_reasoning(request()))
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
    first_observation = build_reasoning_observation(run_reasoning(request()))
    first = estimate_reflex_state(first_observation, profile())

    second_observation = CognitiveObservation(
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
    first_observation = build_reasoning_observation(run_reasoning(request()))
    first = estimate_reflex_state(first_observation, profile())
    previous = metric(first, CognitiveMetric.CLAIM_ACCEPTANCE)
    assert previous.covariance is not None

    missing = CognitiveObservation(
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
    observation = build_reasoning_observation(run_reasoning(request()))
    first = estimate_reflex_state(observation, profile())

    wrong_run = CognitiveObservation(
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
    observation = build_reasoning_observation(run_reasoning(request()))
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
    observation = build_reasoning_observation(run_reasoning(request()))
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
    observation = build_reasoning_observation(run_reasoning(request()))
    original = profile()
    first = estimate_reflex_state(observation, original)
    # Mapping insertion order is not part of the canonical configuration identity.
    reordered = dict(reversed(list(original.model_dump(mode="json").items())))
    restored = CognitiveReflexProfile.model_validate(reordered)
    second = estimate_reflex_state(observation, restored, first)
    assert first.profile_digest_sha256 == second.profile_digest_sha256
    assert first.profile_digest_sha256 != first.input_digest_sha256


def test_old_state_without_profile_digest_is_rejected() -> None:
    observation = build_reasoning_observation(run_reasoning(request()))
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
    observation = build_reasoning_observation(run_reasoning(request()))
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
    data = build_reasoning_observation(run_reasoning(request())).model_dump(
        mode="python"
    )
    data[field] = value
    with pytest.raises(ValidationError, match="finite"):
        CognitiveObservation.model_validate(data)
