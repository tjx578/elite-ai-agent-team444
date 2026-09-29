# ADR-007 — Browser Capability Plane and WebMCP

- **Status:** Accepted target architecture; runtime not implemented
- **Date:** 2026-09-29
- **Baseline reviewed:** `dd5cf74ce47e395cf859a2b5130790129af01e16`
- **Related:** ADR-001, ADR-004, ADR-005, ADR-006; `docs/architecture/roadmap.md`

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

Research for this decision is pinned under
`docs/research/webmcp-donors/README.md`. The official specification repository
is the canonical protocol-knowledge source. Other repositories are donors for
types, authoring skills, browser integration, secure execution, fallback and
evaluation only.

## Decision

WOLF15 Sentient adds a **Browser Capability Plane** with WebMCP as the
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

Backend/service MCP remains under `mcp/`.

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
3. Origin, document/session identity, tool identity, schema/arguments digest,
   execution class, timestamps, cancellation and result status remain explicit
   in receipts.
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
| CP4 | Read-only WebMCP discovery/invocation through isolated or explicitly owner-scoped browser sessions |
| CP5 | Ephemeral provider normalization, registry/resolver integration and pinned task/session state |
| CP6 | Qualification of WebMCP SDKs, skills, polyfills, bridges and fallback providers |
| CP7 | Consequential browser actions with exact approval, idempotency where applicable and independent verification |
| CP8 | WebMCP/browser-provider evaluation, regression, token/cost/latency and temporal drift analysis |
| CP9 | Integrated Browser Capability Plane after all earlier gates pass |

Checkpoint order does not change.

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
