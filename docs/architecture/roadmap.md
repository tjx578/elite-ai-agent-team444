# WOLF15 Sentient architecture and delivery roadmap

## Checkpoint delivery order

The in-repository [Final Target Skeleton](final-target-skeleton.md) is the North
Star; delivery proceeds one checkpoint at a time. [Canonical ownership](canonical-ownership.md)
maps implemented paths to that target. CP0.1–CP0.3 are integrated at
`main@a53388f6`. CP0.4 architecture alignment merged in PR #15 at
`bad73335f518d89356b88cba1cc26730808cd224`, and CP0-ADDENDUM-01
froze `ALG-REG-001` in PR #16 at
`dd5cf74ce47e395cf859a2b5130790129af01e16`; exact-main CI and CodeQL
completed successfully on both resulting commits. CP0 remains open until CP0.5
records a final exact-resulting-main acceptance receipt after the current
architecture amendments. CP1 implementation starts only after that receipt.
WebMCP is added here as a cross-checkpoint target lane; it does not reorder
CP0–CP9 or activate browser authority.

| Checkpoint | Target | Acceptance / dependency |
| --- | --- | --- |
| CP0 Cognitive Foundation Stabilized | M2 + SK-01 + M3-A + SCRS v0 | Ordered CP0.1 SK-01, CP0.2 M3-A, CP0.3 SCRS, CP0.4 architecture, CP0.5 exact-main acceptance; READ_ONLY |
| CP1 Real Sentient Reasoning | M3-B | One real provider behind typed contracts, evidence binding, cancellation and limits; no tool authority |
| CP2 Repository Intelligence | M4 | Exact-revision repository read and source-bound analysis |
| CP3 Production Grade v1 | M5 | Authenticated durable observable read-only service and live acceptance |
| CP4 Personal JARVIS | M6 | Personal assistant, neural interface, voice, read-only connectors, and read-only browser/WebMCP discovery plus invocation |
| CP5 Capability OS | M7 | Capability registry/resolver plus Unified Skills; WebMCP page tools normalize as ephemeral, session-bound providers |
| CP6 Capability Foundry | M8 | Donor provenance, rights, isolation, evaluation and shadow lifecycle, including WebMCP skills/polyfills/bridges |
| CP7 Controlled Technology Builder | M9 | Prepare/review/approve/execute receipts for implementation, test, PR, personal actions, and consequential WebMCP invocations |
| CP8 Adaptive Intelligence | M10 | Validated learning, REE, mature SCRS, and WebMCP/browser-provider evaluation; independent evaluation, no self-promotion |
| CP9 Technology Company OS | Integrated product | End-to-end acceptance including the Browser Capability Plane; no shortcut around earlier gates |

All later checkpoints are frozen targets while CP0 is active. New ideas are
classified as current-checkpoint scope, architecture amendment, future
checkpoint, or out-of-architecture before implementation. The three
[README rules](canonical-ownership.md#local-readme-contract-policy) apply from
CP0.4 onward. Future subsystems get a README when their implementation appears.

The owner-designated `WOLF15_Sentient.html` is a Neural Orchestrator UX Reference
Prototype. Its relation to future `apps/owner-console/` (Next.js/TypeScript + SSE)
is frozen in the [UX reference boundary](canonical-ownership.md#neural-orchestrator-ux-reference).
No production console is built in CP0.

## Baseline and rule

The canonical repository is `tjx578/wolf15-sentient`. PR #1–#7 are merged.
The inspected M1-B `main` baseline is
`7ffac9a8254688649ecf8bca57e2ae7757bd9f32`; its CI installed the
package, passed 56 tests, and checked installed identity/entrypoint on Python
3.11–3.13. M1-C merged at `main` commit
`e14a96919dbd50350c4877393c40a069570d906c`; its
[CI](https://github.com/tjx578/wolf15-sentient/actions/runs/36379162914)
and [CodeQL](https://github.com/tjx578/wolf15-sentient/actions/runs/36379162867)
passed on that commit. These are historical commit-bound receipts. At that
checkpoint, the runtime was a deterministic `READ_ONLY` kernel with three
stubs and contract-only evidence/learning types. The separate
[M2 evidence/context evaluator](m2-evidence-context-runtime.md) subsequently
merged in [PR #11](https://github.com/tjx578/wolf15-sentient/pull/11) at
`main` commit `8cfabf70b2927c7eaf73ae8983df4f9ca7c069fb`; it is a pure
read path, not workflow wiring. No deployment,
Railway change, capability activation, or REE activation follows from these
checkpoints.
This roadmap does not turn a target into a current capability. Each milestone
must update [`current-state.md`](current-state.md) with exact-source and test
evidence.

| Step | Delivery | Acceptance gate | Excluded at that step |
| --- | --- | --- | --- |
| P0 — complete | PR #1–#4 consolidated; canonical repository name | Merge ancestry and CI on resulting main | Deployment |
| M1-B — complete | Freeze responsibility, trust, data, and authority boundaries in architecture docs | Merged PR #6 and CI on resulting `main` `7ffac9a` | Runtime wiring |
| M1-C — complete | Ownership and production trust foundation | Merged PR #7, active [main ruleset](https://github.com/tjx578/wolf15-sentient/rules/24097366), and CI plus CodeQL on resulting `main` `e14a969` | Production launch |
| M2 | Evidence/context read path | SourceRef resolution, freshness/conflict policy, grounded claims, read-only replay | Automatic learning |
| M3 | Schema-constrained reasoning adapters | Typed proposal contract, model-output validation, deterministic fallback and limits | Tool authority for models |
| M4 | Read-only repository intelligence | Exact-revision repository snapshot, provenance, grounded report | Repository mutation |
| M5 | Durable, authenticated, observable read-only service | Auth, idempotency, durable receipts, staging fault/rollback tests, live runtime evidence | Autonomous actions |
| M6 | Personal Assistant read-only brief + Browser Capability Plane v0 | Owner-scoped connector reads, source-bound brief, isolated or explicitly owner-scoped browser session, WebMCP tool discovery and read-only invocation | Send/write or consequential browser actions |
| M7 | Capability Fabric and Unified Skills | Versioned manifests, pinned resolver, denial/replay tests, ephemeral WebMCP provider normalization and lifecycle handling | Automatic provider activation |
| M8 | Capability Foundry | Donor provenance, overlap, isolation, offline/shadow evaluation, WebMCP skill/polyfill/bridge qualification | Automatic code import |
| M9 | Approved personal and browser actions | Prepare/review/approve/execute receipts bound to exact action, origin/session/tool identity and arguments | Unreviewed sending or consequential WebMCP execution |
| M10 | Learning and REE lifecycle | Verified episodes, fixed-rubric offline/shadow evaluation, WebMCP interface/provider benchmarks, separate approval and profile pinning | Self-promotion |

The [SK-01 skill selection assessment](../research/skill-selection/assessment.md)
and [adoption plan](skill-adoption-plan.md) are versioned research inputs. They
can guide qualification of development-workbench procedures during M2–M5.
They do not change this milestone order or activate product skills. Governed
runtime skill loading remains an M7 target; donor evaluation remains M8 work.

M1-C precedes production runtime work. M2 and M3 can be developed as
separate increments. [M3-A](m3a-reasoning-contracts.md) establishes task routing,
reasoning contracts, and the evidence bridge with offline adapters. M3-B must
then prove one approved real provider within these boundaries. SK-01 is a
supporting governance lane; completing all 25 candidate qualifications is not
a prerequisite for M3. M2 and M3 remain
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

## WebMCP cross-checkpoint lane

WebMCP is a browser capability protocol lane, not a new checkpoint and not a
replacement for backend MCP. See
[Browser Capability Plane / WebMCP](webmcp-browser-capability-plane.md),
[Final Target Skeleton](final-target-skeleton.md), and the
[WebMCP donor portfolio](../research/webmcp-donors/README.md).

| Checkpoint | WebMCP scope | Explicitly deferred |
| --- | --- | --- |
| CP1 | Research/spec knowledge only | Browser provider implementation or tool authority |
| CP2 | Exact-revision donor/source inspection where needed | Browser execution |
| CP3 | Generic receipt, cancellation, origin/session identity, idempotency/recovery and audit semantics | Live browser capability |
| CP4 | **Primary runtime entry:** read-only discovery and invocation in isolated or explicitly owner-scoped browser sessions | Consequential/mutating actions |
| CP5 | Normalize page tools as ephemeral providers and pin task/session/provider state | Registration becoming authority |
| CP6 | Qualify SDKs, polyfills, bridges, skills and fallback providers | Whole-runtime donor import |
| CP7 | Consequential actions with owner approval, exact invocation receipt and verification | Page-local approval as authority root |
| CP8 | Task-success, latency, token/cost, fallback-quality and temporal/provider evaluation | Self-promotion |
| CP9 | Integrated Browser Capability Plane | Bypassing earlier gates |

`WEBMCP_NATIVE` and `BROWSER_AUTOMATION_FALLBACK` are distinct execution
classes and never equivalent evidence.
