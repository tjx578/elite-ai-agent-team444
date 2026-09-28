# Target Architecture

## Status

Use the [canonical ownership map](canonical-ownership.md) for the CP0 current
implementation, target destinations and README policy. This document retains
the broader design; target folder names do not authorize duplicate owners or
automatic migration.

This document defines the architecture beyond the PR-2 deterministic kernel. Components described here are not current capabilities unless they are also listed in [Current State](current-state.md).

The M1-B [reference architecture](super-intelligence-reference-architecture.md)
and [roadmap](roadmap.md) extend this original kernel-focused target to the
Personal Assistant, Second Brain, Capability Fabric/Foundry, production trust,
and REE boundaries. The PR numbers in the delivery sequence below are
historical milestone labels, not the GitHub PR #1–#4 consolidation order.

## Design goals

WOLF15 Sentient is intended to be an independent, auditable product for software-engineering work. Its control plane should:

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
WOLF15 Sentient Control Plane
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

### Product responsibilities

| Component | Responsibility | Current implementation |
| --- | --- | --- |
| WOLF15 Sentient | Product identity encompassing interfaces, reasoning, control, specialists, and integrations | Renamed API and deterministic foundation |
| Sentient Core / Neural Orchestrator | Interpret intent, propose plans and specialist needs, synthesize responses | Target; no live reasoning component |
| Control Kernel | Own workflow state, transitions, policy, authority checks, gates, and termination | PR-2 deterministic in-memory kernel |
| Elite AI Agent Team OS | Organize task specialists and their bounded outputs | Three deterministic architect, engineer, reviewer stubs |
| Intelligence Division | Research, analysis, and source verification | Target; roster and contracts pending |
| Knowledge & Memory | Store and retrieve sourced context and lifecycle-bound decisions | Target; no persistence or retrieval implementation |
| Capability Fabric | Describe capabilities and mediate access through authorized tools and adapters | Target; no execution adapters |
| Learning & Adaptation Plane | Journal evidence-backed episodes and produce evaluated capability/workflow candidates without raising authority | Contracts only; not wired to workflow |
| WOLF15 Trading System | Own trading strategy, risk controls, and execution | External; no integration in this foundation |

The Core proposes work; the Control Kernel enforces admissibility throughout
the product, including relevant checks for simple response paths. Memory does
not own workflow state. Policy configuration requires enforcement at the
execution boundary before an adapter can act.

Six divisions and 28 specialists are an organizational target, not running
agents or services. The complete roster, including five proposed Intelligence
Division roles and their input/output boundaries, requires a separate design.
This migration introduces no new role implementations.

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

PR-2 implements the in-memory core: valid states, node ordering, gate transitions, two bounded revision loops, typed failure behavior, and terminal decisions. Timeouts, persistence, external execution, and production operations remain later work. Reasoning components propose typed outputs; they do not choose arbitrary next steps or bypass gates.

### Reasoning adapters

PR-2 provides deterministic architect, reviewer, and engineer stubs with narrow typed contracts and no tool authority. Model-backed versions, plus security, performance, and operations roles, remain later work.

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
