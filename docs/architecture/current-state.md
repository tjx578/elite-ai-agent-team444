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

The original PR-1 checkpoint was verified locally on 2026-08-24:

```text
python -m pytest -q
10 passed in 7.54s
```

The original GitHub Actions jobs were **NOT_EXECUTED** because GitHub billing
blocked runner allocation. The reviewed PR-1 head `cec55f5` was later verified
locally with 30 passing tests and Ruff, and its push and pull-request CI jobs
passed on Python 3.11, 3.12, and 3.13. These results are bound to that head;
the integrated PR-2 head requires its own verification.

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
The caller must provide `READ_ONLY`; intent is capped at 4096 characters and
the repository reference at 2048. The response, state, and `MODE_ROUTER` trace
preserve the routing reason.

## PR-1 exclusions at that milestone

The PR-1 baseline did **not** provide:

- any architect, reviewer, engineer, security, performance, or operations role;
- architecture, implementation, security, performance, or production gates;
- a revision or retry loop;
- LangGraph or another complete graph runtime;
- OpenAI or any other model integration;
- repository, file, shell, test-runner, Git, GitHub, or deployment adapters;
- persistence, checkpoints, approval/resume, or long-term memory;
- a readiness decision (the response has `final_decision: null`);
- an Owner Console or production deployment.

## PR-2 Deterministic Orchestration Kernel

Source inspection confirms that PR-2 adds an in-memory, deterministic orchestration kernel:

- LangGraph `1.2.10`, pinned as a runtime dependency;
- a compiled `StateGraph` with code-defined nodes and conditional edges;
- typed, side-effect-free architect, engineer, and reviewer stubs;
- typed architecture, implementation, validation, review, gate, workflow-result, and execution-event contracts;
- explicit allowed-transition and required-state validators;
- separate architecture and engineering revision counters, each capped at two;
- immutable, correlated events for all attempted nodes, with contiguous sequence, timestamps, status, references, revision count, decision, and optional error classification;
- error codes for invalid role output, missing state, illegal transitions, revision exhaustion, and deterministic validation failure;
- final-decision vocabulary limited to `READY_WITH_CONDITIONS`, `NOT_READY`, and `BLOCKED_REQUIRES_OWNER`.

The compiled graph is:

```text
START
  -> INTAKE
  -> MODE_ROUTER
  -> STATE_CREATION
  -> ARCHITECT
  -> ARCHITECTURE_REVIEW
       -> ARCHITECT (revision, maximum 2)
       -> ENGINEER (approved)
       -> FINALIZE (blocked/failure)
  -> ENGINEER
  -> VALIDATION
  -> REVIEWER
       -> ENGINEER (revision, maximum 2)
       -> FINALIZE (approved/blocked/failure)
  -> END
```

The default stub script approves both gates and produces `WORKFLOW_COMPLETE` with `READY_WITH_CONDITIONS`. Revision exhaustion or invalid typed role output produces `WORKFLOW_BLOCKED` with `BLOCKED_REQUIRES_OWNER`. `NOT_READY` is part of the strict terminal contract; its exact reachable policy path must be confirmed by final PR-2 tests before it is claimed as exercised behavior.

### PR-2 verification status

- Source inspection: **COMPLETE** for the kernel, contracts, transitions, and stubs described above.
- Local PR-2 tests: **PASS** — a fresh environment ran 25 tests in 3.12 seconds.
- Graph smoke verification: **PASS** — compile/render, happy path, bounded revision, and revision-exhaustion checks completed.
- Ruff: **PASS** — `ruff check src tests` completed with no findings.
- Security review: **COMPLETE** — Codex Security diff scan `5a286602-d315-49c9-bd7a-1fefe5ab7db5` reviewed all 12 source/config inventory items plus supporting tests and documentation, closed coverage as complete, and reported zero findings. Three candidate hardening concerns were reproduced and rejected after validation because no current attacker-to-privileged-sink path exists under the local, in-memory, no-deployment boundary.
- Remote PR-2 CI: **NOT_EXECUTED** for initial commit `0eb800d`. Push run `32656762669` and pull-request run `32656786609` each created Python 3.11, 3.12, and 3.13 jobs, but every job had zero steps and `runner_id=0`. GitHub annotated both runs with the account billing lock, so this is neither PASS nor a code/test failure.

The completed PR-2 security review and PR-2 `NOT_EXECUTED` result are separate from the preserved PR-1 local test result and foundation CI record.

## PR-2 hard exclusions

PR-2 contains no:

- OpenAI, Codex, or other model-backed reasoning;
- repository reader or writer, including WOLF15 integration;
- file, shell, test-runner, Git, or GitHub execution adapter;
- persistence, checkpoint store, Supabase, durable approval/resume, or long-term memory;
- optimizer or maintenance agent;
- dashboard or Owner Console;
- Docker integration, deployment, or production operation.

All PR-2 role output is deterministic, in-memory stub data. `READY_WITH_CONDITIONS` is not `READY_FOR_PRODUCTION` and grants no operational authority.

## Evidence policy

A capability moves from target to current only when all applicable evidence exists:

1. implementation is present in the repository;
2. its public contract is documented;
3. focused tests exercise its important behavior;
4. the documented verification command passes in the current checkout;
5. external services are described as integrated only when authenticated runtime evidence exists.

Code presence alone does not prove a service is deployed, a remote CI job has run, an external integration works, or a production action is safe.

## Current authority boundary

The current runtime requires the caller to supply `READ_ONLY` and has no
external repository adapter, so it does not read the repository named in a
task. It grants no file, shell, Git, GitHub, deployment, production-data, or
other external-system authority.

The normative target authority model is defined in [Authority Model](../governance/authority-model.md) and [ADR-004](../adr/ADR-004-human-controlled-production.md).

## Next intelligence milestone

PR-1 established:

```text
validated task request
        -> project-mode classification
        -> deterministic state transition
        -> typed response and trace
        -> automated verification
```

PR-2 adds the deterministic graph, bounded revision behavior, and stub roles while keeping model and repository-execution variability out of the loop. After PR-2 verification closes, the next milestone may introduce schema-constrained model adapters. The current system must not be described as a complete autonomous engineering OS.
