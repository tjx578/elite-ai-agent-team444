# M3-A stacked experiment: Sentient Cognitive Reflex observability v0

## Status

This is a stacked, read-only experiment over the M3-A reasoning branch. It does
not change the existing HTTP endpoint, LangGraph workflow, task routing, model
adapter behavior, authority, memory, capability registry, or REE.

The design translates one narrow idea from the supplied CNRS reference material:
recursive state estimation under uncertainty. It does **not** copy trading
signals, lot/risk formulas, CONF12 weights, PASS/DEFENSIVE/WAIT/LOCK thresholds,
claimed performance numbers, or biological-consciousness language into WOLF15
Sentient.

The implementation name is **Sentient Cognitive Reflex System (SCRS)**. This
increment is only **Cognitive Reflex Observability v0**.

## Controller-derived observations

`build_reasoning_observation(result, observation_id=..., sequence=...,
observed_at=..., producer_id=...)` derives only facts already owned by the M3-A
controller. The caller supplies lifecycle metadata explicitly:

| Metric | v0 meaning |
| --- | --- |
| EVIDENCE_COVERAGE | usable M2 sources / declared M2 sources |
| CLAIM_ACCEPTANCE | non-rejected M2 claim assessments / assessed claims |
| CONFLICT_FREE | 1 only when a source set exists and M2 reports no conflict |
| PROPOSAL_CONTRACT_VALID | 1 only for M3-A PROPOSAL_VALIDATED |
| ADAPTER_OPERATIONAL | 0 only for M3-A ADAPTER_FAILED |

If a source or claim population does not exist, that metric is `NOT_MEASURED`;
it is not converted to zero. Proposal validation still proves schema, binding,
and reference checks only. Cognitive telemetry does not establish factual truth.

## Recursive estimator

The caller must provide an explicit `CognitiveReflexProfile`. There is no
runtime default because no SCRS profile is calibrated in M3-A.

The profile and its nested noise parameters are immutable. Each state binds
`profile_digest_sha256` to the complete validated profile, including schema,
labels, calibration status, all five Q/R/P0 parameter groups, and authority
effect. The v0 encoding is Python JSON with sorted keys, compact separators,
ASCII escaping, and non-finite values forbidden, hashed as UTF-8 with SHA-256.
This is a configuration identity, not a calibration or authenticity claim.
Updates require both matching labels and matching configuration digest.
Changing Q, R, or P0 under the same id/version is rejected. States from the
initial draft without this digest must be bootstrapped again; do not synthesize
a digest for history whose actual profile is unknown.

All estimator numeric fields require finite values. Existing interval and
positive-noise bounds still apply; NaN and either infinity are rejected when
validating profile, observation, or estimate contracts.

For each observed channel v0 applies an independent scalar Kalman update with
identity transition/observation models:

```text
P_pred = P_prev + Q
K      = P_pred / (P_pred + R)
innovation = y - x_pred
x_post = x_pred + K * innovation
P_post = (1 - K) * P_pred
```

The first actual measurement bootstraps its own prior mean rather than inventing
a neutral cognitive score. A missing measurement with prior state performs
prediction only and increases covariance; a missing measurement without prior
state remains `NOT_MEASURED`.

This diagonal v0 is intentionally smaller than a full correlated state-space
model. Cross-metric covariance, learned transition matrices, NIS calibration,
fusion, and threshold selection require representative task data and are not
claimed here.

## Authority boundary

Every observation/profile/state contract fixes:

```text
authority_effect = NONE
```

Every state estimate also fixes:

```text
advisory_only = true
modulation_authorized = false
factual_truth_effect = NONE
calibration_status = UNVALIDATED
```

Therefore a low covariance, high metric state, or any future fusion score cannot
grant WRITE authority, validate a factual claim, bypass review, select a tool,
activate a provider, or change the current task.

## Master checkpoint mapping

This file retains `M3-A` in its filename/title because it is a historical
implementation record. It does not define a roadmap.

- **CP0:** SCRS v0 is an accepted read-only advisory foundation slice.
- **CP1:** a real provider may add measured model/transport telemetry; SCRS
  remains observational.
- **CP3:** a future governor may consume calibrated state only to request deeper
  checks or hold work; Control Kernel remains authority.
- **CP8:** retrospective trajectory smoothing and adaptive candidates belong to
  offline Learning/REE and cannot rewrite historical events or the active task.

See the [Master Roadmap](roadmap.md).

## Acceptance boundary

`SCRS_OBSERVATION_LIFECYCLE = DEFINED_OFFLINE`. Each observation binds a UUID
`observation_id`, strict integer `sequence`, timezone-aware `observed_at`, and
nonblank `producer_id` together with task ID, run ID, input digest, and metrics.
The first event has sequence 1; a new event must have exactly the next sequence,
the same task/run/producer, and a nondecreasing event time. Equal timestamps are
allowed because sequence orders events. An old or skipped sequence with a new
ID is rejected. A known ID with changed payload is rejected.

The estimate contains the complete run-local history of event IDs, sequences,
and SHA-256 digests using the same canonical JSON encoding as the profile.
Replaying any recorded event with identical payload returns the current state
unchanged, including covariance and history. Profile binding is checked before
replay. The caller must pass the latest state; the pure function cannot detect
caller rollback or authenticate producer claims. These digests identify content
and are not signed attestations or proof of statistically independent samples.

V0 bounds a run to 1,024 observations and retains every replay receipt. It never
evicts history or wraps sequence. At the limit, a further new event is rejected;
a caller must explicitly start a different run without carrying over this prior
state. Repeated reasoning inputs can identify distinct observations, so input
digest alone is not used for deduplication. Callers must reuse an event's original
ID on retry. States missing lifecycle fields cannot resume; do not fabricate
history. State retention is caller-owned and no persistent storage is introduced.

CP1 provider telemetry integration remains future work. This contract does not
connect a provider, write memory, or change active workflow behavior. Merge
qualification requires CI, CodeQL, and independent review on the exact rebased
HEAD against main; earlier stacked runs do not substitute for those checks.

The unit tests require deterministic replay, explicit `NOT_MEASURED`, bounded
Kalman gain, covariance growth for prediction-only gaps, profile/run binding,
and proof that the cognitive layer has no authority or factual-truth effect.

Passing these tests would establish the local software contract only. It would
not establish calibrated cognitive metrics, live-model quality, production
readiness, or biological consciousness.
