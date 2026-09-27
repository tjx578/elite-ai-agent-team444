# WOLF15 Neuro Network Research Corpus

## Status

- Corpus match: STRONG_MATCH
- Exact NotebookLM membership: NOT_ESTABLISHED
- Source access: private Google Drive research corpus
- Ingestion date: 2026-09-28
- Repository integration base: `624d5ab579290b13805c13a1f1e69b9925b2a6c1`
- Runtime activation: NOT_EXECUTED

The Google Drive connector does not expose NotebookLM notebook membership. The title supplied by the owner, "WOLF15 neuro NETWORK", resolved to a coherent private research folder containing 61 related artifacts. This document registers that corpus without publishing private Drive file IDs or URLs.

## Corpus shape

- pdf: 2
- other: 4
- markdown: 24
- presentation: 2
- archive: 1
- python: 26
- image: 2

## Source precedence used for integration

1. `WOLF15_SELF_LEARNING_NETWORK_FINAL_KNOWLEDGE_V1.0_ID.md` — consolidated knowledge candidate and final disposition.
2. `WOLF15_SELF_LEARNING_NETWORK_ARCHITECTURE_V4.0_ID.md` — detailed architecture, contracts, quality attributes, roadmap, and simulator audit.
3. `WOLF15_MASTER_GOAP_EXECUTION_PLAN_V4.0_ID.md` — implementation ordering, invariants, gates, and test strategy.
4. `authority-model.md`, `evidence-contract.md`, `decision-envelope.md`, and `pipeline-contract.md` — authority/evidence semantics.
5. `tuyul-neural-orchestrator-skill-v2.md` and `tuyul-network-blueprint-v2.md` — legacy capability and topology sources.
6. Simulators, connectors, tests, dashboards, and topology assets — implementation references or negative fixtures; not production proof.

Lower-precedence sources cannot silently override higher-precedence authority or evidence rules.

## Knowledge adopted into WOLF15 Sentient

The research contributes the following generic architecture patterns after removing trading-specific semantics:

| Research concept | Sentient adoption | Status |
| --- | --- | --- |
| Separate active and background loops | Control Kernel / Task Runtime separated from Learning & Adaptation Plane | ADOPT |
| Five-node learning loop | Task evidence -> Experience Journal -> Learning Orchestrator + Domain Knowledge -> Adaptive Memory | ADOPT_WITH_REMAP |
| Signed/versioned facts | Immutable source/evidence bindings with digest, revision, observed time, and typed claims | ADOPT |
| Frozen dataset / as-of knowledge | Immutable evaluation corpus and versioned knowledge generation | ADOPT |
| Operators Memory | Bounded typed run state plus artifact references; no raw hidden reasoning | ADOPT_WITH_REDESIGN |
| Capability registry/discovery | Repository/capability inventory that never grants authority by discovery alone | ADOPT |
| Async learning | Optional background learning that cannot block the baseline task path | ADOPT |
| Candidate lifecycle | DRAFT -> OFFLINE_EVALUATED -> SHADOW -> APPROVAL_PENDING -> ACTIVE_WORKFLOW | ADOPT |
| Independent gates | Evidence, authority, security, replay, regression, resource, and approval remain separate | ADOPT |
| A2Flow/MCTS | Offline workflow/retrieval/resource optimization candidates only | HOLD_OFFLINE_ONLY |
| Redis shared state as truth | Not canonical; at most cache/lease/test double | REJECT_AS_CANONICAL |
| Single Truth Score release authority | Replaced by independent gates and real receipts | REJECT |
| Raw reasoning trajectory memory | Structured evidence/decision summaries only | REJECT |
| Self-promotion / automatic authority change | Candidate producer cannot activate itself or raise task authority | REJECT |

## Capability extraction

The corpus yields capability candidates in these families:

- evidence and provenance management;
- bounded working/episodic/semantic/procedural/audit memory;
- asynchronous experience journaling;
- deterministic replay and idempotency;
- capability/node discovery with health and version bindings;
- routing and aggregation for non-authoritative work;
- conflict preservation and partial-failure handling;
- offline workflow topology optimization;
- candidate/evaluation/champion-challenger lifecycle;
- multi-repository exact-revision governance;
- negative/fuzz testing for authority smuggling;
- resilience tests for duplicate, delay, out-of-order, partition, and stale evidence;
- structured audit envelopes and claim labeling.

These are capability candidates, not claims that the current runtime already provides them.

## Complete registered source inventory

| # | Source title | Kind | Registration |
| ---: | --- | --- | --- |
| 1 | WOLF15_TUYUL_Cybernetic_Blueprint.pdf | pdf | REGISTERED_SOURCE |
| 2 | wolf15_ssot_config.yaml | other | REGISTERED_SOURCE |
| 3 | WOLF15_SELF_LEARNING_NETWORK_FINAL_KNOWLEDGE_V1.0_ID.md | markdown | REGISTERED_SOURCE |
| 4 | WOLF15_SELF_LEARNING_NETWORK_ARCHITECTURE_V4.0_ID.md | markdown | REGISTERED_SOURCE |
| 5 | WOLF15_Secure_Cognitive_Architecture.pptx | presentation | REGISTERED_SOURCE |
| 6 | WOLF15_Secure_Cognitive_Architecture.pdf | pdf | REGISTERED_SOURCE |
| 7 | WOLF15_PETA_TERPADU_5SCR_EA_DUMB_2026-08-26.md | markdown | REGISTERED_SOURCE |
| 8 | WOLF15_MASTER_GOAP_EXECUTION_PLAN_V4.0_ID.md | markdown | REGISTERED_SOURCE |
| 9 | WOLF15 Self-Learning Network_ Rancangan Perbaikan Komprehensif & Cetak Biru Kognitif v3.0.md | markdown | REGISTERED_SOURCE |
| 10 | wolf-arsenal-toolkit.zip | archive | REGISTERED_SOURCE |
| 11 | wolf-arsenal-toolkit.md | markdown | REGISTERED_SOURCE |
| 12 | wolf-arsenal-toolkit-v2.md | markdown | REGISTERED_SOURCE |
| 13 | visualize_network_topology.py | python | REGISTERED_SOURCE |
| 14 | visualize_network_topology (1).py | python | REGISTERED_SOURCE |
| 15 | verify_wolf_metrics.py | python | REGISTERED_SOURCE |
| 16 | validate_audit_envelope.py | python | REGISTERED_SOURCE |
| 17 | TUYUL_V2_Autonomous_Architecture.pptx | presentation | REGISTERED_SOURCE |
| 18 | tuyul_network_topology.png | image | REGISTERED_SOURCE |
| 19 | tuyul_l8_engine.py | python | REGISTERED_SOURCE |
| 20 | tuyul_l8_engine-v2.py | python | REGISTERED_SOURCE |
| 21 | tuyul_dashboard_logger.py | python | REGISTERED_SOURCE |
| 22 | tuyul-self-learning-rebuild-design.md | markdown | REGISTERED_SOURCE |
| 23 | tuyul-self-learning-rebuild-design (1).md | markdown | REGISTERED_SOURCE |
| 24 | tuyul-neural-orchestrator-skill-v2.md | markdown | REGISTERED_SOURCE |
| 25 | tuyul-network-blueprint-v2.md | markdown | REGISTERED_SOURCE |
| 26 | tuyul-mindmap-reasoning-skill-v5.md | markdown | REGISTERED_SOURCE |
| 27 | tuyul-mindmap-reasoning-skill-v5-v2.md | markdown | REGISTERED_SOURCE |
| 28 | tuyul-mindmap-engine-v5-v6.py | python | REGISTERED_SOURCE |
| 29 | tuyul-mindmap-engine-v5-v5.py | python | REGISTERED_SOURCE |
| 30 | tuyul-mindmap-engine-v5-v4.py | python | REGISTERED_SOURCE |
| 31 | tuyul-mindmap-engine-v5-v3.py | python | REGISTERED_SOURCE |
| 32 | tuyul-mindmap-engine-v5-v2.py | python | REGISTERED_SOURCE |
| 33 | tuyul-cognitive-stress-test-report.md | markdown | REGISTERED_SOURCE |
| 34 | tuyul-cognitive-stress-test-report-v2.md | markdown | REGISTERED_SOURCE |
| 35 | TUYLFX SKILL.md | markdown | REGISTERED_SOURCE |
| 36 | test_tuyul_connections.py | python | REGISTERED_SOURCE |
| 37 | test_self_learning_v3.py | python | REGISTERED_SOURCE |
| 38 | test_provenance_and_integrity.py | python | REGISTERED_SOURCE |
| 39 | test_network_partition.py | python | REGISTERED_SOURCE |
| 40 | SKILL (1).md | markdown | REGISTERED_SOURCE |
| 41 | simulate_self_learning_loop.py | python | REGISTERED_SOURCE |
| 42 | simulate_self_learning_loop-v3.py | python | REGISTERED_SOURCE |
| 43 | simulate_self_learning_loop-v2.py | python | REGISTERED_SOURCE |
| 44 | simulate_mcts_wolf15_v2.py | python | REGISTERED_SOURCE |
| 45 | simulate_mcts_wolf15.py | python | REGISTERED_SOURCE |
| 46 | selflearning.png | image | REGISTERED_SOURCE |
| 47 | run_all_tests.sh | other | REGISTERED_SOURCE |
| 48 | run_all_tests-v3.sh | other | REGISTERED_SOURCE |
| 49 | run_all_tests-v3 (1).sh | other | REGISTERED_SOURCE |
| 50 | pipeline-contract.md | markdown | REGISTERED_SOURCE |
| 51 | neural_orchestrator.py | python | REGISTERED_SOURCE |
| 52 | neural_orchestrator-v9.py | python | REGISTERED_SOURCE |
| 53 | neural_orchestrator-v8.py | python | REGISTERED_SOURCE |
| 54 | neural_orchestrator-v4.py | python | REGISTERED_SOURCE |
| 55 | neural_connector-v2.py | python | REGISTERED_SOURCE |
| 56 | Langkah Nyata WOLF15 Menuju LIVE DEMO.md | markdown | REGISTERED_SOURCE |
| 57 | evidence-contract.md | markdown | REGISTERED_SOURCE |
| 58 | decision-envelope.md | markdown | REGISTERED_SOURCE |
| 59 | authority-model.md | markdown | REGISTERED_SOURCE |
| 60 | Arsitektur Kognitif Bayesian dan Memori Operator A2Flow.md | markdown | REGISTERED_SOURCE |
| 61 | 15-WOLF15_SELF_LEARNING_NETWORK_ARCHITECTURE_V4.0_ID.md | markdown | REGISTERED_SOURCE |
