# Target Architecture

## Status

This document defines the desired architecture. Components described here are not current capabilities unless they are also listed as verified in [Current State](current-state.md).

## Design goals

Elite AI Agent Team OS is intended to be an independent, auditable control plane for software-engineering work. It should:

- accept a bounded owner objective and explicit authority;
- classify the work into one of three project modes;
- coordinate specialized reasoning behind typed contracts;
- keep workflow control deterministic and inspectable;
- execute repository operations only through constrained adapters;
- retain evidence for every gate and decision;
- stop safely when evidence or authority is insufficient;
- reserve merge and production decisions for the owner.

## System boundary

```text
Owner
  |
  v
Owner Console or API client                 TARGET
  |
  v
Elite Control Plane
  +-- Intake and contract validation
  +-- Authority and policy enforcement
  +-- Project Mode Router
  +-- Deterministic Orchestrator
  +-- Gate and revision controller
  +-- Trace and decision ledger
  |
  +------ typed requests and reports ------+
  |                                         |
  v                                         v
Reasoning adapters                    Execution adapters
(architect/reviewer/engineer)         (repo/files/test/Git/GitHub)
  |                                         |
  +---------------- evidence ---------------+
                    |
                    v
             Owner decision gate

Target repositories and production systems remain outside the control plane.
```

The control plane must not be embedded inside a target repository. A repository such as WOLF15 is a target reached through a policy-constrained adapter, not a source of authority for the control plane.

## Logical components

### API and intake

Validates requests, assigns task/run/trace identifiers, and rejects malformed or unsupported input. Authentication and caller identity become mandatory before any non-local or mutating authority is exposed.

### Typed contracts

Machine-readable contracts define task requests, reports, gate decisions, workflow state, execution events, and final decisions. Free-form model text may be supporting evidence, but it must not be the control protocol between components.

### Project Mode Router

Classifies a task into exactly one of:

- `EXISTING_REPO_MODE`;
- `GREENFIELD_SYSTEM_MODE`;
- `HYBRID_EVOLUTION_MODE`.

Mode classification changes the workflow plan; it does not increase authority.

### Deterministic Orchestrator

Owns valid states, node ordering, gate transitions, revision limits, timeouts, failure behavior, and terminal decisions. Reasoning components propose typed outputs; they do not choose arbitrary next steps or bypass gates.

### Reasoning adapters

Architect, reviewer, engineer, security, performance, and operations roles are introduced incrementally. Each adapter has a narrow input/output contract and no implicit tool authority. Early milestones should use deterministic stubs to validate the operating system before introducing model variability.

### Execution adapters

Repository reading, file changes, shell execution, tests, Git, GitHub, and deployment are separate adapters. Each call is checked against task-scoped authority and emits audit evidence. The safe progression is:

```text
read-only -> proposed patch -> isolated worktree -> feature branch
          -> tests -> draft PR -> human approval -> deployment
```

Later steps are not implied by earlier ones.

### Trace and decision ledger

Every workflow node records identifiers, timestamps, status, input/output references, evidence, errors, and decisions. Sensitive data and credentials must never be persisted as trace content.

### Persistence and resume

Durable state, checkpoints, approval requests, and resume are target capabilities. Persistence must preserve idempotency and ensure an expired or modified approval cannot be replayed as authority.

### Owner Console

The UI is a later consumer of stable API and trace contracts. It displays state and requests approval; it does not weaken policy or manufacture authority.

## Trust boundaries

1. **Caller to control plane:** authenticate identity, validate input, and bind explicit authority.
2. **Control plane to model:** treat model output as untrusted structured proposals.
3. **Control plane to execution adapter:** authorize each action, constrain scope, and record evidence.
4. **Execution adapter to target repository:** isolate changes and protect default branches.
5. **Control plane to external services:** use least-privilege credentials and distinguish configured from verified connectivity.
6. **Draft PR to production:** require a separate human-controlled decision and deployment mechanism.

## Failure behavior

The system fails closed when a contract is invalid, required evidence is missing, the revision limit is exhausted, an adapter exceeds its scope, or authority is insufficient. The expected terminal result is `BLOCKED_REQUIRES_OWNER` or `NOT_READY`, not an optimistic success status.

## Delivery sequence

| Milestone | Scope | Explicitly excluded |
| --- | --- | --- |
| PR-0 | Truth alignment, architecture contracts, ADRs, authority model | Runtime claims |
| PR-1 | Python/API/contracts/router/state/trace foundation with tests | LangGraph, model calls, repo execution |
| PR-2 | Deterministic graph, bounded revision loop, stub roles | Real model reasoning |
| PR-3 | Schema-constrained model adapters | Repository mutation |
| PR-4 | Read-only and isolated repository execution | Main-branch or production authority |
| PR-5 | Feature branch and draft PR delivery | Autonomous merge/deploy |
| PR-6 | Durable state, approval, and resume | Owner Console |
| PR-7 | Owner Console over stable contracts | Policy bypass |
| PR-8+ | Additional specialists, memory, optimization | Authority expansion by default |

Each milestone must update [Current State](current-state.md) using repository and test evidence.
