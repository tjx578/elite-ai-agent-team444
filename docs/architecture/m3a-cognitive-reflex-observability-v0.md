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

`build_reasoning_observation(ReasoningResult)` derives only facts already owned
by the M3-A controller:

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

## Roadmap mapping

- **M3-A / this stacked increment:** observe controller-owned reasoning/evidence
  telemetry and produce an advisory recursive estimate.
- **M3-B:** a real provider may add measured transport/model telemetry, but SCRS
  remains observational unless a separate reviewed increment changes that.
- **M5:** a future Cognitive Modulation Governor may consume calibrated state to
  request deeper checks or hold work; hard policy remains owned by the Kernel.
- **M10:** retrospective trajectory smoothing (including an RTS-style candidate)
  belongs with offline Learning/REE and cannot rewrite historical events or the
  active task.

No automatic fusion weights, behavioral thresholds, reflective mutation, or
promotion mechanism are included in this change.

## Acceptance boundary

The unit tests require deterministic replay, explicit `NOT_MEASURED`, bounded
Kalman gain, covariance growth for prediction-only gaps, profile/run binding,
and proof that the cognitive layer has no authority or factual-truth effect.

Passing these tests would establish the local software contract only. It would
not establish calibrated cognitive metrics, live-model quality, production
readiness, or biological consciousness.
