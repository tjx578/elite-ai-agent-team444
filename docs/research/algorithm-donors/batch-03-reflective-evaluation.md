# ARCH-ALG-03 — Reflective / Pipeline / Evaluation Algorithms

## Scope

Third donor batch: pipeline bridges, structured reasoning prompts, ETL/knowledge processing, reflective pattern reports, drift analysis, symmetry/invariance concepts, service bridges, background daemons, MCP routing, distribution/imbalance analysis, and reflective learning loops.

## Canonical conclusion

This batch is primarily useful for **pipeline contracts, deterministic tools, evaluation, observability, and learning candidates**. Live self-modification is rejected.

### Adopt / rebuild

- **PipelineStageContract** and per-stage receipts.
- **ReasoningProcedure** as a loadable skill/procedure.
- **KnowledgeIngestionPipeline**: validate → normalize → deduplicate → preserve provenance/conflict.
- **LearningPatternEvaluator**.
- **DriftAnalyzer**.
- **InvarianceEvaluator**.
- **DistributionImbalanceAnalyzer**.
- **ToolRegistry** / MCP descriptor concepts.
- **ServiceAdapter** with bounded timeout and typed result.
- **OutcomeEventTranslator**.
- **BackgroundJobRunner** with non-blocking scheduling and explicit failure state.
- **ProviderResult**.
- **MultiRepoSyncReceipt**.

### Required corrections

- No placeholder `True` counted as PASS.
- No default healthy values when data is missing.
- No direct `update_weights()` from a live task.
- No model update inside an online feedback loop.
- No blocking `time.sleep()` inside async workers.
- No comma-appended pseudo-JSON logs; use JSONL or durable storage.
- No fake Monte Carlo/Bayesian labels for non-equivalent math.
- No hash-derived fake coherence.
- No default `SYNCED` without verification.
- No first-source-wins knowledge conflict resolution.
- No unversioned provider/adapter contract.

## Checkpoint ownership

| Principle | Target | Checkpoint |
|---|---|---|
| PipelineStageContract / ReasoningProcedure | orchestration | CP1 |
| MultiRepoSyncReceipt | repositories | CP2 |
| ServiceAdapter / ProviderResult | integrations/models | CP3 |
| BackgroundJobRunner / observability | persistence/observability | CP3 |
| ToolRegistry / deterministic tools | tools/capabilities | CP5 |
| Provider compatibility qualification | Foundry | CP6 |
| Pattern/drift/invariance/distribution evaluation | evaluation/SCRS | CP8 |
| Outcome → candidate learning | learning/REE | CP8 |
