# WOLF15 Sentient — Algorithm Adoption Canon

Status: **DRAFT_RECONCILED — independent review pending**

This document summarizes the official adoption rule for all legacy algorithm donor batches.

It is **not a roadmap**. Checkpoint numbering, order and status are owned only
by the [root README](../../README.md#10-roadmap-master-cp0cp9);
[roadmap.md](roadmap.md) is its derived detail. This document may assign a
donor principle to one of those CPs but cannot create another checkpoint.

## Core decision

Legacy algorithms are **knowledge donors**, not runtime authorities.

The canonical transformation is:

```text
Legacy Donor
    ↓
Source Review
    ↓
Extract Generic Principle
    ↓
Map to Canonical WOLF15 Subsystem
    ↓
Assign Checkpoint Ownership
    ↓
Rebuild against Typed Contracts
    ↓
Evaluate
    ↓
Integrate only with required gates/evidence
```

## Canonical components extracted from all batches

### Reasoning and context

- Reasoning Plan Contract
- Reasoning Trace
- ReasoningProcedure / ReasoningProcedureDSL
- ConceptGraph / architecture context graph
- ProcedureSelector

### Control and runtime governance

- PolicyRuleEngine
- deterministic sequential gate cascade
- CircuitBreaker
- RetryEscalationGuard
- configuration/governance digest
- idempotency and replay identity

### Repository and integration

- RepositorySnapshotReader
- exact revision identity
- IntegrationManifest
- MultiRepoSyncReceipt
- ProviderAdapter / ProviderResult

### Capability Fabric

- ToolDescriptor
- CapabilityProvider
- CapabilityResolver
- provider compatibility metadata
- safe provider acquisition lifecycle
- duplicate/overlap classification

### Evidence, evaluation, and observability

- Assessment lineage
- Evidence-aware aggregation
- Telemetry Correlation Analyzer
- Runtime Saturation Detector
- Multi-Horizon Drift Analyzer
- Telemetry Persistence Analyzer
- Cognitive Disagreement Index
- ExplainableWeightedFusion
- InvarianceEvaluator
- DistributionImbalanceAnalyzer

### Learning / REE

- Episode Journal
- LearningPatternEvaluator
- Replay / Monte-Carlo evaluator
- TemporalGeneralizationEvaluator
- bounded candidate optimizer
- hysteresis/adaptive freeze

### Presentation / tools

- versioned ResponseProfile
- deterministic structured-data conversion tools
- ContractSurfaceValidator / ImportPreflight

## Domain separation

WOLF15 Sentient cognitive core does **not** absorb trading-specific decision logic, broker execution logic, lot sizing, SL/TP, prop-firm rules, market-specific thresholds, or market-specific psychological scoring.

Those algorithms may exist only in domain products/providers with separate qualification, authority, and evidence boundaries.

## Relationship to CP0

CP0 remains immutable historical acceptance at:

`bad73335f518d89356b88cba1cc26730808cd224`

This package is a documentation-only addendum and does not retroactively change CP0 acceptance evidence.

When merged later, the new `main` SHA may become the starting baseline for CP1 while the CP0 acceptance SHA remains unchanged.


## Ownership and review

See [canonical ownership](canonical-ownership.md) for ReasoningPlan/ModelGateway
roles and the [registry](../research/algorithm-donors/adoption-registry.yaml)
for 37 inactive designs. This reconciliation is not independent review or freeze.
