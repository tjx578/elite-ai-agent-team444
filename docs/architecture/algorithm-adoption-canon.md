# WOLF15 Sentient — Algorithm Adoption Canon

## Repository integration status

Imported from the owner-supplied proposed package. This document contributes
design guidance; the addendum is still DRAFT_INCOMPLETE. It grants no runtime
authority and does not establish historical source identity or qualification.
The existing canonical architecture and explicit task authorization continue
to govern implementation and repository actions.

Status: **PROPOSED CANONICAL ADDENDUM**

This document summarizes the official adoption rule for all legacy algorithm donor batches.

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


## Reconciled draft

See [registry status and provenance](../research/algorithm-donors/README.md).
The package narrative does not replace the [canonical ownership map](canonical-ownership.md).
