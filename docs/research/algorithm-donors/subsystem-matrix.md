# Algorithm to canonical subsystem matrix

DRAFT_RECONCILED. One primary owner per record. The Control Kernel retains
sole authority and workflow state ownership.

| ID | Algorithm | Primary owner | Collaborators |
| --- | --- | --- | --- |
| ALG-REASON-PLAN-001 | ReasoningPlanContract | contracts | orchestration, sentient |
| ALG-REASON-TRACE-001 | ReasoningTrace | orchestration | observability |
| ALG-CONCEPT-GRAPH-001 | ConceptGraph | context | knowledge |
| ALG-PROCEDURE-SELECTOR-001 | ProcedureSelector | orchestration | — |
| ALG-REPO-SNAPSHOT-001 | RepositorySnapshotReader | repositories | execution/repo_reader |
| ALG-INTEGRATION-MANIFEST-001 | IntegrationManifest | repositories | capabilities |
| ALG-POLICY-RULES-001 | PolicyRuleEngine | control | — |
| ALG-GATE-CASCADE-001 | DeterministicGateCascade | control | control/gates |
| ALG-CIRCUIT-BREAKER-001 | CircuitBreaker | control | execution |
| ALG-RETRY-GUARD-001 | RetryEscalationGuard | control | observability |
| ALG-EVENT-ENVELOPE-001 | SentientEvent | contracts | observability |
| ALG-SERVICE-ADAPTER-001 | ProviderAdapterResult | integrations | models |
| ALG-EPISODE-JOURNAL-001 | EpisodeJournal | memory | observability |
| ALG-RESPONSE-PROFILE-001 | ResponseProfile | sentient | personal |
| ALG-TOOL-DESCRIPTOR-001 | ToolDescriptor | tools | capabilities |
| ALG-CAPABILITY-PROVIDER-001 | CapabilityProviderDescriptor | capabilities | models, tools, mcp |
| ALG-CAPABILITY-RESOLVER-001 | CapabilityResolver | capabilities | — |
| ALG-CONVERTER-TOOLS-001 | StructuredDataConversionToolpack | tools | skills |
| ALG-SAFE-ACQUISITION-001 | SafeProviderAcquisition | capability_factory | capabilities |
| ALG-CONTRACT-VALIDATOR-001 | ContractSurfaceValidator | evaluation | capability_factory |
| ALG-DRIFT-001 | DriftAnalyzer | sentient/cognition | ree, evaluation |
| ALG-MULTIHORIZON-STATE-001 | MultiHorizonStateAnalyzer | sentient/cognition | observability |
| ALG-PERSISTENCE-001 | TelemetryPersistenceAnalyzer | sentient/cognition | observability |
| ALG-DISAGREEMENT-001 | CognitiveDisagreementIndex | sentient/cognition | evaluation |
| ALG-FUSION-EXPLAIN-001 | ExplainableWeightedFusion | evaluation | sentient/cognition |
| ALG-HYSTERESIS-001 | StateTransitionHysteresis | sentient/cognition | control |
| ALG-REPLAY-EVAL-001 | ReplayMonteCarloEvaluator | evaluation | ree |
| ALG-TEMPORAL-GEN-001 | TemporalGeneralizationEvaluator | evaluation | ree |
| ALG-BOUNDED-OPT-001 | BoundedCandidateOptimizer | ree | learning, evaluation |
| ALG-INVARIANCE-001 | InvarianceEvaluator | evaluation | — |
| ALG-DISTRIBUTION-001 | DistributionImbalanceAnalyzer | observability | evaluation |
| ALG-REASON-PROCEDURE-001 | ReasoningProcedure DSL | orchestration | sentient |
| ALG-MODEL-ADAPTER-001 | ProviderAdapter | models/providers | sentient/model_gateway, contracts |
| ALG-PROCEDURE-SKILL-001 | Reasoning Procedure as Skill | skills | orchestration |
| ALG-DUPLICATE-OVERLAP-001 | Duplicate/Overlap Detector | capability_factory | — |
| ALG-TELEMETRY-CORRELATION-001 | TelemetryCorrelationAnalyzer | observability | sentient/cognition, evaluation |
| ALG-RUNTIME-SATURATION-001 | RuntimeSaturationDetector | observability | sentient/cognition, evaluation |
