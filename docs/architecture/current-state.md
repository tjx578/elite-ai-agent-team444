# Current State

## Purpose

This document records what is demonstrably present in the repository. It is not a description of the eventual Elite AI Agent Team OS.

## PR-0 baseline

At the start of PR-0, the repository was at **Stage 0 — Blueprint and Documentation Foundation**. The only tracked project artifact was a vision-oriented `README.md`.

The following capabilities were **not implemented or verified** at that baseline:

- an installable Python package;
- a FastAPI application or runnable HTTP endpoint;
- typed request, report, gate, or execution contracts;
- project-mode routing;
- a deterministic orchestration workflow;
- LangGraph integration;
- OpenAI or any other model integration;
- repository, shell, Git, GitHub, or deployment tools;
- execution tracing or persistence;
- automated tests or continuous integration;
- an Owner Console.

PR-0 added documentation and architecture decision records. Documentation is not runtime evidence.

## PR-1 executable foundation

PR-1 adds a small, locally executable foundation. The current implementation contains:

- an installable `elite_team` Python package requiring Python 3.11 or newer;
- FastAPI application factory and ASGI entry point;
- `GET /health`, returning service identity and version;
- `POST /tasks`, accepting a strict `TaskRequest` and returning a strict `TaskResponse`;
- `READ_ONLY` as the only accepted authority;
- the three project-mode enum and a deterministic mode router;
- in-memory `TaskState` creation with unique task, run, and trace identifiers;
- correlated trace events for `INTAKE`, `MODE_ROUTER`, and `STATE_CREATION`;
- integration tests for health, the three routing outcomes, fail-closed validation, trace shape/correlation, and identifier uniqueness;
- a GitHub Actions workflow definition for Python 3.11, 3.12, and 3.13.

Local verification on 2026-08-24:

```text
python -m pytest -q
10 passed in 7.54s
```

The GitHub Actions file is present, but no authenticated remote run was inspected in this workstream. Remote CI status is therefore **NOT_EXECUTED / NOT_VERIFIED here**, not PASS.

## Exact PR-1 flow

```text
HTTP request
  -> Pydantic validation
  -> INTAKE trace
  -> deterministic MODE_ROUTER
  -> in-memory TaskState creation
  -> STATE_CREATION trace
  -> typed HTTP response with FOUNDATION_COMPLETE
```

Routing is intentionally narrow:

- no repository -> `GREENFIELD_SYSTEM_MODE`;
- repository plus an explicit supported evolution action/phrase -> `HYBRID_EVOLUTION_MODE`;
- any other repository-bearing request -> `EXISTING_REPO_MODE`.

The supplied repository is not resolved, fetched, read, or validated as an accessible repository.

## Still target-only

PR-1 does **not** provide:

- any architect, reviewer, engineer, security, performance, or operations role;
- architecture, implementation, security, performance, or production gates;
- a revision or retry loop;
- LangGraph or another complete graph runtime;
- OpenAI or any other model integration;
- repository, file, shell, test-runner, Git, GitHub, or deployment adapters;
- persistence, checkpoints, approval/resume, or long-term memory;
- a readiness decision (the response has `final_decision: null`);
- an Owner Console or production deployment.

## Evidence policy

A capability moves from target to current only when all applicable evidence exists:

1. implementation is present in the repository;
2. its public contract is documented;
3. focused tests exercise its important behavior;
4. the documented verification command passes in the current checkout;
5. external services are described as integrated only when authenticated runtime evidence exists.

Code presence alone does not prove a service is deployed, a remote CI job has run, an external integration works, or a production action is safe.

## Current authority boundary

PR-1 accepts only `READ_ONLY`, but currently has no external repository adapter, so it does not read the repository named in a task. It grants no file, shell, Git, GitHub, deployment, production-data, or other external-system authority.

The normative target authority model is defined in [Authority Model](../governance/authority-model.md) and [ADR-004](../adr/ADR-004-human-controlled-production.md).

## Next workflow milestone

The completed PR-1 slice is:

```text
validated task request
        -> project-mode classification
        -> deterministic state transition
        -> typed response and trace
        -> automated verification
```

The next milestone should add the deterministic graph, bounded revision behavior, and stub roles while keeping model and repository-execution variability out of the loop. The current foundation must not be described as a complete multi-agent OS.
