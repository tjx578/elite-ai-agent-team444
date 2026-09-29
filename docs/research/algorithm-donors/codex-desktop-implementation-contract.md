# Codex Desktop Implementation Contract — Algorithm Donors

This document is mandatory reading before Codex Desktop implements any donor-derived algorithm in WOLF15 Sentient.

## 1. Start from the checkpoint, not from the donor file

Before coding, record:

```text
ACTIVE_CHECKPOINT = CPx
ACTIVE_STEP       = CPx.y
BASE_SHA          = <exact SHA>
ALGORITHM_ID      = <registry ID>
TARGET_SUBSYSTEM  = <canonical owner>
README_CONTRACT   = <path>
```

If the algorithm's `target_checkpoint` in `adoption-registry.yaml` is later than the active checkpoint, **do not implement it**. Record it as deferred.

## 2. Never direct-copy a donor implementation

Required workflow:

```text
DONOR SOURCE
  ↓
Extract generic principle
  ↓
List donor assumptions and defects
  ↓
Map to canonical WOLF15 contract
  ↓
Implement minimal checkpoint-owned behavior
  ↓
Tests / evidence
  ↓
Review exact HEAD
```

## 3. Resolve ownership before code placement

- `control/` owns authority/policy/gates.
- `sentient/` owns cognition/proposals.
- `orchestration/` owns workflow coordination, not authority.
- `evidence/` owns evidence structures/grounding, not execution.
- `context/` owns assembled context, not durable workflow state.
- `memory/` cannot own workflow state or policy.
- `capabilities/` owns provider metadata/resolution, not task authority.
- `evaluation/` measures; it does not self-promote candidates.
- `learning/` and `ree/` may only produce candidates until approved.

If placement changes ownership, create an architecture amendment first.

## 4. Preserve evidence semantics

Every implementation must distinguish:

- `VERIFIED`
- `SOURCE_CLAIM`
- `DERIVED`
- `ASSUMPTION`
- `NOT_MEASURED`

Never translate absence into a favorable numeric default.

## 5. Authority discipline

- Model/provider output is always proposal/data.
- Confidence, quality, coherence, health, drift, or meta score never raises authority.
- Side effects require Control Kernel admission and appropriate approval.
- Trust != authority.

## 6. Configuration discipline

Every active algorithm profile/config should be:

- versioned;
- finite-numeric validated;
- immutable for a running task;
- bound to a digest;
- recorded in run metadata where decision-relevant.

No silent in-place mutation of active configuration.

## 7. Provider and repository discipline

- Resolve exact SHA before reading a repository snapshot.
- Donor/source revision must be immutable and recorded.
- Provider version and compatibility contract must be explicit.
- Do not execute donor source during discovery/analysis.
- Capability candidate lifecycle is evaluation → shadow → admission, never direct active.


## 8. Mandatory prohibition coverage

The prohibition sources below are **normative implementation constraints**, not optional research notes:

1. `docs/research/algorithm-donors/anti-pattern-registry.md`;
2. `docs/research/algorithm-donors/anti-patterns.md`;
3. the selected algorithm record's `reject` list in `adoption-registry.yaml`;
4. any checkpoint- or subsystem-specific prohibition explicitly referenced by the selected record.

Before implementation begins, Codex must build a **Prohibition Compliance Matrix** for the selected `ALGORITHM_ID`. Every prohibition from the normative sources above must be classified as exactly one of:

- `APPLIES` — the prohibition is relevant to the proposed implementation;
- `NOT_APPLICABLE` — the prohibition cannot apply to this implementation, with a concrete reason;
- `UNRESOLVED` — applicability cannot yet be established.

`UNRESOLVED` is a stop condition. Codex must not implement or claim completion until it is resolved.

Minimum matrix fields:

```text
ALGORITHM_ID
PROHIBITION_SOURCE
PROHIBITION_ID_OR_RULE
APPLICABILITY = APPLIES | NOT_APPLICABLE | UNRESOLVED
IMPLEMENTATION_BOUNDARY
ENFORCEMENT_MECHANISM
VERIFICATION_EVIDENCE
STATUS = PASS | FAIL | NOT_EXECUTED | NOT_APPLICABLE
RATIONALE
```

For every `APPLIES` rule:

- identify the exact implementation boundary that prevents the prohibited behavior;
- provide evidence appropriate to that rule, such as a negative test, contract/schema test, static scan, configuration validation, architecture-boundary review, or exact-source review;
- record the exact test path, command, receipt, or reviewed source location;
- treat `NOT_EXECUTED` as not satisfied;
- treat missing evidence as `NOT_MEASURED`, never as PASS.

For every `NOT_APPLICABLE` rule, Codex must state why the selected algorithm, subsystem, checkpoint, and side-effect surface make that prohibition inapplicable. A blanket statement such as "not relevant" is insufficient.

The selected record's `reject` list is mandatory even when a similar prohibition already exists in the global anti-pattern documents. The record-level rejection is the donor-specific contract and must be mapped explicitly.

At minimum, when relevant, verification must demonstrate that the implementation does **not** introduce:

- raw tool payload logging or placeholder-secret fallbacks;
- majority vote, latency, graph size, node count, or other uncalibrated signals as factual-truth/confidence authority;
- adaptive mutation without the required baseline → replay/held-out evaluation → shadow → rollback → approval lifecycle;
- blocking `time.sleep()` or equivalent blocking waits in async workers;
- trading entry/exit, lot sizing, SL/TP, broker execution, or other excluded domain logic inside the WOLF15 Sentient cognitive core;
- any other prohibition present in the two normative anti-pattern documents or the selected record's `reject` list.

A donor-derived implementation is **not complete** while any applicable prohibition is unmapped, has `FAIL`, or lacks executed evidence.

## 9. Required minimum tests for donor-derived code

As applicable:

1. happy path;
2. missing evidence/data;
3. exact boundary values;
4. invalid schema;
5. `NaN`, `+inf`, `-inf` rejection;
6. duplicate/replay behavior;
7. stale/out-of-order event behavior;
8. concurrency/isolation;
9. deterministic replay if deterministic behavior is claimed;
10. failure classification;
11. authority-escalation negative test;
12. unsupported side-effect negative test;
13. config/profile digest mismatch;
14. rollback/fallback where checkpoint requires it;
15. negative tests or equivalent verification for every applicable prohibition in the Prohibition Compliance Matrix;
16. explicit verification of every selected-record `reject` item that can be enforced or observed at this checkpoint.

## 10. Do not overclaim validation

Use exact language:

- import passes → `IMPORT_PASS`, not runtime ready;
- unit tests pass → unit tests pass, not production ready;
- synthetic/replay result → `SIMULATED` or `REPLAY`, not measured production evidence;
- source review → `SOURCE_REVIEWED`, not qualified provider.

## 11. Update registry after implementation

A donor-derived implementation is not complete until `adoption-registry.yaml` is updated with:

- implementation path;
- commit SHA;
- tests/evidence;
- lifecycle state;
- known limitations;
- whether the source donor is now superseded by canonical WOLF15 implementation.

## 12. Branch/PR discipline

- one checkpoint-owned change at a time;
- no unrelated subsystem expansion;
- no direct main mutation;
- exact-head CI/review evidence before merge;
- no deployment unless explicitly in checkpoint scope and authorized.

## 13. Stop conditions

Codex must stop and report rather than guess when:

- donor semantics are ambiguous;
- canonical subsystem ownership conflicts;
- required evidence is missing;
- implementation would activate a later checkpoint;
- source and documentation disagree materially;
- a required capability/provider is unavailable;
- the change would raise authority or add side effects beyond the checkpoint;
- either normative anti-pattern document is missing/unreadable;
- a selected-record `reject` list cannot be reconciled with the proposed implementation;
- any prohibition remains `UNRESOLVED`, `FAIL`, or lacks required executed evidence.


## Reconciled repository status

DRAFT_RECONCILED. See [registry](adoption-registry.yaml) and [provenance](source-provenance.md).
Design guidance grants no runtime authority. Independent review and freeze remain separate.

Use decision.target_subsystem, decision.target_checkpoints and decision.checkpoint_stages.
source_proposal preserves the original YAML; origin and batch_provenance label
reconciliation. lifecycle_stage grants no authority. ReasoningPlan contract
owner is contracts, coordination owner orchestration, and producer sentient.
Control retains workflow state and authority. The cognitive gateway owner is
sentient/model_gateway; provider implementations belong to models/providers.
The latest user instruction forbids automatic push/PR/merge for this addendum.
