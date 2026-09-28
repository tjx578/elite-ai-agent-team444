# SK-01 skill selection assessment

This is a public, documentation-only summary of the 28 September 2026
historical catalog reassessment. The companion [catalog](catalog.json) records
all 220 distinct selectors as **design candidates**. It is not a runtime
registry, a list of installed packages, or permission to run a skill.

## Provenance and evidence

The reassessment read a 9 September historical catalog at revision
[`d2411fbb431a19527179437500beadaa05f5b161`](https://github.com/tjx578/TUYUL-FX-WOLF-15LAYER-SYSTEM/blob/d2411fbb431a19527179437500beadaa05f5b161/docs/runbooks/codex-skill-assessment.md)
and the Sentient architecture at revision
[`e14a96919dbd50350c4877393c40a069570d906c`](https://github.com/tjx578/wolf15-sentient/blob/e14a96919dbd50350c4877393c40a069570d906c/docs/architecture/super-intelligence-reference-architecture.md).
The 220-entry source JSON has SHA-256
`058ca1a3c2334dc936ebce19c858cf6528b16dff48a1f276cad0a9af9d017622`;
the narrative assessment has SHA-256
`0323f2973e14be63bb4c36780ffb6ae7fa378126969d9727a5458417c9aef5b5`.
The source workbook digest and individual worksheet rows are recorded in the
catalog. These are historical source bindings; they do not identify the bytes
currently installed on an owner's host.

The public catalog retains selector, selection category, proposed function and
owner area, target stage, source row, qualification dependency, overlap status,
evidence status, and next check. It omits the source bundle, private paths,
account data, and skill package code. The 220 source records have unique
selectors and their category counts sum to 220. The historical 157 global and
63 plugin counts are source-reported, not a current Codex inventory.

| Selection category | Historical count | Meaning |
| --- | ---: | --- |
| `PRIORITAS_INTI` | 25 | First candidates for bounded package review |
| `PENDUKUNG_BERTAHAP` | 48 | Task-dependent support |
| `FOUNDRY_META` | 8 | Authoring, evaluation, and management candidates |
| `PERSONAL_DOKUMEN` | 14 | Personal research and artifact candidates |
| `KONSOLIDASI_ALTERNATIF` | 43 | Functional comparison needed; equivalence unproven |
| `OPSIONAL_PROVIDER` | 31 | Depends on a selected provider and host |
| `EKSPERIMEN_TERTUNDA` | 35 | Needs a measured problem and offline evaluation |
| `DOMAIN_TERPISAH` | 15 | Separate project or domain authority |
| `REFERENSI_LEGACY_SAJA` | 1 | Historical negative reference, never an active gate |

The 25 core entries are candidate priorities, not 25 qualified packages. The
current host inventory is `NOT_MEASURED`; full current package review,
behavioral tests, contribution tests, and `common-skill/v1` evaluation are
`NOT_EXECUTED`. Individual package dependencies and exact overlap peers have
not been established. The catalog states those gaps rather than inventing a
dependency graph or treating similar names as equivalent.

## First package-review batch

The first eight candidates support evidence and context work and its follow-up
reviews. M2's initial read path is already merged separately in
[PR #11](https://github.com/tjx578/wolf15-sentient/pull/11); this batch does not
retroactively qualify that implementation.

| Work | Candidate selectors |
| --- | --- |
| Source and requirement discovery | `agent-scout-explorer`, `agent-specification` |
| Context and planning | `retrieval-knowledge-structurer`, `agent-planner` |
| Implementation and tests | `agent-coder`, `agent-tester` |
| Review and evidence | `agent-reviewer`, `verification-quality` |

For each package, inspect its complete current bytes and dependencies, run
positive and negative behavior tests, compare its contribution to a fixed
baseline, then evaluate exact bound evidence under the
[qualification policy](../../governance/skill-qualification-policy.md). If a
collector, evaluator, or environment is unavailable, retain `NOT_EXECUTED` or
`NOT_MEASURED`. Package use in the development workbench requires its own
scoped admission; Sentient product use requires later runtime controls.

The [adoption plan](../../architecture/skill-adoption-plan.md) places these
steps alongside the existing milestone order. No skill package, active loader,
permission, connector, or workflow behavior is changed by SK-01.
