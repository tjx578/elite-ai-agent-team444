# ELITE AI AGENT TEAM OS

> An independent, human-governed control plane for auditable AI-assisted software-engineering workflows.

![Status](https://img.shields.io/badge/status-PR--2%20deterministic%20kernel-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-green)
![License](https://img.shields.io/badge/license-private-lightgrey)

## Status at a glance

This repository is being built as small, verifiable vertical slices. The original multi-agent vision remains the target, but it is not presented as working software.

## CURRENT IMPLEMENTATION

The repository contains the PR-1 foundation plus the source implementation of the **PR-2 Deterministic Orchestration Kernel**.

PR-1 remains the verified foundation baseline:

- an installable Python 3.11+ package using FastAPI and Pydantic;
- `GET /health` and `POST /tasks`;
- strict task, state, response, authority, and execution-trace contracts;
- conservative routing across the three project modes;
- creation of correlated task, run, and trace identifiers;
- a deterministic three-step foundation trace: `INTAKE`, `MODE_ROUTER`, `STATE_CREATION`;
- read-only authority as the only accepted authority value;
- architecture ADRs and the least-privilege authority model;
- a read-only GitHub Actions test workflow definition; the observed remote foundation job was `NOT_EXECUTED` because a GitHub billing lock left it with zero steps and `runner_id=0`;
- ten local API/contract tests, verified passing in this checkout on 2026-08-24.

PR-2 source adds:

- a LangGraph `1.2.10` `StateGraph` as a code-controlled workflow controller;
- typed, side-effect-free `ArchitectStub`, `EngineerStub`, and `ReviewerStub` roles;
- strict architecture, implementation, validation, review, gate, workflow-result, and execution-event contracts;
- explicit transition allow-lists and required-state checks;
- architecture and engineering review loops capped at two revisions each;
- correlated, immutable execution events for every attempted workflow node, including revision count, decision, and sanitized error fields;
- fail-closed paths for invalid typed role output, validation failure, direct owner blocks, and revision-limit exhaustion;
- terminal decision contracts for `READY_WITH_CONDITIONS`, `NOT_READY`, and `BLOCKED_REQUIRES_OWNER`.

The default deterministic happy path is entirely in memory. It produces typed architecture and implementation artifacts, deterministic validation/review evidence, and `READY_WITH_CONDITIONS`. That status is an assessment only; it grants no repository or production authority.

**PR-2 verification status:** a fresh local environment passed 25 tests in 3.12 seconds; Ruff, graph compile/render, and happy-path, revision, and exhaustion smoke checks passed. The initial PR-2 push and pull-request workflow runs were both **NOT_EXECUTED**: all six Python 3.11-3.13 jobs had zero steps and `runner_id=0`, with GitHub reporting that the account was locked because of billing. Security review remains pending. The PR-1 result must not be reused as PR-2 evidence.

See [Current State](docs/architecture/current-state.md) for the exact evidence boundary.

### Hard boundary: not implemented

- OpenAI, Codex, or any other model-backed reasoning;
- repository reading or mutation, including WOLF15 integration;
- file, shell, test-runner, Git, or GitHub execution adapters;
- persistence, checkpoints, Supabase, durable approval/resume, or long-term memory;
- optimizer or maintenance agents;
- an Owner Console or dashboard;
- Docker, deployment, or production operations.

The role classes are deterministic stubs, not AI agents. A repository string remains classification input only and is never opened. Technology names in the target architecture are planned choices unless explicitly listed above as current.

## Run the current kernel

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m uvicorn elite_team.main:app --reload
```

Check service identity:

```bash
curl http://127.0.0.1:8000/health
```

Submit a read-only task:

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"intent":"Audit this repository","repository":"https://example.invalid/owner/project","authority":"READ_ONLY"}'
```

`POST /tasks` runs the in-memory PR-2 graph and returns the typed terminal artifacts and full execution trace. The repository value is classification input only; the service does not fetch or inspect it. Interactive API documentation is available at `http://127.0.0.1:8000/docs` while the local service is running.

## TARGET ARCHITECTURE

```text
Owner
  |
  v
Owner Console / API
  |
  v
Independent Elite Control Plane
  +-- typed intake and authority policy
  +-- project-mode router
  +-- deterministic orchestrator
  +-- bounded gates and revision loops
  +-- trace and decision ledger
  |
  +------ typed contracts -------+
  |                               |
  v                               v
Reasoning roles             Execution adapters
Architect                   Repository / Files
Reviewer                    Tests / Shell
Engineer                    Git / GitHub
Security / Performance      Deployment (separate approval)
  |                               |
  +------------- evidence --------+
                 |
                 v
          Human decision boundary
```

The orchestrator controls state and transitions deterministically. Model-backed roles produce schema-constrained proposals; they do not control the workflow or grant themselves tools. Target repositories remain external systems reached through constrained adapters.

Read the complete [Target Architecture](docs/architecture/target-architecture.md) and [Execution Flow](docs/architecture/execution-flow.md).

## Project modes

The top-level router returns exactly one mode:

| Mode | Use when | Source of truth |
| --- | --- | --- |
| `GREENFIELD_SYSTEM_MODE` | Designing a new system without an existing repository | Validated owner requirements |
| `EXISTING_REPO_MODE` | Auditing, repairing, or incrementally improving an existing repository | Repository evidence plus owner objective |
| `HYBRID_EVOLUTION_MODE` | Evolving an existing repository into a materially new architecture or successor | Current repository, explicit evolution intent, and migration constraints |

Mode controls planning, not authority. Supplying a repository does not imply write access; selecting hybrid mode does not permit changes.

## CURRENT DETERMINISTIC KERNEL

```text
INTAKE
  -> MODE_ROUTER
  -> STATE_CREATION
  -> ARCHITECT
  -> ARCHITECTURE_REVIEW
  -> ENGINEER
  -> VALIDATION
  -> REVIEWER
  -> FINALIZE
```

`ARCHITECTURE_REVIEW` may loop back to `ARCHITECT`; `REVIEWER` may loop back to `ENGINEER`. Each loop permits at most two revisions. Gate outcomes are `APPROVED`, `REVISION_REQUIRED`, or `BLOCKED_REQUIRES_OWNER`. Typed output failures and exhausted limits terminate through `FINALIZE` with `BLOCKED_REQUIRES_OWNER`.

## Authority and production safety

The default is non-mutating. Intended authority progresses only through explicit, scoped grants:

```text
analysis only
  -> read-only
  -> proposed patch
  -> isolated worktree
  -> feature branch and tests
  -> draft pull request
  -> human approval
  -> separately controlled production action
```

There is no direct push to a protected/default branch, autonomous merge, or production mutation. Credentials, project mode, model output, and a readiness label are not authority. See the normative [Authority Model](docs/governance/authority-model.md).

## Delivery roadmap

| Increment | Scope | Evidence required before claiming completion |
| --- | --- | --- |
| **PR-0** | Truth alignment, architecture contracts, ADRs, authority model | Documentation matches repository state |
| **PR-1** | Python/API/contracts/router/state/trace foundation | Focused tests pass; endpoints and schemas are runnable |
| **PR-2** | Deterministic graph, bounded revision loop, stub roles | Workflow integration tests pass without model variability |
| **PR-3** | Schema-constrained model adapters | Contract, failure, and evaluation evidence |
| **PR-4** | Read-only and isolated repository adapters | Policy tests and sandbox evidence; no default-branch authority |
| **PR-5** | Feature branch and draft PR delivery | Git/GitHub integration evidence and human merge boundary |
| **PR-6** | Persistence, approval, and resume | Idempotency and replay-resistant approval tests |
| **PR-7** | Owner Console | UI consumes stable contracts without bypassing policy |
| **PR-8+** | Additional roles, memory, optimization | Capability-specific security, quality, and performance evidence |

PR-1 establishes the local slice of **M0 — Executable Foundation**: a validated task enters, its mode is classified, deterministic state and trace are produced, and local automated tests pass. Full M0 promotion still requires a verified remote CI run. M0 is not the same as a complete agent OS.

## Target specialist organization

Specialists are introduced only when the workflow and evidence justify them:

- **Architect:** system boundaries, data/API contracts, migration, and trade-offs;
- **Engineer:** implementation plans and isolated changes;
- **Reviewer:** architecture/code correctness, regression, and gate decisions;
- **Security:** threat analysis and security evidence;
- **Performance:** bottlenecks, benchmarks, and scale evidence;
- **Operations:** deployment design, observability, rollback, and incident readiness.

The planned organization may grow beyond these roles. Role count is not a maturity metric; verified end-to-end behavior is.

## Documentation

- [Current State](docs/architecture/current-state.md)
- [Target Architecture](docs/architecture/target-architecture.md)
- [Execution Flow](docs/architecture/execution-flow.md)
- [ADR-001: Independent Control Plane](docs/adr/ADR-001-independent-control-plane.md)
- [ADR-002: Deterministic Orchestrator](docs/adr/ADR-002-deterministic-orchestrator.md)
- [ADR-003: Three Project Modes](docs/adr/ADR-003-three-project-modes.md)
- [ADR-004: Human-Controlled Production](docs/adr/ADR-004-human-controlled-production.md)
- [Authority Model](docs/governance/authority-model.md)

## Truth and verification policy

Claims in this repository follow separate evidence classes:

- source and configuration show what is present;
- local tests show what passed in the current checkout;
- remote CI shows what ran on the remote service;
- authenticated runtime evidence shows what is actually running;
- authenticated production evidence shows production state.

One class must not be substituted for another. Missing or inaccessible external evidence is `UNKNOWN` or `NOT_MEASURED`, not a pass, zero, or readiness claim.

## License

Private project unless otherwise specified.
