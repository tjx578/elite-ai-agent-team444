# ADR-005: WOLF15 Sentient Product Identity and Namespace

- **Status:** Accepted and merged on canonical `main`
- **Date:** 2026-09-28
- **Baseline:** PR-2 `df43c93e12b2ff68ce4fe1c2d3778a6052886413`
- **Related:** [ADR-001](ADR-001-independent-control-plane.md), [ADR-002](ADR-002-deterministic-orchestrator.md)

## Decision

WOLF15 Sentient identifies the complete product. Its canonical repository name,
Python distribution, and health service identifier are `wolf15-sentient`.
The Python package is `wolf15_sentient`. Elite AI Agent Team OS identifies the
specialist organization within the product. WOLF15 Trading System remains an
external system with its own strategy, risk, and execution authority.

Sentient Core / Neural Orchestrator proposes plans and synthesizes responses.
The Control Kernel owns workflow state, transitions, authority, gates, and
termination throughout the product. A model proposal or product name grants
no tools or permissions. Simple response paths still require the relevant
policy checks. Future execution adapters must enforce policy at their call
boundary; policy declarations alone do not provide enforcement.

Intelligence Division performs research, analysis, and source verification.
Knowledge provides sourced storage and retrieval. Memory retains context and
decisions according to their lifecycle. Workflow state belongs to the kernel.
The Capability Fabric is a target for capability descriptions and authorized
adapter access. None of these target components is introduced by this rename.

## Migration boundary

This increment changes the top-level namespace, package metadata, imports,
ASGI command, API title, health literal, tests, CI identity check, and documents.
The existing `api/`, `contracts/`, `agents/`, and `orchestration/` folders remain
inside the product package. The kernel's algorithms, revision caps, typed
workflow contracts, and READ_ONLY authority policy retain the PR-2 behavior.

The future `orchestration -> control` and `agents -> elite_team` moves belong
to a separate increment. A `sentient/` package requires a later intelligence
milestone. Moving the complete old package into `wolf15_sentient/elite_team`
would incorrectly subordinate product-wide API, contracts, and control.

## Compatibility

This is an intentional breaking rename for consumers of `elite_team`, the
`elite-ai-agent-team` distribution, the old ASGI path, and the old health literal.
No compatibility alias or second package is shipped. Consumers must update
these references together. The unpublished package version remains `0.1.0`.
Any release process must assess versioning before publication.

## Evidence and sequencing

The identity migration started at PR-2, which included PR-1 commit
`107eae91d681d6bbd5786483ea8c84db1e4b6088` at the original checkpoint.
The repository is now `tjx578/wolf15-sentient`; PR #1–#4 are merged on `main`
at `64ae79f`. Final CI ran on that exact commit and passed 56 tests plus
installed identity checks on Python 3.11–3.13. The separate uncommitted PR-3
model-adapter work in the primary checkout still requires its own port and
verification under the new namespace.

The proposed six divisions and 28 specialists remain an organizational target.
A complete roster with five additional Intelligence Division roles, input/output
contracts, and task boundaries is still required. This change does not invent
that roster or assert that the unavailable organization diagram was inspected.
Three deterministic roles exist at this baseline: architect, engineer, reviewer.

## Acceptance

- Build and install the renamed distribution; import its installed namespace.
- Load `wolf15_sentient.main:app` and verify API/OpenAPI identity.
- Reject the old health service literal and unsupported authority values.
- Pass routing, trace, isolation, transition, revision, and exhaustion tests.
- Verify the original PR-3 checkout is unchanged.
- Record local evidence separately from remote CI and provider/runtime evidence.

Full remote acceptance requires CI steps actually executed at the delivered
migration SHA. Local acceptance does not satisfy that requirement.
