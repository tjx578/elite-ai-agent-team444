# Algorithm Anti-Pattern Registry

Codex Desktop must treat every item in this file as **prohibited unless a later canonical ADR explicitly replaces the rule**.

## Evidence and measurement

- No missing evidence → `PASS`, `STABLE`, `HEALTHY`, `NEUTRAL`, or synthetic score.
- No random/synthetic metrics presented as measured runtime evidence.
- No placeholder `True` counted as passed verification.
- No score called probability/confidence without calibration evidence.
- No graph size, node count, or relationship count used as confidence.
- No first-source-wins / latest-wins conflict erasure.
- No majority vote treated as factual truth.
- No latency treated as semantic truth weight.

## Authority and policy

- No cognitive/model/meta score may raise authority.
- No model prompt is a sole policy enforcement mechanism.
- No critical gate failure may be overridden by total score.
- No mandatory gate failure may produce `EXECUTE_REDUCED` or equivalent side effect.
- No tool/skill/provider registry owns execution authority.
- No donor code may self-activate or self-promote.

## Runtime and provider safety

- No remote source `fetch → import → execute`.
- No mutable branch (`main`, `latest`, tag without immutable digest) as runtime identity.
- No unpinned hot reload during a run.
- No arbitrary Python callable in a declarative reasoning plan.
- No raw tool payload logging when secrets/private data may be present.
- No placeholder secret fallback.
- No process-health response treated as readiness without dependency checks.

## Learning and adaptation

- No direct `update_weights()` / model mutation from a live task.
- No online feedback loop may change active policy/profile silently.
- No episode/analysis log may be called learning without outcome/evaluation.
- No adaptive change without baseline, replay/held-out evaluation, shadow, rollback, and approval.

## Concurrency and state

- No single observation = perfect alignment.
- No duplicate observation narrowing uncertainty twice.
- No unbounded graph path enumeration on large graphs.
- No async worker using blocking `time.sleep()`.
- No pseudo-JSON append format; use JSONL or durable storage.

## Domain separation

Do not move the following into WOLF15 Sentient cognitive core:

- trading entry/exit rules;
- lot sizing;
- SL/TP algorithms;
- prop-firm logic;
- market-specific CONF12/TII/WLWCI/TRQ/EAF/FRPC formulas;
- BUY/SELL/NO_TRADE logic;
- owner psychology/FOMO/revenge diagnosis as a core cognition mechanism;
- broker/runtime execution authority.

Domain logic may exist in separate products/providers if independently qualified and authorized.


## Reconciled repository status

DRAFT_RECONCILED. See [registry](adoption-registry.yaml) and [provenance](source-provenance.md).
Design guidance grants no runtime authority. Independent review and freeze remain separate.
