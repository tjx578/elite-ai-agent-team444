# WOLF15 Sentient — Algorithm Donor Canon

Status: **DRAFT_RECONCILED — independent review pending**
Purpose: documentation-only guidance for Codex Desktop and human reviewers.

**Roadmap authority:** this directory is a frozen donor/research overlay only.
It may map records to CP0–CP9, but it does not define checkpoint order or a
parallel roadmap. The normative sequence belongs to the
[root README](../../../README.md#10-roadmap-master-cp0cp9);
[roadmap.md](../../architecture/roadmap.md) is derived detail.
Runtime effect: **NONE**.
Authority effect: **NONE**.
CP0 status: **CLOSED / PASS** and must not be reopened by this documentation package.
CP0 accepted baseline: `bad73335f518d89356b88cba1cc26730808cd224`.

## Purpose

This directory records what may be extracted from the legacy algorithm corpus, where each extracted principle belongs in the WOLF15 Sentient skeleton, which checkpoint may implement it, and which source behavior is explicitly prohibited.

The rule for every donor is:

> **EXTRACT → ABSTRACT → REBUILD → EVALUATE**

Never use `COPY → IMPORT → ACTIVATE` as an adoption path.

## Batch index

| Batch | Canonical topic | File |
|---|---|---|
| ARCH-ALG-01 | Cognitive / Constitutional Algorithms | `batch-01-cognitive-constitutional.md` |
| ARCH-ALG-02 | Neural Orchestration / Capability Algorithms | `batch-02-neural-capability.md` |
| ARCH-ALG-03 | Reflective / Pipeline / Evaluation Algorithms | `batch-03-reflective-evaluation.md` |
| ARCH-ALG-04 | Cognitive Lifecycle / Contracts / Tools / Runtime Tests | `batch-04-cognitive-contract-runtime.md` |
| ARCH-ALG-05 | Reasoning Graph / Policy Guard / Temporal Evaluation / Explainable Fusion | `batch-05-reasoning-policy-evaluation.md` |

## Mandatory companion documents

- `adoption-registry.yaml` — SSOT for adoption decisions.
- `checkpoint-adoption-matrix.md` — when each extracted algorithm may be implemented.
- `anti-pattern-registry.md` — prohibited behavior inherited from legacy donors.
- `codex-desktop-implementation-contract.md` — mandatory implementation rules for Codex Desktop.
- `source-provenance.md` — report/source provenance and evidence status.

## Non-negotiable invariants

1. Control Kernel owns authority.
2. Model output is proposal, not command.
3. Evidence outranks narrative confidence.
4. Missing evidence remains `NOT_MEASURED`.
5. Memory cannot own workflow state.
6. Skill trust cannot raise task authority.
7. Donor order cannot determine provider priority.
8. Candidate implementations cannot self-promote.
9. Running tasks pin relevant model/provider/registry generations.
10. External side effects use one policy-controlled execution boundary.
11. Donor code does not become runtime code merely because it has a production-looking name.
12. Trading-domain logic remains outside the WOLF15 Sentient cognitive core.

## Reconciled generation and evidence

Generation: CP0-ADDENDUM-01-RECONCILED-001. Both ZIPs are hash-verified.
All 13 package members, including five batch documents, were read completely.
The package is the owner-designated reconciliation source; older snapshots
are no longer required to close this documentation step.

The registry retains 31 package records plus four RECONCILED_DESIGN records
and two BATCH_DOCUMENT_SUPPORTED telemetry components: **37 inactive designs**.
Only lifecycle_stage.documented is true. No runtime or authority changes occur.

- [Source provenance and input hashes](source-provenance.md).
- [All-record checkpoint matrix](checkpoint-matrix.md).
- [Subsystem ownership matrix](subsystem-matrix.md).
- [Checkpoint guidance](checkpoint-adoption-matrix.md).
- [Implementation contract](codex-desktop-implementation-contract.md).
- [Canonical ownership](../../architecture/canonical-ownership.md).
- [Indexed exclusions](anti-patterns.md).
- [Supplementary local observations](local-source-observations.md).

## Frozen generation ALG-REG-001

ALG-REG-001 is locally FROZEN, bound to reviewed source commit
`a6c2f24334b25349d9f9dcee52899169eebd4e37`. All ten independent
documentation review groups passed. The 37 design records are unchanged.

- [Exact-source independent review receipt](receipts/CP0_ADDENDUM_01_A01_REVIEW_a6c2f24.json).
- [Freeze metadata and four source/frozen artifact digests](receipts/ALG-REG-001-freeze.yaml).

Digest values use exact Git blob bytes, not platform-dependent checkout line
endings. The registry embeds the reviewed pre-freeze digest; the separate
freeze receipt holds the final registry digest to avoid self-reference.
The receipt references are relative to this algorithm-donors directory.

ALG-REG-001 and its bound artifacts are immutable. Newly discovered donors,
including repositories or D:/Python sources, enter a research/admission queue
for a future generation such as ALG-REG-002. Do not silently edit ALG-REG-001.

The earlier reconciled-generation text and companion-document draft appendices
record the reviewed source stage; the freeze receipt records the current local
freeze. The copied review receipt retains its original pre-freeze scope/status.
This freeze records documentation acceptance and does not qualify implementations.

Push, Draft PR, remote checks, PR review, merge and resulting-main verification
remain separate. CP0 remains CLOSED / PASS at its accepted SHA. CP1 is
NOT_STARTED and requires an integrated, verified resulting-main baseline.

## Separate WebMCP donor portfolio

WebMCP research is tracked separately under
[`docs/research/webmcp-donors/`](../webmcp-donors/README.md). It does not
mutate the frozen `ALG-REG-001` generation. WebMCP repositories are protocol,
skill, runtime/fallback and evaluation donors whose implementation belongs to
CP4–CP8 according to the official roadmap.
