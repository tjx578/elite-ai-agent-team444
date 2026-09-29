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

## 8. Required minimum tests for donor-derived code

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
14. rollback/fallback where checkpoint requires it.

## 9. Do not overclaim validation

Use exact language:

- import passes → `IMPORT_PASS`, not runtime ready;
- unit tests pass → unit tests pass, not production ready;
- synthetic/replay result → `SIMULATED` or `REPLAY`, not measured production evidence;
- source review → `SOURCE_REVIEWED`, not qualified provider.

## 10. Update registry after implementation

A donor-derived implementation is not complete until `adoption-registry.yaml` is updated with:

- implementation path;
- commit SHA;
- tests/evidence;
- lifecycle state;
- known limitations;
- whether the source donor is now superseded by canonical WOLF15 implementation.

## 11. Branch/PR discipline

- one checkpoint-owned change at a time;
- no unrelated subsystem expansion;
- no direct main mutation;
- exact-head CI/review evidence before merge;
- no deployment unless explicitly in checkpoint scope and authorized.

## 12. Stop conditions

Codex must stop and report rather than guess when:

- donor semantics are ambiguous;
- canonical subsystem ownership conflicts;
- required evidence is missing;
- implementation would activate a later checkpoint;
- source and documentation disagree materially;
- a required capability/provider is unavailable;
- the change would raise authority or add side effects beyond the checkpoint.


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
