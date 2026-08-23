# ADR-002: Deterministic Orchestrator

- **Status:** Accepted
- **Date:** 2026-08-24
- **Implementation status:** Implemented; local and security verification complete, remote CI `NOT_EXECUTED` because no job obtained a runner under the GitHub billing lock

## Context

Model reasoning is probabilistic and may return malformed output, request unauthorized tools, repeat work, or choose inconsistent next steps. Letting a model own workflow control would make gates, retries, and safety behavior difficult to test.

## Decision

The Neural Orchestrator is a deterministic controller, not an unconstrained agent.

Code-defined policy owns:

- valid workflow states and transitions;
- project-mode routing inputs and outputs;
- role selection and node order;
- schema validation;
- gates, retry limits, and revision counters;
- authority checks before tool execution;
- trace emission and terminal decisions.

Reasoning roles receive bounded context and return typed proposals. They cannot invoke one another directly, approve their own output, choose arbitrary transitions, or increase authority.

The implemented maximum is two revisions for each architecture and engineering review loop. Exhaustion produces `BLOCKED_REQUIRES_OWNER`.

## Consequences

### Positive

- control flow can be unit and integration tested without a model;
- malformed output fails closed at a clear boundary;
- traces explain why a node or transition occurred;
- deterministic stubs can validate the operating system before model integration.

### Costs

- contracts and transition rules require deliberate maintenance;
- workflow changes need code and test updates;
- exceptional cases must be modeled explicitly rather than delegated vaguely.

## Guardrails

- Model text is data, never executable control instructions.
- All inter-node outputs pass schema validation.
- Every loop has a finite counter and terminal failure state.
- A final status is calculated from gate results and evidence, not model confidence.
- LangGraph, if adopted, implements the state machine; its presence does not replace policy design.

## Alternatives rejected

- **Free-running autonomous agent:** insufficiently predictable and auditable.
- **Prompt-only gates:** model compliance is not an enforcement boundary.
- **Unbounded reviewer loops:** can consume resources indefinitely without owner visibility.

## Verification

Tests must cover valid transitions, rejected transitions, invalid schemas, revision exhaustion, unauthorized tool requests, and terminal decision calculation.
