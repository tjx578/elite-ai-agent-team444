# Browser Capability Plane / WebMCP

## Status

**Derived target design. Runtime not implemented.** The [root README §10](../../README.md#10-roadmap-master-cp0cp9) owns checkpoint order and gates; the
[roadmap](roadmap.md) and this document are subordinate views, not acceptance
or activation decisions.

The last verified pre-amendment canonical main inspected for this design is
`dd5cf74ce47e395cf859a2b5130790129af01e16`. This document defines future
browser capability ownership and checkpoint boundaries. Reconciliation on
2026-10-01 used canonical `main@1410df328615325a7f8ac76574e6bf4b57bad68e`;
the earlier baseline above remains historical provenance. Current API naming
is documented with dated primary sources in [ADR-007](../adr/ADR-007-webmcp-browser-capability-plane.md).

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
  -> CP4 fixed native read-only profile admission / CP5 general resolver
  -> Kernel authorizes exact invocation
  -> execute page tool
  -> WebToolResult + ExecutionReceipt
  -> evidence/context
  -> owner-visible result
~~~

CP4 must implement and test the fixed native profile, exact descriptor binding,
revocation and Kernel admission before its first invocation; it returns an
explicit no-provider result when those requirements cannot be met. It does not
wait on or silently emulate the CP5 dynamic resolver. At CP5 or later, if no
qualified WebMCP tool satisfies the request, the Resolver may consider a
separately qualified `BROWSER_AUTOMATION_FALLBACK`. Fallback is explicit and
is not equivalent evidence to `WEBMCP_NATIVE`. Any donor fallback package must
first pass CP6 qualification and separate admission; consequential effects
remain gated by CP7 regardless of execution class.

## WOLF15 contracts

Future `contracts/webmcp.py` normalizes browser observations into WOLF15
contracts.

### WebCapabilityDescriptor

- canonical capability ID and provider ID;
- browser session, exact document/navigation and page identity;
- origin and discovery timestamp;
- tool name/title/description, descriptor generation/digest and input-schema digest;
- annotations as untrusted provider metadata;
- provider/capability lifecycle state and discovery receipt;
- required authority/data classes;
- qualification/evaluation receipts.

### WebToolInvocation

- task/run ID and policy/registry generation;
- browser/session, exact document/navigation identity and origin;
- exact tool identity, descriptor generation/digest, schema digest and arguments digest;
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
invalidate a descriptor. Fabric owns provider/capability lifecycle under Kernel
admission. Control Kernel owns task/workflow state, authority and termination;
page lifecycle does not transfer that ownership to a provider. Invocation must
recheck the bound document/navigation identity and descriptor/schema generation
and digest, not merely origin or tool name. Any mismatch fails closed.

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
approval bound to task/run, browser/session, origin, document/navigation identity,
tool, descriptor generation/digest, schema digest, arguments digest, execution
class, policy/registry generation and authorized effects -> Kernel authorization ->
idempotency/correlation where applicable -> execution -> durable receipt ->
authoritative verification. Unknown outcomes are reconciled, not blindly
retried. A navigation or descriptor/schema update between approval and call,
revocation, expiry or changed arguments invalidates that approval. The adapter
rejects the stale call and requires a new preview and approval; same-origin or
same-name rediscovery cannot inherit the old grant.

## Donor-derived knowledge

The researched donor portfolio under `docs/research/webmcp-donors/` provides
protocol canon/types, authoring skills, retrofit/verification workflows, secure
mutation/recovery patterns, polyfill/bridge/fallback patterns and evaluation
methodology. Donors are not runtime dependencies until CP6 qualification.

## Acceptance extensions

### CP4
- discover a real WebMCP tool in an allowed session;
- prove the bounded native fixed-profile admission prerequisite before invocation;
- bind descriptor to origin/session/document/navigation and descriptor/schema generation/digests;
- execute a read-only tool and emit a receipt;
- cancellation and stale-descriptor behavior are explicit;
- unsupported WebMCP does not silently become fallback.

### CP5
- normalize ephemeral provider descriptors;
- deny stale session/origin/document/tool/descriptor/schema/policy generation mismatches;
- no automatic provider activation.

### CP6
- exact donor SHA/provenance/license/security/dependency review;
- native/polyfill/bridge/fallback comparison;
- skill overlap/diff qualification;
- sandboxed independent offline evaluation; connected/shadow execution remains
  blocked until its separate design, containment and evidence path are approved.

### CP7
- exact owner approval for consequential invocation, with negative tests for
  navigation and descriptor/schema changes between approval and call;
- idempotency/recovery where applicable;
- durable receipt and authoritative verification.

### CP8
- regression corpus for tool selection/arguments/outcomes;
- task success, latency, token/cost and fallback-quality metrics;
- temporal compatibility/provider drift;
- no self-promotion.
