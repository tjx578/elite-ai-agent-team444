# SCRS observability contract

## Ownership and interfaces

CURRENT: `build_reasoning_observation` translates controller-owned
`ReasoningResult` into `CognitiveObservation`; callers supply event UUID,
sequence, aware timestamp and producer. `estimate_reflex_state` consumes that
observation, an explicit `CognitiveReflexProfile`, and optional latest prior
state, returning `CognitiveStateEstimate` for five scalar telemetry channels.

## Lifecycle and boundaries

The full immutable profile is SHA-256 bound. New events require contiguous
sequence, matching task/run/producer and nondecreasing time. Complete history
is retained for at most 1,024 events per run. Identical historical replay returns
current state unchanged; reused ID with different content is rejected. Caller
must retain and supply the latest state. This pure function provides no storage,
producer authentication or rollback-resistant ledger.

Missing metrics remain `NOT_MEASURED` or prediction-only when a prior exists.
State/covariance/innovation/gain are advisory, with calibration `UNVALIDATED`,
`modulation_authorized=false` and no authority or factual-truth effect. There
is no active workflow consumer, behavioral threshold, provider call or REE.

## Verification and target

Depends on [contracts](../contracts/README.md) and M3-A result types.
[SCRS tests](../../../tests/unit/test_cognitive_reflex.py) cover equations,
finite numbers, full-profile binding, replay and ordering. The
[SCRS design](../../../docs/architecture/m3a-cognitive-reflex-observability-v0.md)
defines encoding and limits. Future `sentient/cognition/` placement and calibrated
modulation require separate review. Any telemetry meaning, encoding, lifecycle
or profile change must review this README and its producer/consumer contracts.

[Canonical ownership](../../../docs/architecture/canonical-ownership.md)
decides global ownership; this README describes the local contract.
