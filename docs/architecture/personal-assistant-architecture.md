# Personal Assistant and Owner OS

## Status

**M1-B target design.** The current runtime has no Gmail, Calendar, Drive,
contacts, search, YouTube, news, messaging, reminder, or background-event
adapter. The only current HTTP task path is the deterministic in-memory
kernel described in [`current-state.md`](current-state.md). This document
does not connect an account or authorize messages, orders, or writes.
WhatsApp, Telegram, and Slack are later candidate communication channels;
their presence in a plan does not establish a connector or consent.

## Boundary

The Personal Assistant translates an owner's request or an explicitly
approved event into a scoped task. The Control Kernel validates caller,
authority, target, and lifecycle. Each connector supplies a narrow capability
and returns source-bound observations through the
[Second Brain](second-brain-architecture.md). Sentient Core may assemble a
brief or draft, but a connector acts only after the Kernel's boundary check.

| Phase | Example | Authority ceiling |
| --- | --- | --- |
| CP4 read-only | Read calendar/mail/Drive/web/news/project status; discover and invoke qualified read-only WebMCP tools in an isolated or explicitly owner-scoped browser session | Scoped reads only |
| CP7 controlled action | Draft a message/calendar change or prepare a consequential WebMCP action | Owner-visible draft/plan; no effect without exact approval |
| Later approved action | Send or create an exact reviewed artifact | Separate action-specific approval and adapter enforcement |

The first end-to-end use case is a **Morning Intelligence Brief** assembled
from permitted calendar, mail, project, research, and pending-task sources.
Every item must retain source, freshness, access scope, and uncertainty.
Unavailable connectors produce `NOT_MEASURED` sections; they do not create
fabricated brief content. Search results and third-party text are untrusted
data, not instructions to the assistant.

## Data and control flow

```text
Owner -> task scope -> Kernel
                      -> read-only connector set -> SourceRef[] -> ContextBundle
                      -> browser session -> WebMCP discovery -> read-only invocation receipt
                      -> Core draft -> evidence check -> owner brief
```

Connector credentials belong to the connector's least-privilege boundary,
not to prompts, durable memory, or cross-provider context. The design must
minimize retrieved content, keep source-specific access controls, and avoid
passing private mail or contact data to another provider without a defined
policy. Proactive runs require an owner-selected schedule, source set,
delivery destination, and notification policy. No schedule is active here.

## Failure and acceptance

- Denied scope or expired consent blocks the connector call and records a
  sanitized receipt when that adapter exists.
- A partial source outage yields a clearly partial brief; required evidence
  remains missing. No retry of an ambiguous external mutation is automatic.
- CP4 is accepted only after authenticated read-only connector tests,
  provenance/freshness checks, an owner-visible brief on real permitted data,
  and a bounded browser vertical slice proving WebMCP discovery plus read-only
  invocation with origin/session/tool receipts.
- CP7 needs draft validation, consequential browser-action classification,
  exact owner approval, idempotency/recovery where relevant, and independent
  verification of authoritative state.

Provider choices, consent lifetime, retention, regional data handling, and
notification defaults are open decisions. They are not inferred from a
connected app or from this diagram.

## WebMCP browser boundary

Voice and text enter the same task-intake path. Voice is transport, not
authority. WebMCP tools are untrusted capability descriptors until the
Capability Resolver and Control Kernel admit an exact invocation.

CP4 should prefer an isolated browser context. Reuse of a real owner browser,
cookies or enterprise SSO is higher-scope and requires explicit session policy.
A logged-in page is not permission to mutate it.

Backend MCP remains appropriate for persistent service capabilities. WebMCP is
page/session bound and must not be stored as a permanent backend provider.
