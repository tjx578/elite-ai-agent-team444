# Algorithm anti-pattern registry

View of [the registry](adoption-registry.yaml). Each mechanism is REJECTED for
adoption into Sentient. External domain systems retain their own separately
governed responsibilities. Algorithm records add donor-specific exclusions.

| ID | Rejected mechanism | Required replacement |
| --- | --- | --- |
| DOMAIN-01 | BUY/SELL, lot sizing, SL/TP and prop-firm logic | Keep domain ownership outside Sentient |
| DOMAIN-02 | Market-specific TII, TWMS thresholds and VIX trade recommendations | Specify and evaluate task-domain metrics separately |
| DOMAIN-03 | Owner psychology scoring and FOMO/revenge diagnosis | Use observable system failures, not psychological inference |
| EVIDENCE-01 | Synthetic coherence, random integrity and hard-coded 0.95 confidence | Require measured evidence and independent calibration |
| EVIDENCE-02 | Missing input becomes zero or default healthy | Preserve NOT_MEASURED, coverage and unknown/HOLD |
| AUTHORITY-01 | Remote Python execution from donor acquisition | Separate retrieval, isolation, review and admission |
| AUTHORITY-02 | Automatic runtime parameter mutation and live self-learning | Offline candidates and independently authorized promotion |
| REVISION-01 | Branch main used as runtime revision | Pin immutable source, package and configuration digests |
| GATE-01 | Mandatory gate failure followed by reduced execution | Kernel denies or holds; no score override |
| CLAIM-01 | Parse success or dispatch acceptance promoted to runtime readiness | Separate syntax, import, runtime, integration and delivery/application evidence |
| DEDUPE-01 | Same basename or normalized suffix treated as same source | Use actual SHA-256 identity and preserve distinct variants |
| GRAPH-01 | Unbounded graph paths and graph size as confidence | Bound traversal and evaluate against independent evidence |
| EVALUATION-01 | Cancellation-prone metrics, invalid normalization and empty windows | Test finite values, missingness, boundary sizes and temporal separation |
| OVERLAP-01 | Multiple donor orchestrators become competing kernels | One canonical Control Kernel |
