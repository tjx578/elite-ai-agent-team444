# ADR-007 — Browser Capability Plane and WebMCP

- **Status:** Proposed ADR; derived from canonical README target design; runtime not implemented
- **Date:** 2026-09-29
- **Baseline reviewed:** `dd5cf74ce47e395cf859a2b5130790129af01e16`
- **Reconciliation:** 2026-10-01 against canonical `main@1410df328615325a7f8ac76574e6bf4b57bad68e`; historical reviewed baseline above is preserved
- **Related:** [root README](../../README.md), ADR-001, ADR-004, ADR-005, ADR-006; `docs/architecture/roadmap.md`

## Context

WOLF15 Sentient requires a browser capability path for Personal JARVIS: the
owner should be able to speak or type an intent, let Sentient use a live web
application when appropriate, and preserve the deterministic authority chain
used for repositories, backend MCP services and later controlled actions.

WebMCP is an active Web Machine Learning Community Group proposal that exposes
page functionality to agents as structured tools. The researched current
surface is `document.modelContext`; page tools are bound to browser document,
origin and session context. WebMCP complements backend MCP. It does not replace
service-side MCP and registration does not create authority.

Primary-source check on 2026-10-01: the [WebMCP draft dated 2026-09-30,
§4.1](https://webmachinelearning.github.io/webmcp/#extensions-to-document) attaches
`modelContext` to `Document`; [Chrome imperative API documentation updated
2026-09-21](https://developer.chrome.com/docs/ai/webmcp/imperative-api) likewise
uses `document.modelContext`. A prior review recommendation to substitute
`navigator.modelContext` is not applied to this current-source description.
Historical donor snapshots remain pinned separately; a future implementation
must verify its exact browser/API version rather than infer compatibility from
either spelling alone.

Research for this decision is pinned under
`docs/research/webmcp-donors/README.md`. The official specification repository
is the canonical protocol-knowledge source. Other repositories are donors for
types, authoring skills, browser integration, secure execution, fallback and
evaluation only.

## Decision

The [canonical root README](../../README.md) defines the target **Browser
Capability Plane**. This proposed ADR details that design, with WebMCP as the
preferred structured browser interface when a qualified page-provided tool can
satisfy the task.

Target ownership:

- `integrations/browser/webmcp/` — browser/session discovery, normalization,
  invocation and receipts.
- `capabilities/providers/webmcp/` — provider representation consumed by the
  Capability Registry and Resolver.
- `contracts/webmcp.py` — provider-independent WOLF15 descriptor, invocation
  and result/receipt contracts.
- `execution/browser/fallback/` — later bounded browser-automation fallback.
- `apps/owner-console/features/browser/` — owner-visible browser state,
  approvals and receipts.

Backend/service MCP remains under `mcp/`. Control Kernel owns task/workflow
state, authority, admission and termination. Capability Fabric owns
provider/capability lifecycle under Kernel admission; browser adapters report
session/descriptor invalidation without creating another task-state owner.
Publication of this proposal does not itself establish ADR acceptance.

### Execution classes

- `WEBMCP_NATIVE` means an actual page-provided structured WebMCP capability
  was discovered and invoked through the supported browser surface.
- `BROWSER_AUTOMATION_FALLBACK` means a separately qualified automation
  provider was used because native WebMCP could not satisfy the task.

These classes are never interchangeable evidence.

## Authority and security

1. A discovered tool is not automatically qualified, active or authorized.
2. `readOnlyHint`, `untrustedContentHint`, `consequentialHint`, descriptions
   and schemas are provider assertions. They are policy inputs, not authority.
3. Approvals and receipts bind task/run, origin, browser/session and exact
   document/navigation identity, tool identity, descriptor generation/digest,
   schema digest, arguments digest, policy/registry generation, execution class
   and authorized effects. Invocation revalidates these bindings; navigation,
   descriptor/schema changes, revocation or expiry reject the stale grant and
   require a fresh preview/approval. Timestamps, cancellation and outcome remain
   explicit in receipts.
4. Page content, tool metadata and tool results are untrusted external data.
5. A logged-in browser, cookie or enterprise SSO session is not task authority.
6. Page-local confirmation cannot become the WOLF15 authority root.
7. Ambiguous mutation outcomes are reconciled against authoritative state; they
   are not blindly retried.
8. Fallback automation fails closed on stale element/session state and may not
   masquerade as native WebMCP.

## Checkpoint allocation

| CP | WebMCP responsibility |
| --- | --- |
| CP1 | Protocol/contract research only; no browser execution |
| CP3 | Generic receipt, cancellation, origin/session identity, idempotency/recovery and telemetry semantics |
| CP4 | Native bounded read-only discovery/invocation through isolated or explicitly owner-scoped sessions; fixed profile and Kernel admission implemented and tested before invocation |
| CP5 | General registry/resolver, ephemeral provider lifecycle and pinned provider generations; task/workflow state remains Kernel-owned |
| CP6 | Qualification of WebMCP SDKs, skills, polyfills, bridges and fallback providers |
| CP7 | Consequential browser actions with exact approval, idempotency where applicable and independent verification |
| CP8 | WebMCP/browser-provider evaluation, regression, token/cost/latency and temporal drift analysis |
| CP9 | Integrated Browser Capability Plane after all earlier gates pass |

Checkpoint order follows README §10. CP4 does not depend on an unfinished CP5
resolver: it uses a native, fixed-profile admission prerequisite with explicit
no-provider, revocation and stale-document rejection. The general dynamic
resolver arrives at CP5. Donor SDK/code/skill/runtime imports wait for CP6
qualification and separate admission; earlier checkpoints may rebuild documented
principles natively. Qualification is offline-only under current policy. Connected
or shadow evaluation needs separately approved design, containment and evidence
paths; this ADR grants none.

## Explicitly rejected

- treating WebMCP as a replacement for backend MCP;
- importing an entire donor runtime into the core;
- `registered == qualified == authorized` semantics;
- page-local confirmation as owner authority;
- silent fallback from WebMCP to browser automation;
- persistent trust after navigation/session change;
- using WebMCP annotations as proof of side-effect class;
- autonomous consequential browser actions before CP7.

## Verification boundary

This ADR is architecture-only. It installs no browser, extension, polyfill,
WebMCP SDK, skill, bridge or runtime provider. It connects to no user browser
session and does not change the current `READ_ONLY` runtime authority.
