# CP1.1 prohibition matrix

Status: DESIGN_RECONCILIATION / NOT_RUNTIME_QUALIFICATION. All restrictions below are normative for the native candidate. A clause or schema PASS does not establish transport/runtime enforcement.

Explicit boundary: no tools, repository mutation, memory writes, provider fallback, hidden model switch, secrets in receipts, deployment, capability activation or REE activation. No raw/internal reasoning persistence. No first/latest-source conflict erasure, uncalibrated confidence, trading execution or owner psychology scoring.

| Row | Source | Applicability | Design rule | Implementation evidence |
|---|---|---|---|---|
| 1 | docs/research/algorithm-donors/anti-pattern-registry.md:7 | APPLIES | - No missing evidence → `PASS`, `STABLE`, `HEALTHY`, `NEUTRAL`, or synthetic score. | NOT_EXECUTED; reassess per implementation |
| 2 | docs/research/algorithm-donors/anti-pattern-registry.md:8 | APPLIES | - No random/synthetic metrics presented as measured runtime evidence. | NOT_EXECUTED; reassess per implementation |
| 3 | docs/research/algorithm-donors/anti-pattern-registry.md:9 | APPLIES | - No placeholder `True` counted as passed verification. | NOT_EXECUTED; reassess per implementation |
| 4 | docs/research/algorithm-donors/anti-pattern-registry.md:10 | APPLIES | - No score called probability/confidence without calibration evidence. | NOT_EXECUTED; reassess per implementation |
| 5 | docs/research/algorithm-donors/anti-pattern-registry.md:11 | APPLIES | - No graph size, node count, or relationship count used as confidence. | NOT_EXECUTED; reassess per implementation |
| 6 | docs/research/algorithm-donors/anti-pattern-registry.md:12 | APPLIES | - No first-source-wins / latest-wins conflict erasure. | NOT_EXECUTED; reassess per implementation |
| 7 | docs/research/algorithm-donors/anti-pattern-registry.md:13 | APPLIES | - No majority vote treated as factual truth. | NOT_EXECUTED; reassess per implementation |
| 8 | docs/research/algorithm-donors/anti-pattern-registry.md:14 | APPLIES | - No latency treated as semantic truth weight. | NOT_EXECUTED; reassess per implementation |
| 9 | docs/research/algorithm-donors/anti-pattern-registry.md:18 | APPLIES | - No cognitive/model/meta score may raise authority. | NOT_EXECUTED; reassess per implementation |
| 10 | docs/research/algorithm-donors/anti-pattern-registry.md:19 | APPLIES | - No model prompt is a sole policy enforcement mechanism. | NOT_EXECUTED; reassess per implementation |
| 11 | docs/research/algorithm-donors/anti-pattern-registry.md:20 | APPLIES | - No critical gate failure may be overridden by total score. | NOT_EXECUTED; reassess per implementation |
| 12 | docs/research/algorithm-donors/anti-pattern-registry.md:21 | APPLIES | - No mandatory gate failure may produce `EXECUTE_REDUCED` or equivalent side effect. | NOT_EXECUTED; reassess per implementation |
| 13 | docs/research/algorithm-donors/anti-pattern-registry.md:22 | APPLIES | - No tool/skill/provider registry owns execution authority. | NOT_EXECUTED; reassess per implementation |
| 14 | docs/research/algorithm-donors/anti-pattern-registry.md:23 | APPLIES | - No donor code may self-activate or self-promote. | NOT_EXECUTED; reassess per implementation |
| 15 | docs/research/algorithm-donors/anti-pattern-registry.md:27 | APPLIES | - No remote source `fetch → import → execute`. | NOT_EXECUTED; reassess per implementation |
| 16 | docs/research/algorithm-donors/anti-pattern-registry.md:28 | APPLIES | - No mutable branch (`main`, `latest`, tag without immutable digest) as runtime identity. | NOT_EXECUTED; reassess per implementation |
| 17 | docs/research/algorithm-donors/anti-pattern-registry.md:29 | APPLIES | - No unpinned hot reload during a run. | NOT_EXECUTED; reassess per implementation |
| 18 | docs/research/algorithm-donors/anti-pattern-registry.md:30 | APPLIES | - No arbitrary Python callable in a declarative reasoning plan. | NOT_EXECUTED; reassess per implementation |
| 19 | docs/research/algorithm-donors/anti-pattern-registry.md:31 | APPLIES | - No raw tool payload logging when secrets/private data may be present. | NOT_EXECUTED; reassess per implementation |
| 20 | docs/research/algorithm-donors/anti-pattern-registry.md:32 | APPLIES | - No placeholder secret fallback. | NOT_EXECUTED; reassess per implementation |
| 21 | docs/research/algorithm-donors/anti-pattern-registry.md:33 | APPLIES | - No process-health response treated as readiness without dependency checks. | NOT_EXECUTED; reassess per implementation |
| 22 | docs/research/algorithm-donors/anti-pattern-registry.md:37 | APPLIES | - No direct `update_weights()` / model mutation from a live task. | NOT_EXECUTED; reassess per implementation |
| 23 | docs/research/algorithm-donors/anti-pattern-registry.md:38 | APPLIES | - No online feedback loop may change active policy/profile silently. | NOT_EXECUTED; reassess per implementation |
| 24 | docs/research/algorithm-donors/anti-pattern-registry.md:39 | APPLIES | - No episode/analysis log may be called learning without outcome/evaluation. | NOT_EXECUTED; reassess per implementation |
| 25 | docs/research/algorithm-donors/anti-pattern-registry.md:40 | APPLIES | - No adaptive change without baseline, replay/held-out evaluation, shadow, rollback, and approval. | NOT_EXECUTED; reassess per implementation |
| 26 | docs/research/algorithm-donors/anti-pattern-registry.md:44 | APPLIES | - No single observation = perfect alignment. | NOT_EXECUTED; reassess per implementation |
| 27 | docs/research/algorithm-donors/anti-pattern-registry.md:45 | APPLIES | - No duplicate observation narrowing uncertainty twice. | NOT_EXECUTED; reassess per implementation |
| 28 | docs/research/algorithm-donors/anti-pattern-registry.md:46 | NOT_APPLICABLE | - No unbounded graph path enumeration on large graphs. | NOT_EXECUTED; reassess per implementation |
| 29 | docs/research/algorithm-donors/anti-pattern-registry.md:47 | NOT_APPLICABLE | - No async worker using blocking `time.sleep()`. | NOT_EXECUTED; reassess per implementation |
| 30 | docs/research/algorithm-donors/anti-pattern-registry.md:48 | NOT_APPLICABLE | - No pseudo-JSON append format; use JSONL or durable storage. | NOT_EXECUTED; reassess per implementation |
| 31 | docs/research/algorithm-donors/anti-pattern-registry.md:54 | APPLIES | - trading entry/exit rules; | NOT_EXECUTED; reassess per implementation |
| 32 | docs/research/algorithm-donors/anti-pattern-registry.md:55 | APPLIES | - lot sizing; | NOT_EXECUTED; reassess per implementation |
| 33 | docs/research/algorithm-donors/anti-pattern-registry.md:56 | APPLIES | - SL/TP algorithms; | NOT_EXECUTED; reassess per implementation |
| 34 | docs/research/algorithm-donors/anti-pattern-registry.md:57 | APPLIES | - prop-firm logic; | NOT_EXECUTED; reassess per implementation |
| 35 | docs/research/algorithm-donors/anti-pattern-registry.md:58 | APPLIES | - market-specific CONF12/TII/WLWCI/TRQ/EAF/FRPC formulas; | NOT_EXECUTED; reassess per implementation |
| 36 | docs/research/algorithm-donors/anti-pattern-registry.md:59 | APPLIES | - BUY/SELL/NO_TRADE logic; | NOT_EXECUTED; reassess per implementation |
| 37 | docs/research/algorithm-donors/anti-pattern-registry.md:60 | APPLIES | - owner psychology/FOMO/revenge diagnosis as a core cognition mechanism; | NOT_EXECUTED; reassess per implementation |
| 38 | docs/research/algorithm-donors/anti-pattern-registry.md:61 | APPLIES | - broker/runtime execution authority. | NOT_EXECUTED; reassess per implementation |
| 39 | docs/research/algorithm-donors/anti-patterns.md:9 | APPLIES |  /  DOMAIN-01  /  BUY/SELL, lot sizing, SL/TP and prop-firm logic  /  Keep domain ownership outside Sentient  /  | NOT_EXECUTED; reassess per implementation |
| 40 | docs/research/algorithm-donors/anti-patterns.md:10 | APPLIES |  /  DOMAIN-02  /  Market-specific TII, TWMS thresholds and VIX trade recommendations  /  Specify and evaluate task-domain metrics separately  /  | NOT_EXECUTED; reassess per implementation |
| 41 | docs/research/algorithm-donors/anti-patterns.md:11 | APPLIES |  /  DOMAIN-03  /  Owner psychology scoring and FOMO/revenge diagnosis  /  Use observable system failures, not psychological inference  /  | NOT_EXECUTED; reassess per implementation |
| 42 | docs/research/algorithm-donors/anti-patterns.md:12 | APPLIES |  /  EVIDENCE-01  /  Synthetic coherence, random integrity and hard-coded 0.95 confidence  /  Require measured evidence and independent calibration  /  | NOT_EXECUTED; reassess per implementation |
| 43 | docs/research/algorithm-donors/anti-patterns.md:13 | APPLIES |  /  EVIDENCE-02  /  Missing input becomes zero or default healthy  /  Preserve NOT_MEASURED, coverage and unknown/HOLD  /  | NOT_EXECUTED; reassess per implementation |
| 44 | docs/research/algorithm-donors/anti-patterns.md:14 | APPLIES |  /  AUTHORITY-01  /  Remote Python execution from donor acquisition  /  Separate retrieval, isolation, review and admission  /  | NOT_EXECUTED; reassess per implementation |
| 45 | docs/research/algorithm-donors/anti-patterns.md:15 | APPLIES |  /  AUTHORITY-02  /  Automatic runtime parameter mutation and live self-learning  /  Offline candidates and independently authorized promotion  /  | NOT_EXECUTED; reassess per implementation |
| 46 | docs/research/algorithm-donors/anti-patterns.md:16 | APPLIES |  /  REVISION-01  /  Branch main used as runtime revision  /  Pin immutable source, package and configuration digests  /  | NOT_EXECUTED; reassess per implementation |
| 47 | docs/research/algorithm-donors/anti-patterns.md:17 | APPLIES |  /  GATE-01  /  Mandatory gate failure followed by reduced execution  /  Kernel denies or holds; no score override  /  | NOT_EXECUTED; reassess per implementation |
| 48 | docs/research/algorithm-donors/anti-patterns.md:18 | APPLIES |  /  CLAIM-01  /  Parse success or dispatch acceptance promoted to runtime readiness  /  Separate syntax, import, runtime, integration and delivery/application evidence  /  | NOT_EXECUTED; reassess per implementation |
| 49 | docs/research/algorithm-donors/anti-patterns.md:19 | NOT_APPLICABLE |  /  DEDUPE-01  /  Same basename or normalized suffix treated as same source  /  Use actual SHA-256 identity and preserve distinct variants  /  | NOT_EXECUTED; reassess per implementation |
| 50 | docs/research/algorithm-donors/anti-patterns.md:20 | NOT_APPLICABLE |  /  GRAPH-01  /  Unbounded graph paths and graph size as confidence  /  Bound traversal and evaluate against independent evidence  /  | NOT_EXECUTED; reassess per implementation |
| 51 | docs/research/algorithm-donors/anti-patterns.md:21 | NOT_APPLICABLE |  /  EVALUATION-01  /  Cancellation-prone metrics, invalid normalization and empty windows  /  Test finite values, missingness, boundary sizes and temporal separation  /  | NOT_EXECUTED; reassess per implementation |
| 52 | docs/research/algorithm-donors/anti-patterns.md:22 | APPLIES |  /  OVERLAP-01  /  Multiple donor orchestrators become competing kernels  /  One canonical Control Kernel  /  | NOT_EXECUTED; reassess per implementation |
| 53 | docs/research/algorithm-donors/adoption-registry.yaml:1797 | APPLIES | A plan controlling execution or manufacturing missing facts | NOT_EXECUTED; reassess per implementation |
| 54 | docs/research/algorithm-donors/adoption-registry.yaml:1914 | APPLIES | Unrestricted internal reasoning logs and synthetic confidence | NOT_EXECUTED; reassess per implementation |
| 55 | docs/research/algorithm-donors/adoption-registry.yaml:2025 | APPLIES | Unbounded all-simple-path traversal; graph size as confidence | NOT_EXECUTED; reassess per implementation |
| 56 | docs/research/algorithm-donors/adoption-registry.yaml:2128 | APPLIES | Trading strategy names and authority derived from score | NOT_EXECUTED; reassess per implementation |
| 57 | docs/research/algorithm-donors/adoption-registry.yaml:5123 | APPLIES | Arbitrary callables and a second workflow authority chain | NOT_EXECUTED; reassess per implementation |
| 58 | docs/research/algorithm-donors/adoption-registry.yaml:5214 | APPLIES | Errors collapsed into empty objects and score-driven permission | NOT_EXECUTED; reassess per implementation |
