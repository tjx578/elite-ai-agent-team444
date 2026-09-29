# Browser Capability Plane / WebMCP

## Status

**Target design. Runtime not implemented.**

The last verified pre-amendment canonical main inspected for this design is
`dd5cf74ce47e395cf859a2b5130790129af01e16`. This document defines future
browser capability ownership and checkpoint boundaries.

## Capability family

~~~text
browser.webmcp
├── discover
├── invoke
├── author
├── declarative
├── lifecycle
├── secure-action
├── retrofit
├── browser-fallback
├── bridge
└── evaluate
~~~

## Preferred execution path

~~~text
Owner voice/text
  -> authenticated task intake
  -> Sentient Core proposal
  -> Control Kernel task scope
  -> Browser Session
  -> WebMCP discovery
  -> normalize WebCapabilityDescriptor[]
  -> Capability Resolver
  -> Kernel authorizes exact invocation
  -> execute page tool
  -> WebToolResult + ExecutionReceipt
  -> evidence/context
  -> owner-visible result
~~~

If no qualified WebMCP tool satisfies the request, the Resolver may consider a
separately qualified `BROWSER_AUTOMATION_FALLBACK`. Fallback is explicit and
is not equivalent evidence to `WEBMCP_NATIVE`.

## WOLF15 contracts

Future `contracts/webmcp.py` normalizes browser observations into WOLF15
contracts.

### WebCapabilityDescriptor

- canonical capability ID and provider ID;
- browser session/document/page identity;
- origin and discovery timestamp;
- tool name/title/description and input-schema digest;
- annotations as untrusted provider metadata;
- lifecycle state and discovery receipt;
- required authority/data classes;
- qualification/evaluation receipts.

### WebToolInvocation

- task/run ID and policy/registry generation;
- browser/session/document/origin;
- exact tool identity and arguments digest;
- requested execution class;
- authority grant and approval reference when required;
- cancellation/deadline.

### WebToolResult

- execution class: `WEBMCP_NATIVE` or `BROWSER_AUTOMATION_FALLBACK`;
- provider identity/revision where measurable;
- timestamps and output digest;
- explicit error/degraded/unknown outcome;
- untrusted-content indicator;
- evidence/receipt references;
- independent verification when required.

## Lifecycle and trust

WebMCP tools are ephemeral. Route changes, navigation, iframe/origin exposure,
session loss, `toolchange`, provider revocation or page destruction can
invalidate a descriptor.

~~~text
TOOL_PRESENT != QUALIFIED
QUALIFIED != ACTIVE
ACTIVE != AUTHORIZED_FOR_THIS_TASK
readOnlyHint != proof of read-only
consequentialHint != approval
successful return != independently verified effect
~~~

## WebMCP vs backend MCP

| Dimension | Backend MCP | WebMCP |
| --- | --- | --- |
| Primary owner | `mcp/` | `integrations/browser/webmcp/` |
| Lifetime | service/provider | page/document/session |
| Authentication context | connector/service credential | browser/page session plus WOLF15 policy |
| Registry representation | persistent qualified provider | ephemeral provider instance |
| Consequential authority | Kernel/approval | Kernel/approval; page confirmation is insufficient |

## Browser session policy

CP4 starts read-only and prefers an isolated browser context. Reuse of a real
owner browser profile, cookies, SSO or already-open tabs is higher-scope and
must be explicitly policy-bound. An authenticated page is not permission to
mutate it.

## Consequential actions

CP7 introduces mutation only through proposal -> exact action preview -> owner
approval bound to task/session/origin/tool/args -> Kernel authorization ->
idempotency/correlation where applicable -> execution -> durable receipt ->
authoritative verification. Unknown outcomes are reconciled, not blindly
retried.

## Donor-derived knowledge

The researched donor portfolio under `docs/research/webmcp-donors/` provides
protocol canon/types, authoring skills, retrofit/verification workflows, secure
mutation/recovery patterns, polyfill/bridge/fallback patterns and evaluation
methodology. Donors are not runtime dependencies until CP6 qualification.

## Acceptance extensions

### CP4
- discover a real WebMCP tool in an allowed session;
- bind descriptor to origin/session/document and schema digest;
- execute a read-only tool and emit a receipt;
- cancellation and stale-descriptor behavior are explicit;
- unsupported WebMCP does not silently become fallback.

### CP5
- normalize ephemeral provider descriptors;
- deny stale session/origin/tool/policy mismatches;
- no automatic provider activation.

### CP6
- exact donor SHA/provenance/license/security/dependency review;
- native/polyfill/bridge/fallback comparison;
- skill overlap/diff qualification;
- sandbox/offline/shadow evaluation.

### CP7
- exact owner approval for consequential invocation;
- idempotency/recovery where applicable;
- durable receipt and authoritative verification.

### CP8
- regression corpus for tool selection/arguments/outcomes;
- task success, latency, token/cost and fallback-quality metrics;
- temporal compatibility/provider drift;
- no self-promotion.
