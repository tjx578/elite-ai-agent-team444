# CP1.1-DESIGN-003 — generation reconciliation

Lifecycle authority: the separately bound independent review and freeze receipts. The original corrective package supplied a **CANDIDATE / REVIEW_PENDING** proposal; that proposal is retained in the downloaded review package. The completed independent review now records a real exact-artifact design review. Local document freeze is separate from remote integration, GitHub approval, runtime acceptance and checkpoint closure.

## Purpose and source boundary

Integration base: `dd49ee105e3a07b3fe147925e9d44d9c3a7633ff` in `tjx578/wolf15-sentient`. That integration retained the developer guide from PR22, but its AGENTS.md bytes no longer matched the historical DESIGN-002 manifest. This proposal preserves that guide and restores the task-specific CP1.1 pointers to Principle, versioning, subset guidance, and the integration contract. The full Principle is not a raw system prompt. Nothing here activates a provider, persona loader, memory, or execution capability.

The ten active member paths are identical to those of the DESIGN-002 manifest. Only AGENTS.md changes in this proposed set; the other nine retain their exact predecessor bytes. The new manifest is an explicit path-to-raw-SHA-256 map, including original line endings. It records content identity and the candidate state at creation. Lifecycle is determined separately by valid review/freeze evidence; the manifest is not rewritten merely to change a lifecycle label.

## Historical and active proof domains

| Domain | Proof used | Disposition |
| --- | --- | --- |
| DESIGN-001, ALG-REG-001 and existing historical pins | Existing exact files and bindings | Preserve unchanged; this proposal does not remove checker coverage |
| DESIGN-002 manifest, independent review and freeze receipt | Original paths and exact hashes in migration.json | Preserve byte-identically; historical PASS remains historical |
| Nine unchanged DESIGN-002 members | Original paths, checked against predecessor digests | Preserve at current paths |
| Historical DESIGN-002 AGENTS.md | Exact 875-byte copy in cp1.1-design-003-historical-AGENTS.md | Preserve as immutable archive; current AGENTS.md is a different member of the successor set |
| DESIGN-003 members | cp1.1-design-003-review-manifest.json | Content bound; lifecycle follows the current separately bound review and freeze receipts |

The historical AGENTS source is full revision `58ebf093371e6bcb2f45b848d22561c35d608a25`, path `AGENTS.md`, Git blob `17e19fad4f59e8ca648be37758e73a0a172a1fb1`, SHA-256 `a85b1eebfdd3b43a08832c97f4c5ff08d82a3a6073abebc9529cc82cc468585f`. Its supplied source binding and exact bytes were checked before archival. The archive preserves those bytes without wrappers or line-ending conversion. This is content provenance, not a new approval or claim that the historical source_commit field already identifies publication.

Using an archive removes the need to fetch historical objects during shallow CI. The checker must bind the archive path and digest explicitly; it must not look for old AGENTS bytes at the current AGENTS.md path or silently update the historical pin. The nine current-path historical members must continue to match their old digests. A later change to any of those members requires a new explicit archival/disposition decision; it must not disappear from historical coverage.

## Files and schemas

- `cp1.1-design-003-review-manifest.json`: `cp1.1-review-manifest/v1`; explicit ten-member map; `CONTENT_BOUND`; `generation_state_at_creation=CANDIDATE`.
- `cp1.1-design-003-independent-review.json`: `cp1.1-independent-review/v1`; exact manifest digest; actual independent reviewer identity, time, method, result and limitations. It is neither a GitHub approval nor a human exact-byte review.
- `cp1.1-design-003-freeze-receipt.json`: `cp1.1-freeze-receipt/v1`; binds the exact manifest and completed review. The integrator records actual local freeze separately; runtime loading and canonical closure remain false, and publication is bound separately.
- `cp1.1-design-003-migration.json`: `cp1.1-generation-migration/v1`; explicit predecessor receipt/member dispositions and proposed active artifact bindings.
- `cp1.1-design-003-historical-AGENTS.md`: exact historical member archive, not developer instructions for the current tree.

Manifest, review, freeze and migration artifacts remain outside the ten-member active byte-set. None contains its own digest. The migration file binds the other artifacts but is not itself their acceptance evidence. This explanatory note does not override the README, persona versioning, or checker policy.

## Required fail-closed behavior

Historical integrity and active acceptance are separate decisions. Historical hash matches do not make DESIGN-003 frozen. The original pending artifacts must yield `ACTIVE_GENERATION_NOT_FROZEN` in the generation gate. Null reviewer/time, pending status, false active_generation and absent owner acceptance must never be interpreted as PASS or default success. A structural check of this proposal is not the independent exact-artifact review required for freeze.

Local document freeze requires an independent reviewer to inspect the final ten-member manifest and its exact bytes, record the real outcome and identity/time, and resolve findings. That review was completed by the separate governance reviewer; the integrator records the freeze. The owner's scoped request of 2026-09-30 18:38 UTC to complete PR21 authorizes this corrective document work and its publication to the existing PR. This is an execution grant, not a claim that the owner personally reviewed the final bytes. The earlier package's additional pending final-owner wording reflected its diagnosis-only scope and is superseded by the current task authorization; canonical persona-versioning requires independent exact-artifact review before freeze. No merge, deployment, trading, runtime activation or checkpoint closure is authorized. A real freeze artifact must bind that actual review. Updating review/freeze evidence requires updating the migration references and the reviewed checker pins as appropriate; no status field alone can authorize a generation. Preserve predecessor receipts, bind publication separately, and verify fresh CI/resulting-main before claiming closure. Runtime/provider behavior remains a separate CP1.6 gate.

No blanket secret-scan exception is introduced for these new hashes or files. Any new detector findings still require exact detector/type/path/line/field/fingerprint triage. This note does not assert that detection, generation enforcement, or production acceptance has been executed.

## Verification scope

The original package author's local, static inspection established the ten proposed member digests, the unchanged nine historical members, the three unchanged DESIGN-002 evidence artifacts, and the exact archive SHA-256/Git blob identity. These are artifact-integrity checks. No target module import, scanner, runtime test, performance benchmark, commit, push, merge, deployment, or external write was performed by this authoring step.

The separate governance reviewer repeated raw-byte verification in the saved executor: ten successor members, all 36 historical checker pins, the three DESIGN-002 receipts and exact historical AGENTS Git bytes matched. The completed review records methods and limitations. The reviewer inspected the generation gate statically; scanner tests and deadline acceptance are not claimed by this review. Changing a manifest member requires a new exact-artifact review.
