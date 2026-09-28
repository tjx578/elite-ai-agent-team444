"""Typed contracts for advisory-only Sentient Cognitive Reflex observability v0."""

from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, ConfigDict, Field, model_validator

from wolf15_sentient.contracts.evidence import Sha256
from wolf15_sentient.contracts.models import NonBlankText, StrictContract

UnitInterval = Annotated[float, Field(ge=0.0, le=1.0, allow_inf_nan=False)]
PositiveNoise = Annotated[float, Field(gt=0.0, le=10.0, allow_inf_nan=False)]
NonNegativeFloat = Annotated[float, Field(ge=0.0, allow_inf_nan=False)]
FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]
ObservationSequence = Annotated[int, Field(ge=1, le=1024, strict=True)]


class CognitiveMetric(StrEnum):
    EVIDENCE_COVERAGE = "EVIDENCE_COVERAGE"
    CLAIM_ACCEPTANCE = "CLAIM_ACCEPTANCE"
    CONFLICT_FREE = "CONFLICT_FREE"
    PROPOSAL_CONTRACT_VALID = "PROPOSAL_CONTRACT_VALID"
    ADAPTER_OPERATIONAL = "ADAPTER_OPERATIONAL"


class MetricNoiseProfile(StrictContract):
    """Explicit, uncalibrated scalar Kalman parameters for one metric."""

    model_config = ConfigDict(frozen=True)

    process_noise: PositiveNoise
    observation_noise: PositiveNoise
    initial_covariance: PositiveNoise


class CognitiveReflexProfile(StrictContract):
    """No default profile is supplied because M3-A has no calibrated thresholds."""

    model_config = ConfigDict(frozen=True)

    schema_version: Literal["scrs-profile-v0"] = "scrs-profile-v0"
    profile_id: NonBlankText
    version: NonBlankText
    calibration_status: Literal["UNVALIDATED"] = "UNVALIDATED"
    evidence_coverage: MetricNoiseProfile
    claim_acceptance: MetricNoiseProfile
    conflict_free: MetricNoiseProfile
    proposal_contract_valid: MetricNoiseProfile
    adapter_operational: MetricNoiseProfile
    authority_effect: Literal["NONE"] = "NONE"


class CognitiveObservation(StrictContract):
    """Controller-derived M3-A telemetry; none means genuinely not measured."""

    schema_version: Literal["scrs-observation-v0"] = "scrs-observation-v0"
    task_id: UUID
    run_id: UUID
    input_digest_sha256: Sha256
    observation_id: UUID
    sequence: ObservationSequence
    observed_at: AwareDatetime
    producer_id: NonBlankText
    evidence_coverage: UnitInterval | None = None
    claim_acceptance: UnitInterval | None = None
    conflict_free: UnitInterval | None = None
    proposal_contract_valid: UnitInterval
    adapter_operational: UnitInterval
    missing_metrics: list[CognitiveMetric] = Field(default_factory=list)
    source: Literal["M3A_CONTROLLER_DERIVED"] = "M3A_CONTROLLER_DERIVED"
    authority_effect: Literal["NONE"] = "NONE"
    factual_truth_verified: Literal[False] = False

    @model_validator(mode="after")
    def validate_missing_metrics(self) -> "CognitiveObservation":
        optional = {
            CognitiveMetric.EVIDENCE_COVERAGE: self.evidence_coverage,
            CognitiveMetric.CLAIM_ACCEPTANCE: self.claim_acceptance,
            CognitiveMetric.CONFLICT_FREE: self.conflict_free,
        }
        expected = {metric for metric, value in optional.items() if value is None}
        if set(self.missing_metrics) != expected:
            raise ValueError(
                "missing_metrics must exactly match unmeasured optional telemetry"
            )
        if len(self.missing_metrics) != len(set(self.missing_metrics)):
            raise ValueError("missing_metrics must be unique")
        return self


class CognitiveMetricEstimate(StrictContract):
    metric: CognitiveMetric
    status: Literal["MEASURED", "PREDICTED_ONLY", "NOT_MEASURED"]
    observation: UnitInterval | None = None
    predicted_state: UnitInterval | None = None
    state: UnitInterval | None = None
    innovation: FiniteFloat | None = None
    gain: UnitInterval | None = None
    covariance: NonNegativeFloat | None = None

    @model_validator(mode="after")
    def validate_status_shape(self) -> "CognitiveMetricEstimate":
        numeric = (
            self.predicted_state,
            self.state,
            self.covariance,
        )
        if self.status == "NOT_MEASURED":
            if self.observation is not None or any(
                value is not None for value in numeric
            ):
                raise ValueError("NOT_MEASURED cannot contain a state estimate")
            if self.innovation is not None or self.gain is not None:
                raise ValueError("NOT_MEASURED cannot contain filter diagnostics")
        elif self.status == "PREDICTED_ONLY":
            if self.observation is not None:
                raise ValueError("PREDICTED_ONLY cannot contain an observation")
            if any(value is None for value in numeric):
                raise ValueError(
                    "PREDICTED_ONLY requires predicted state and covariance"
                )
            if self.innovation is not None or self.gain is not None:
                raise ValueError("PREDICTED_ONLY cannot contain update diagnostics")
        else:
            if self.observation is None or any(value is None for value in numeric):
                raise ValueError("MEASURED requires observation, state, and covariance")
            if self.innovation is None or self.gain is None:
                raise ValueError("MEASURED requires innovation and gain")
        return self


class ObservationReceipt(StrictContract):
    """Run-local replay identity; caller retains this data without implicit I/O."""

    observation_id: UUID
    sequence: ObservationSequence
    digest_sha256: Sha256


class CognitiveStateEstimate(StrictContract):
    """Advisory estimate only; it cannot authorize routing, tools, or execution."""

    schema_version: Literal["scrs-state-v0"] = "scrs-state-v0"
    task_id: UUID
    run_id: UUID
    input_digest_sha256: Sha256
    observation_id: UUID
    sequence: ObservationSequence
    observed_at: AwareDatetime
    producer_id: NonBlankText
    observation_digest_sha256: Sha256
    observation_history: tuple[ObservationReceipt, ...] = Field(
        min_length=1, max_length=1024
    )
    profile_id: NonBlankText
    profile_version: NonBlankText
    profile_digest_sha256: Sha256
    calibration_status: Literal["UNVALIDATED"] = "UNVALIDATED"
    metrics: list[CognitiveMetricEstimate] = Field(min_length=5, max_length=5)
    advisory_only: Literal[True] = True
    modulation_authorized: Literal[False] = False
    authority_effect: Literal["NONE"] = "NONE"
    factual_truth_effect: Literal["NONE"] = "NONE"

    @model_validator(mode="after")
    def validate_metric_set(self) -> "CognitiveStateEstimate":
        history = self.observation_history
        if [item.sequence for item in history] != list(range(1, self.sequence + 1)):
            raise ValueError("observation history must be contiguous from sequence one")
        if len({item.observation_id for item in history}) != len(history):
            raise ValueError("observation history IDs must be unique")
        if (history[-1].observation_id, history[-1].digest_sha256) != (
            self.observation_id,
            self.observation_digest_sha256,
        ):
            raise ValueError("latest observation must match history")
        metrics = [item.metric for item in self.metrics]
        if len(metrics) != len(set(metrics)):
            raise ValueError("cognitive estimate metrics must be unique")
        if set(metrics) != set(CognitiveMetric):
            raise ValueError(
                "cognitive estimate must contain the complete v0 metric set"
            )
        return self


__all__ = [
    "CognitiveMetric",
    "CognitiveMetricEstimate",
    "CognitiveObservation",
    "CognitiveReflexProfile",
    "CognitiveStateEstimate",
    "MetricNoiseProfile",
    "ObservationReceipt",
]
