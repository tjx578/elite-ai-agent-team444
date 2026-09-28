# WOLF15 Sentient

> An independent, human-governed control plane for auditable AI-assisted software-engineering workflows.

![Status](https://img.shields.io/badge/status-canonical%20main-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-green)
![License](https://img.shields.io/badge/license-no%20public%20grant-lightgrey)

## Status at a glance

**CP0 foundation:** SK-01 governance, M3-A offline reasoning contracts, and
SCRS advisory observability are integrated at
`main@a53388f60b34372c5c3f43a31d8a5157add54379`. Resulting-main
[CI](https://github.com/tjx578/wolf15-sentient/actions/runs/36465209386) and
[CodeQL](https://github.com/tjx578/wolf15-sentient/actions/runs/36465209366)
passed, with 198 tests per Python 3.11/3.12/3.13. CP0 closure still requires
architecture alignment and the final exact-main acceptance receipt. See the
[architecture index](docs/architecture/README.md),
[current-to-target ownership map](docs/architecture/canonical-ownership.md),
and [checkpoint roadmap](docs/architecture/roadmap.md). Real model/provider,
repository-reader, execution, capability/REE activation and deployment are
outside this integrated offline foundation.

The records below preserve earlier implementation milestones and their evidence.

The canonical GitHub repository is
[tjx578/wolf15-sentient](https://github.com/tjx578/wolf15-sentient). PR #1–#4
are merged; their consolidation baseline is `64ae79f`. The [CI run on that baseline](https://github.com/tjx578/wolf15-sentient/actions/runs/36372815613)
passed 56 tests and the installed identity check on Python 3.11, 3.12, and
3.13. The earlier [identity snapshot](docs/verification/sentient-identity-20260928.md)
and [integration record](docs/verification/sentient-identity-integration-20260928.md)
retain their own source and wheel bindings.
PR #5 aligned repository-name references, and PR #6 merged the M1-B
architecture freeze. The [CI run on M1-B `main`](https://github.com/tjx578/wolf15-sentient/actions/runs/36374583942)
passed 56 tests and installed identity checks on Python 3.11–3.13 at
`7ffac9a8254688649ecf8bca57e2ae7757bd9f32`.

PR #7 then merged the M1-C repository trust foundation at `main` commit
`e14a96919dbd50350c4877393c40a069570d906c`. Its
[CI](https://github.com/tjx578/wolf15-sentient/actions/runs/36379162914)
passed 57 tests on each tested Python version (3.11, 3.12, and 3.13), plus lint,
type, build/install, dependency-audit, and secret-scan gates; its
[CodeQL run](https://github.com/tjx578/wolf15-sentient/actions/runs/36379162867)
passed Actions and Python analysis. The
[main ruleset](https://github.com/tjx578/wolf15-sentient/rules/24097366)
is active. These receipts do not establish production deployment.

This repository is being built as small, verifiable vertical slices. The original multi-agent vision remains the target, but it is not presented as working software.

WOLF15 Sentient is the product identity. **Elite AI Agent Team OS** names its
planned organization of divisions and specialists. **WOLF15 Trading System**
remains an external system with its own strategy, risk, and execution authority.

The original identity migration started at PR-2 commit
`df43c93e12b2ff68ce4fe1c2d3778a6052886413`. Its Python distribution and health
service name are `wolf15-sentient`; its import namespace is `wolf15_sentient`.
Existing consumers must update imports, launch commands, and health identity
checks. The former namespace is not provided as an alias. The version remains
`0.1.0` for this unpublished migration.

The GitHub repository rename and PR consolidation are complete. PR-3 model
adapter work remains in its separate development checkout. See
[ADR-005: Product Identity and Namespace](docs/adr/ADR-005-product-identity.md)
and the [migration guide](docs/migrations/sentient-identity.md).

## M1-B architecture boundaries

The [reference architecture](docs/architecture/super-intelligence-reference-architecture.md)
maps the Control Kernel, Sentient Core, specialists, Personal Assistant,
Second Brain, Capability Fabric/Foundry, and learning/REE boundaries. The
[roadmap](docs/architecture/roadmap.md) orders the evidence gates for later
increments. These are target designs; the current runtime remains the
`READ_ONLY` deterministic kernel described below.

## CURRENT IMPLEMENTATION

The active HTTP workflow contains the PR-1 foundation and **PR-2 Deterministic
Orchestration Kernel**. Separate M2 evidence, M3-A reasoning and SCRS libraries
are integrated as described above; they are not wired into `/tasks`.

PR-1 remains the verified foundation baseline:

- an installable Python 3.11+ package using FastAPI and Pydantic;
- `GET /health` and `POST /tasks`;
- strict task, state, response, authority, and execution-trace contracts;
- conservative routing across the three project modes;
- creation of correlated task, run, and trace identifiers;
- a deterministic three-step foundation trace: `INTAKE`, `MODE_ROUTER`, `STATE_CREATION`;
- read-only authority as the only accepted authority value;
- architecture ADRs and the least-privilege authority model;
- a read-only GitHub Actions test workflow; the reviewed PR-1 head `cec55f5`
  passed 30 local tests and push/pull-request CI on Python 3.11–3.13;
- bounded request text, explicit `READ_ONLY`, and routing reasons in state,
  response, and trace.

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

**PR-2 verification:** the integrated source passed 47 local tests, Ruff check,
and Python compilation on 2026-09-28. Its original head passed 25 local tests,
graph compile/render, and workflow smoke checks. Codex Security diff scan
`5a286602-d315-49c9-bd7a-1fefe5ab7db5` covered that original scope and
found no reportable issue. The original CI jobs were `NOT_EXECUTED` during the
GitHub billing lock. The integrated PR-2 head `aa596cb` passed push and
pull-request CI on Python 3.11–3.13 with 47 tests per job. This does not
qualify the later identity-migration head.

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
python -m uvicorn wolf15_sentient.main:app --reload
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
WOLF15 Sentient Control Plane
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

- [ADR-005: Product Identity and Namespace](docs/adr/ADR-005-product-identity.md)
- [Identity migration guide](docs/migrations/sentient-identity.md)

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

This repository is publicly visible but has no open-source license. No public
reuse grant has been made. `CODEOWNERS` identifies review stewardship; it does
not establish copyright ownership. See [Security policy](SECURITY.md) for
private vulnerability reporting.
