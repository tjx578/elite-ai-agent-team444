# Algorithm Adoption Matrix by Checkpoint

This file controls **when** extracted donor principles may be implemented. It does not change the existing CP0–CP9 roadmap; it overlays donor adoption onto that roadmap.

## CP0 — Cognitive Foundation Stabilized

Status: **CLOSED / PASS**.
No donor runtime implementation is added retroactively.

Allowed after closeout only as documentation addendum:
- donor registry;
- source provenance;
- anti-pattern registry;
- algorithm-to-checkpoint mapping.

## CP1 — Real Sentient Reasoning / M3-B

Allowed donor-derived implementation:
- `ReasoningPlan` contract.
- `ReasoningTrace`.
- `ReasoningProcedure` / declarative reasoning procedure.
- bounded `ModelGateway` adapter pattern.
- `ConceptGraph` only where necessary to structure task/context reasoning.
- procedure selection as advisory orchestration, never authority.

Forbidden in CP1:
- Capability Registry activation.
- repo mutation.
- Control Kernel redesign.
- self-learning.
- adaptive behavior modulation.

## CP2 — Repository Intelligence / M4

Allowed:
- `RepositorySnapshotReader`.
- exact SHA/ref resolution.
- repository/source graph and dependency context.
- `IntegrationManifest` read-only representation.
- `MultiRepoSyncReceipt` semantics where useful.

Forbidden:
- direct repository writes.
- branch-name-as-runtime-identity.
- donor repo code execution.

## CP3 — Production Grade v1 / M5

Allowed:
- `PolicyRuleEngine`.
- deterministic sequential gate cascade.
- `ProviderResult` and service adapters.
- `SentientEvent` with durable outbox/inbox.
- `CircuitBreaker`.
- `RetryEscalationGuard`.
- background job runner.
- episode/audit journal persistence.
- contract surface validation / import preflight as checks.
- telemetry correlation/saturation indicators.

Mandatory rule: these mechanisms may restrict or hold work; they may not increase task authority.

## CP4 — Personal JARVIS / M6

Allowed:
- pinned `ResponseProfile` / presentation profile.
- voice/UI interaction procedures.
- read-only personal connectors according to CP4 scope.

Forbidden:
- personality profile affecting facts, policy, evidence, or authority.

## CP5 — Capability OS / M7

Allowed:
- `ToolDescriptor`.
- `CapabilityProvider`.
- `CapabilityResolver`.
- provider health metadata.
- `ReasoningProcedure` as a Unified Skill provider.
- deterministic structured-data tools.
- MCP/tool registry as registry data, not authority.
- explainable provider/candidate assessment lineage.

## CP6 — Capability Foundry / M8

Allowed:
- safe provider acquisition lifecycle.
- exact donor SHA pinning.
- provenance/license/security checks.
- architecture analysis and extraction.
- duplicate/overlap classification.
- contract compatibility checks.
- sandbox evaluation.
- shadow qualification.

Forbidden:
- fetch → import → execute.
- direct candidate activation.
- donor order priority.

## CP7 — Controlled Builder / M9

Allowed:
- `GitHubMutationAdapter` under explicit Control Kernel approval.
- isolated worktree / feature branch workflows.
- proposal → patch → test → review → draft PR.
- approved personal actions with receipts.

Forbidden:
- direct main mutation.
- automatic merge/deploy.

## CP8 — Adaptive Intelligence / M10

Allowed after sufficient real telemetry/evaluation data exists:
- `MultiHorizonStateAnalyzer`.
- `DriftAnalyzer`.
- `TelemetryPersistenceAnalyzer`.
- `RuntimeSaturationDetector`.
- `CognitiveDisagreementIndex`.
- `ExplainableWeightedFusion`.
- hysteresis and adaptive freeze.
- replay/Monte-Carlo candidate evaluation.
- `TemporalGeneralizationEvaluator`.
- bounded candidate optimizer.
- retrospective smoothing / REE candidate lifecycle.

Mandatory lifecycle:

`Episode → Outcome → Candidate → Replay → Held-Out / Temporal Eval → Shadow → Owner Approval → Versioned Activation`

No candidate self-promotion.

## CP9 — Technology Company OS

No new donor principle bypasses earlier checkpoint contracts. CP9 integrates proven components; it is not permission to weaken authority, evidence, or evaluation boundaries.


## Reconciled repository status

DRAFT_RECONCILED. See [registry](adoption-registry.yaml) and [provenance](source-provenance.md).
Design guidance grants no runtime authority. Independent review and freeze remain separate.

The [record matrix](checkpoint-matrix.md) specifies stage slices. CP1 model
adapters and CP3 service adapters are distinct. CP3 preflight is not CP6
qualification; CP3 telemetry observes without CP8 adaptive behavior. CP5
registration, CP6 qualification and active capability are separate states.
