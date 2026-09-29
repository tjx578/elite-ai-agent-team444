# Algorithm to checkpoint matrix

DRAFT_RECONCILED: 31 package + four recovered + two explicit batch-supported
records. All 37 are inactive. View of [the registry](adoption-registry.yaml).

| ID | Algorithm | Checkpoint stages | Primary owner |
| --- | --- | --- | --- |
| ALG-REASON-PLAN-001 | ReasoningPlanContract | CP1: Checkpoint-owned behavior only; no later-stage activation | contracts |
| ALG-REASON-TRACE-001 | ReasoningTrace | CP1: Typed reasoning statuses and references; CP3: Durable traces; no hidden CoT | orchestration |
| ALG-CONCEPT-GRAPH-001 | ConceptGraph | CP1: Bounded task/context structure; CP2: Exact-revision repository dependency context | context |
| ALG-PROCEDURE-SELECTOR-001 | ProcedureSelector | CP1: Checkpoint-owned behavior only; no later-stage activation | orchestration |
| ALG-REPO-SNAPSHOT-001 | RepositorySnapshotReader | CP2: Checkpoint-owned behavior only; no later-stage activation | repositories |
| ALG-INTEGRATION-MANIFEST-001 | IntegrationManifest | CP2: Read-only exact-revision representation; CP5: Compatibility metadata | repositories |
| ALG-POLICY-RULES-001 | PolicyRuleEngine | CP3: Checkpoint-owned behavior only; no later-stage activation | control |
| ALG-GATE-CASCADE-001 | DeterministicGateCascade | CP3: Checkpoint-owned behavior only; no later-stage activation | control |
| ALG-CIRCUIT-BREAKER-001 | CircuitBreaker | CP3: Checkpoint-owned behavior only; no later-stage activation | control |
| ALG-RETRY-GUARD-001 | RetryEscalationGuard | CP3: Checkpoint-owned behavior only; no later-stage activation | control |
| ALG-EVENT-ENVELOPE-001 | SentientEvent | CP3: Typed durable event flow and replay identity; CP5: Capability events; no registry authority | contracts |
| ALG-SERVICE-ADAPTER-001 | ProviderAdapterResult | CP3: Checkpoint-owned behavior only; no later-stage activation | integrations |
| ALG-EPISODE-JOURNAL-001 | EpisodeJournal | CP3: Durable episode/audit facts; no learning activation; CP8: Outcome-linked evaluation input; no workflow state ownership | memory |
| ALG-RESPONSE-PROFILE-001 | ResponseProfile | CP4: Checkpoint-owned behavior only; no later-stage activation | sentient |
| ALG-TOOL-DESCRIPTOR-001 | ToolDescriptor | CP5: Checkpoint-owned behavior only; no later-stage activation | tools |
| ALG-CAPABILITY-PROVIDER-001 | CapabilityProviderDescriptor | CP5: Checkpoint-owned behavior only; no later-stage activation | capabilities |
| ALG-CAPABILITY-RESOLVER-001 | CapabilityResolver | CP5: Checkpoint-owned behavior only; no later-stage activation | capabilities |
| ALG-CONVERTER-TOOLS-001 | StructuredDataConversionToolpack | CP5: Checkpoint-owned behavior only; no later-stage activation | tools |
| ALG-SAFE-ACQUISITION-001 | SafeProviderAcquisition | CP6: Checkpoint-owned behavior only; no later-stage activation | capability_factory |
| ALG-CONTRACT-VALIDATOR-001 | ContractSurfaceValidator | CP3: Contract/import preflight; no qualification verdict; CP6: Foundry compatibility evaluation and independent qualification | evaluation |
| ALG-DRIFT-001 | DriftAnalyzer | CP8: Checkpoint-owned behavior only; no later-stage activation | sentient/cognition |
| ALG-MULTIHORIZON-STATE-001 | MultiHorizonStateAnalyzer | CP8: Checkpoint-owned behavior only; no later-stage activation | sentient/cognition |
| ALG-PERSISTENCE-001 | TelemetryPersistenceAnalyzer | CP8: Checkpoint-owned behavior only; no later-stage activation | sentient/cognition |
| ALG-DISAGREEMENT-001 | CognitiveDisagreementIndex | CP8: Checkpoint-owned behavior only; no later-stage activation | sentient/cognition |
| ALG-FUSION-EXPLAIN-001 | ExplainableWeightedFusion | CP5: Explainable lineage using fixed versioned criteria; no confidence claim; CP8: Calibrated fusion evaluated independently; no self-promotion | evaluation |
| ALG-HYSTERESIS-001 | StateTransitionHysteresis | CP8: Checkpoint-owned behavior only; no later-stage activation | sentient/cognition |
| ALG-REPLAY-EVAL-001 | ReplayMonteCarloEvaluator | CP8: Checkpoint-owned behavior only; no later-stage activation | evaluation |
| ALG-TEMPORAL-GEN-001 | TemporalGeneralizationEvaluator | CP8: Checkpoint-owned behavior only; no later-stage activation | evaluation |
| ALG-BOUNDED-OPT-001 | BoundedCandidateOptimizer | CP8: Checkpoint-owned behavior only; no later-stage activation | ree |
| ALG-INVARIANCE-001 | InvarianceEvaluator | CP8: Checkpoint-owned behavior only; no later-stage activation | evaluation |
| ALG-DISTRIBUTION-001 | DistributionImbalanceAnalyzer | CP8: Checkpoint-owned behavior only; no later-stage activation | observability |
| ALG-REASON-PROCEDURE-001 | ReasoningProcedure DSL | CP1: Checkpoint-owned behavior only; no later-stage activation | orchestration |
| ALG-MODEL-ADAPTER-001 | ProviderAdapter | CP1: One bounded real model provider behind the cognitive gateway; no service/capability activation | models/providers |
| ALG-PROCEDURE-SKILL-001 | Reasoning Procedure as Skill | CP5: Checkpoint-owned behavior only; no later-stage activation | skills |
| ALG-DUPLICATE-OVERLAP-001 | Duplicate/Overlap Detector | CP6: Checkpoint-owned behavior only; no later-stage activation | capability_factory |
| ALG-TELEMETRY-CORRELATION-001 | TelemetryCorrelationAnalyzer | CP3: Observe measured signals using fixed versioned reporting; no modulation; CP8: Evaluate adaptive interpretation/candidates after calibration; no independent actuation or self-promotion | observability |
| ALG-RUNTIME-SATURATION-001 | RuntimeSaturationDetector | CP3: Observe measured signals using fixed versioned reporting; no modulation; CP8: Evaluate adaptive interpretation/candidates after calibration; no independent actuation or self-promotion | observability |
