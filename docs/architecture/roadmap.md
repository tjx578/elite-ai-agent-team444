# WOLF15 Sentient architecture and delivery roadmap

## Baseline and rule

The canonical repository is `tjx578/wolf15-sentient`. PR #1–#6 are merged.
The inspected M1-B `main` baseline is
`7ffac9a8254688649ecf8bca57e2ae7757bd9f32`; its CI installed the
package, passed 56 tests, and checked installed identity/entrypoint on Python
3.11–3.13. This is a historical commit-bound receipt, not proof for later
M1-C changes. The working runtime is a deterministic `READ_ONLY` kernel with
three stubs and contract-only evidence/learning types. No deployment,
Railway change, capability activation, or REE activation follows from M1-B.
This roadmap does not turn a target into a current capability. Each milestone
must update [`current-state.md`](current-state.md) with exact-source and test
evidence.

| Step | Delivery | Acceptance gate | Excluded at that step |
| --- | --- | --- | --- |
| P0 — complete | PR #1–#4 consolidated; canonical repository name | Merge ancestry and CI on resulting main | Deployment |
| M1-B — complete | Freeze responsibility, trust, data, and authority boundaries in architecture docs | Merged PR #6 and CI on resulting `main` `7ffac9a` | Runtime wiring |
| M1-C — in progress | Ownership and production trust foundation | Active protected-branch policy plus separate lint, type, build/install, dependency, secret, and security gates on exact M1-C head and resulting `main` | Production launch |
| M2 | Evidence/context read path | SourceRef resolution, freshness/conflict policy, grounded claims, read-only replay | Automatic learning |
| M3 | Schema-constrained reasoning adapters | Typed proposal contract, model-output validation, deterministic fallback and limits | Tool authority for models |
| M4 | Read-only repository intelligence | Exact-revision repository snapshot, provenance, grounded report | Repository mutation |
| M5 | Durable, authenticated, observable read-only service | Auth, idempotency, durable receipts, staging fault/rollback tests, live runtime evidence | Autonomous actions |
| M6 | Personal Assistant read-only brief | Owner-scoped connector reads, source-bound Morning Intelligence Brief | Send/write |
| M7 | Capability Fabric and Unified Skills | Versioned manifests, pinned resolver, denial and replay tests | Automatic provider activation |
| M8 | Capability Foundry | Donor provenance, overlap, isolation, offline/shadow evaluation | Automatic code import |
| M9 | Approved personal actions | Prepare/review/approve/execute receipts bound to exact action | Unreviewed sending |
| M10 | Learning and REE lifecycle | Verified episodes, fixed-rubric offline/shadow evaluation, separate approval and profile pinning | Self-promotion |

M1-C precedes production runtime work. M2 and M3 can be developed as
separate bounded changes, but neither can claim a full cognitive service
without evidence binding and Kernel-enforced policy. M4 is the first
repository-intelligence vertical slice. M5's target is read-only Production
Grade v1; M6–M9 add personal use and controlled capabilities after that
foundation is demonstrated.

The requested **Sentient REE contracts and offline score v0** remains a
separate, side-effect-free increment. It may define typed metrics, exact
`ΔR`, candidate `α/β/γ` updates, `|δ| ≤ 0.05`, missing-metric handling,
normalization/cancellation guards, provenance, config versions, and
synthetic tests. That increment cannot wire REE into LangGraph, change the
active profile or `alpha_beta_gamma.yml`, write memory, activate
`reflective_heuristics.json`, grant authority, or integrate trading.
Later M10 promotion requires verified outcomes, an evaluator whose rubric
cannot be changed by candidate weights, and owner-controlled approval.

No date, cost, service-level target, provider, or deployment environment is
committed by this roadmap. Each step needs its own design decision and
measured acceptance evidence before it becomes the next current-state claim.
