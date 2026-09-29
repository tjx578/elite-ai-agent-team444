# ARCH-ALG-05 — Reasoning Graph / Policy Guard / Temporal Evaluation / Explainable Fusion

## Scope

Fifth donor batch: advanced reasoning frameworks, mind-map engines, knowledge graphs, policy/psychology-control code, deterministic verdict cascades, VIX/regime code, volatility clustering, walk-forward validation, VPCE/context gates, and explainable weighted fusion.

## Canonical conclusion

This batch is especially important for **ConceptGraph, PolicyRuleEngine, CircuitBreaker/RetryEscalationGuard, TemporalGeneralizationEvaluator, TelemetryPersistenceAnalyzer, and ExplainableWeightedFusion**.

### Adopt / rebuild

- **ConceptGraph** for architecture/knowledge/repository dependency context.
- **ReasoningProcedureDSL** with typed declarative steps; arbitrary Python callables are prohibited.
- **PolicyRuleEngine** with criticality and fail-closed semantics.
- **CircuitBreaker** with explicit reason, severity, cooldown/resume criteria.
- **RetryEscalationGuard** for repeated failures, rapid retries, or widening mutation scope after failure.
- **TemporalGeneralizationEvaluator** based on walk-forward/held-out windows.
- **TelemetryPersistenceAnalyzer** for clustered error/latency/failure behavior.
- **ExplainableWeightedFusion** with component contributions; do not call it probability/confidence until calibrated.
- **IntegrationManifest** pinned to exact revision.
- **ContractSurfaceValidator**.
- **ImportPreflight** as one readiness input, not a readiness verdict.
- **ContextAdmissibilityAssessment** separated from Control Kernel authorization.

### Critical defects to prevent

- Graph size must never create confidence.
- Missing policy inputs cannot default to `True`.
- Critical rule failure cannot be overridden by aggregate score.
- Missing evidence cannot trigger automatic correction/mutation.
- Mutable branch names such as `main` cannot be runtime identity.
- `SYNCED` requires verified sync state, not only local logging.
- Synthetic data must be labeled `SIMULATED`/`ASSUMPTION`.
- Cognitive/meta score cannot grant authority.
- Failed mandatory gate cannot result in reduced execution.
- Import smoke test is not production readiness.
- Avoid unbounded `all_simple_paths` on large graphs.
- Active configuration must be immutable/digested; avoid shallow-copy mutation.
- Calculated scores are not calibrated confidence unless independently validated.

## Checkpoint ownership

| Principle | Target | Checkpoint |
|---|---|---|
| ConceptGraph / ReasoningProcedureDSL | context/knowledge/orchestration | CP1/CP2 |
| IntegrationManifest | repositories/capabilities | CP2/CP5 |
| PolicyRuleEngine / CircuitBreaker / RetryEscalationGuard | control/observability | CP3 |
| ContractSurfaceValidator / ImportPreflight | evaluation/runtime | CP3/CP6 |
| ExplainableWeightedFusion | evaluation | CP5/CP8 |
| TemporalGeneralizationEvaluator | evaluation/REE | CP8 |
| TelemetryPersistenceAnalyzer | observability/SCRS | CP8 |
