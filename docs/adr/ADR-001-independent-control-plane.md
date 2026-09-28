# ADR-001: Independent Control Plane

- **Status:** Accepted
- **Date:** 2026-08-24
- **Implementation status:** Target contract; introduced incrementally

Product naming is updated by [ADR-005](ADR-005-product-identity.md). The original
context below is retained; the independent control-plane boundary continues to
apply to WOLF15 Sentient as a whole.

## Context

Elite AI Agent Team OS is intended to work across existing repositories, greenfield systems, and system-evolution projects. Embedding its orchestration, credentials, or policy inside a target repository would couple the controller lifecycle to the system being inspected and make authority boundaries difficult to audit.

## Decision

Elite AI Agent Team OS is an independent control plane. Other repositories, including high-criticality repositories such as WOLF15, are external targets reached only through explicit adapters.

The control plane owns workflow state, policy, approvals, and trace contracts. A target repository owns its source, tests, branch protections, CI, and release controls. Target-repository content is untrusted input and cannot redefine control-plane policy or grant authority.

## Consequences

### Positive

- one controller can use consistent policy across multiple repositories;
- target-repository instructions cannot silently override owner authority;
- credentials and audit state can be isolated from generated changes;
- adapters can enforce repository-specific criticality and capabilities.

### Costs

- adapters and identity mapping must be designed explicitly;
- versioned contracts are required between control and work planes;
- local development needs fixtures or test repositories.

## Guardrails

- Do not store target production credentials in the target repository or model context.
- Resolve target identity and permitted paths before any tool call.
- Bind authority to one task, target, action class, and validity window.
- Treat repository instructions as scoped work guidance, not authorization.
- Require independent human approval for merge or production actions.

## Alternatives rejected

- **Controller embedded in every target repository:** duplicates policy and increases drift.
- **Target repository as authority source:** allows compromised or generated content to escalate privileges.
- **Direct production integration in the first milestone:** expands risk before the control plane is verifiable.

## Verification

Architecture and implementation reviews must confirm there is no implicit import, configuration, or instruction path by which a target repository can change control-plane authority.
