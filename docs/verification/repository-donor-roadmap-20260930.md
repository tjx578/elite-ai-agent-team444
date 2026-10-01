# Repository donor roadmap reconciliation — 30 September 2026 WITA

## Scope and verdict

Mode: **REVIEW_GAP + DESIGN_TO_BE**. Documentation/source reconciliation is the
scope. Donor qualification/runtime readiness remains **WARN / NOT_EXECUTED**;
commit existence is the only donor property independently verified here.
This record is not a CI, release, skill qualification or checkpoint-closeout receipt.

Sentient base: `07c942cd62ec5e85a521ee47976559a55f35d8b8`. GitHub tree contains 103 tracked files before this
change and no AGENTS.md. Source comparison from `dd5cf74ce47e395cf859a2b5130790129af01e16`
changes only README.md. API source still routes `/tasks` to the deterministic
in-memory workflow with Architect/Engineer/Reviewer stubs. Real model providers,
repository execution, persistent memory, Foundry, dynamic skills and WebMCP
remain absent from the implemented baseline. No donor program was executed.

## Authoritative inputs

| Input | Bytes | SHA-256 | Use |
| --- | --- | --- | --- |
| `WOLF15_SENTIENT_MASTER_REPOSITORY_DONOR_REGISTER_v1.2_WEBMCP(1).md` | 22506 | `611dd6feb2da7dc6e00b62c0353beee52d51838fd8796f192322fc1e6e4b065c` | Portfolio, capability intentions and CP routing |
| `WOLF15_SENTIENT_WEBMCP_DONOR_CP_MATRIX_v1.2(1).csv` | 2765 | `ccbab9b16a945c3a97c6052b5a88acf1f26a9e525fb96bd360e56785890b2a33` | 11 exact S06 rows, copied without byte changes |

Source dates remain 29 September 2026; this reconciliation is dated in WITA on
30 September. Source-reported current HEAD is not an independent observation of
today's default branch. Full assessment/code/build/license/security evidence was
not supplied by a commit lookup and is not invented.

## Files with the same name or function

Neither uploaded basename exists in main or the inspected PR #17 tree.

| Existing path / location | Observed gap | Reconciliation |
| --- | --- | --- |
| Root README at base | Complete system/28-role/73-substep SSoT, donor summary lacks Transformers and full S06 routing | Extend the existing master; preserve persona, roster and gates |
| `docs/architecture/roadmap.md` on main | CP0 incorrectly still described as open; older milestone view | Replace with complete derived CP0–CP9/substep view from root README |
| `docs/architecture/current-state.md` on main | Latest checkpoint paragraph stops at CP0.1–CP0.3 | Add observed base and CP0 CLOSED / CP1 ACTIVE_NEXT; preserve historical receipts |
| `docs/architecture/README.md` and `canonical-ownership.md` | Global authority wording predates root SSoT | Explicit root → architecture → subsystem hierarchy; no new controller |
| `docs/research/donor-adaptation-register-20260929.md` in PR #17 | Earlier portfolio normalization, not present on main | Reuse its path for full uploaded v1.2 reconciliation |
| `docs/research/webmcp-donors/README.md` and `portfolio.yaml` in PR #17 | Older combined target_cp mapping | Reuse paths, keep all 11 revisions, apply exact CSV primary/secondary/qualification fields |
| `docs/research/algorithm-donors/*` on main | Frozen algorithm corpus, distinct from repository portfolio | Leave all bytes untouched; reference ALG-REG-001 rather than overwrite |
| New `webmcp-donors/donor-cp-matrix.csv` | No source CSV on main | Preserve uploaded bytes; normalized filename only |

PR #17 snapshot: `e8f82b06868311a19f65ae03782a3b499e04ba1a`, open/unmerged at inspection.
Its five inspected review threads were resolved. This update does not merge,
rebase or modify that PR; future reconciliation must preserve the newer root
README and donor routing. Branch state is a snapshot, not a live badge.

## Exact commit existence observations

Observed UTC 2026-09-29 16:58:21–16:58:22 (WITA 2026-09-30 00:58:21–00:58:22).
Each GitHub GET `/repos/{repository}/commits/{revision}` returned a matching
full commit SHA. The links identify the exact object; none proves code fitness.

| Repository | Requested / returned SHA | Result |
| --- | --- | --- |
| `webmachinelearning/webmcp` | [`0957b0b8f1e32c401d4248424719a4851d4202c4`](https://github.com/webmachinelearning/webmcp/commit/0957b0b8f1e32c401d4248424719a4851d4202c4) | PASS_EXACT_COMMIT_EXISTS |
| `webmachinelearning/webmcp-types` | [`a8d8292ff645b691bfdb529484d3c089e81e8c28`](https://github.com/webmachinelearning/webmcp-types/commit/a8d8292ff645b691bfdb529484d3c089e81e8c28) | PASS_EXACT_COMMIT_EXISTS |
| `GoogleChromeLabs/webmcp-tools` | [`a66c1be1caee78bb98b9781bf5cb4413ad2ccac7`](https://github.com/GoogleChromeLabs/webmcp-tools/commit/a66c1be1caee78bb98b9781bf5cb4413ad2ccac7) | PASS_EXACT_COMMIT_EXISTS |
| `GoogleChromeLabs/use-webmcp-tool` | [`9f0dc6eddf88cff65ebe877f199d4547e74ab31e`](https://github.com/GoogleChromeLabs/use-webmcp-tool/commit/9f0dc6eddf88cff65ebe877f199d4547e74ab31e) | PASS_EXACT_COMMIT_EXISTS |
| `webmaxru/web-ai-agent-skills` | [`03b778c8ef822c98b112fd3617050c72d78f4d60`](https://github.com/webmaxru/web-ai-agent-skills/commit/03b778c8ef822c98b112fd3617050c72d78f4d60) | PASS_EXACT_COMMIT_EXISTS |
| `TueJon/webmcpify` | [`c17d1f1382e306296becc0e8294106c477e13d40`](https://github.com/TueJon/webmcpify/commit/c17d1f1382e306296becc0e8294106c477e13d40) | PASS_EXACT_COMMIT_EXISTS |
| `nekuda-ai/webmcp-kit` | [`f0298ec9f26af13e477b9141ab4d8f2a6c23426d`](https://github.com/nekuda-ai/webmcp-kit/commit/f0298ec9f26af13e477b9141ab4d8f2a6c23426d) | PASS_EXACT_COMMIT_EXISTS |
| `signettai/signett` | [`cb9be5ff2e9ca669c14e596673355d1ce58d3924`](https://github.com/signettai/signett/commit/cb9be5ff2e9ca669c14e596673355d1ce58d3924) | PASS_EXACT_COMMIT_EXISTS |
| `WebMCP-org/npm-packages` | [`1c7a398a77fa54e54b4d3fdd7ed05d19efb067d5`](https://github.com/WebMCP-org/npm-packages/commit/1c7a398a77fa54e54b4d3fdd7ed05d19efb067d5) | PASS_EXACT_COMMIT_EXISTS |
| `opentiny/webmcp-sdk` | [`47a2b031dfd77db19e18b5e7621976c5885bd924`](https://github.com/opentiny/webmcp-sdk/commit/47a2b031dfd77db19e18b5e7621976c5885bd924) | PASS_EXACT_COMMIT_EXISTS |
| `nekuda-ai/WindTunnel` | [`5ca8644e23826ebb30108e7bad240b61043bfe67`](https://github.com/nekuda-ai/WindTunnel/commit/5ca8644e23826ebb30108e7bad240b61043bfe67) | PASS_EXACT_COMMIT_EXISTS |
| `tjx578/transformers-sentient` | [`6b07e4510e3f9667f5256656118515bcde306fc4`](https://github.com/tjx578/transformers-sentient/commit/6b07e4510e3f9667f5256656118515bcde306fc4) | PASS_EXACT_COMMIT_EXISTS |

## Reconciliation decisions and remaining gates

- README root remains system SSoT; the donor register is master only for portfolio detail.
- All 11 CSV rows retain source revisions, roles and primary/secondary/qualification routing.
- Source knowledge/native foundations may precede CP6; portfolio package/code/skill/runtime admission may not. A necessary early import is HOLD pending an explicit qualification decision.
- Shadow is conditional on a separately authorized qualification path; current policy supports offline only.
- Framework license and model/dataset rights are distinct. `trust_remote_code=false` is a design default, not measured runtime enforcement.
- CP0 remains closed; CP1.1 is next. The 28-role roster and 73 existing substeps remain present.
- Openlib repository identity is NOT_ESTABLISHED. Non-S06 reported HEADs and historical assessed clones remain SOURCE_REPORTED and are not replaced by newer revisions.

Before donor activation: inspect complete pinned packages/models, establish
intended-use rights, inspect dependencies/security/egress, enforce sandbox
containment, collect independent behavior/contribution evidence, qualify the
evaluator, then obtain matching admission. No model download, training,
persistent learning, deployment or trading action was performed here.

Local documentation checks and remote CI are recorded in the delivery PR at
the exact candidate/resulting-main SHA. They cannot qualify donor code.
