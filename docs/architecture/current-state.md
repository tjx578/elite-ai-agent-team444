# Current State

## Purpose

This document records what is demonstrably present in the repository. It is not a description of the eventual WOLF15 Sentient product.

## Canonical baseline

The canonical repository is
[`tjx578/wolf15-sentient`](https://github.com/tjx578/wolf15-sentient).
PR #1–#7 are merged. The M1-B architecture-freeze baseline is `main` commit
`7ffac9a8254688649ecf8bca57e2ae7757bd9f32`, not a moving claim about
later commits. Its [CI run](https://github.com/tjx578/wolf15-sentient/actions/runs/36374583942)
installed the project, passed 56 tests, and passed the installed product
identity/entrypoint check on Python 3.11, 3.12, and 3.13. Earlier checkpoints
remain separate: PR #1–#4 consolidated at `64ae79f`, and the original migration
snapshot passed 27 source and 27 installed-package tests. Its
[verification record](../verification/sentient-identity-20260928.md) remains
bound to that earlier source.

The migration began over PR-2 commit `df43c93e12b2ff68ce4fe1c2d3778a6052886413`.
The distribution and `/health` service name are
`wolf15-sentient`; the package and ASGI entrypoint are `wolf15_sentient` and
`wolf15_sentient.main:app`. Package folders `api`, `contracts`, `agents`, and
`orchestration` retain their existing responsibilities. See
[ADR-005](../adr/ADR-005-product-identity.md) and the
[migration guide](../migrations/sentient-identity.md).

The PR-1 and PR-2 records below describe historical baselines, including the
former namespace and historical verification. The separate model-adapter and
offline REE work is not part of M1-B `main`. M1-B documents target architecture;
it does not add model reasoning, repository execution, persistent memory,
trading integration, or authority. The proposed six divisions and 28
specialists remain a target; three deterministic stub roles are implemented.

## M1-C production trust foundation: complete

At the M1-B `main` checkpoint, GitHub reported `protected: false` for `main`
and no effective branch rules. The tracked tree did not contain `CODEOWNERS`,
`SECURITY.md`, a dependency lockfile, or separate lint, type-check, build,
dependency-audit, and secret-scan CI jobs. CI at that checkpoint ran package
installation, pytest, and the installed identity/entrypoint check only.

PR #7 merged M1-C at `main` commit
`e14a96919dbd50350c4877393c40a069570d906c`. Its
[CI run](https://github.com/tjx578/wolf15-sentient/actions/runs/36379162914)
installed locked dependencies, passed 57 tests on each of Python 3.11, 3.12,
and 3.13, and passed Ruff, Pyright, sdist/wheel build, isolated installed-package
smoke, dependency audit, and secret scan. The separate
[CodeQL run](https://github.com/tjx578/wolf15-sentient/actions/runs/36379162867)
passed Actions and Python analysis. GitHub reported `protected: true` for
`main`; the [active M1-C ruleset](https://github.com/tjx578/wolf15-sentient/rules/24097366)
requires a PR and ten named checks, blocks force-push and deletion, dismisses
stale approvals, and requires review conversations to be resolved. The ruleset
has no bypass actors. `CODEOWNERS`, `SECURITY.md`, `uv.lock`, weekly Dependabot
configuration, and private vulnerability reporting are present or enabled.
The CodeQL workflow in this tree pins both action steps to verified
`v4.38.2` commit `2892aa5e19bbd11bc0cff5427e3b750a04d9e3c2`; the cited
`e14a969` run used the then-current mutable `v4` tag. Dependency locking
covers Python packages in `uv.lock`, while the installed-package check proves
an install and smoke test, not byte-for-byte reproducible wheel artifacts.
The owner deferred selection of an open-source license; the public repository
has no license grant. These are source- and GitHub-bound receipts for this
checkpoint, not a claim about later commits. Production deployment and Railway
changes are **NOT_EXECUTED**; no capability or REE is activated.

## M2 evidence and context read path: merged checkpoint

[PR #11](https://github.com/tjx578/wolf15-sentient/pull/11) merged the initial
M2 read path at `main` commit
`8cfabf70b2927c7eaf73ae8983df4f9ca7c069fb`. The pure
`wolf15_sentient.evidence.assemble_context` function consumes caller-supplied
UTF-8 source content, `SourceRef` metadata, claims, and an explicit policy. It
checks SHA-256 digests, scope, revision, and freshness; preserves conflicts and
missing evidence; and returns a structured `BLOCKED` result when no source is
usable. A matching ID and digest never promote a source assertion to fact:
caller-submitted `VERIFIED` claims are downgraded to `SOURCE_CLAIM` unless an
independent validation path exists. See the
[M2 contract and limits](m2-evidence-context-runtime.md).

The [CI run on the merge commit](https://github.com/tjx578/wolf15-sentient/actions/runs/36386405999)
completed successfully: 74 tests passed on each of Python 3.11, 3.12, and
3.13; Ruff, Pyright, sdist/wheel build and isolated install, dependency audit,
and secret scan also passed. The separate
[CodeQL run](https://github.com/tjx578/wolf15-sentient/actions/runs/36386405976)
completed Actions and Python analysis successfully on the same SHA. These are
source and CI receipts, not deployment or production-runtime evidence.

The evaluator does not dereference locators, read repositories, call external
providers, write memory, or connect to the active LangGraph workflow. It does
not infer semantic conflicts from arbitrary prose. `READY` describes context
assembly only, not factual or production readiness. The M1-B and M1-C
checkpoints above remain historical records of their own revisions.

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

- Integrated PR-2 head `aa596cb` on 2026-09-28: **PASS_LOCAL** — 47 tests,
  Ruff check, and Python compilation. Push and pull-request CI passed on
  Python 3.11–3.13, with 47 tests per job.
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

## Next trust and intelligence milestones

PR-1 established:

```text
validated task request
        -> project-mode classification
        -> deterministic state transition
        -> typed response and trace
        -> automated verification
```

PR-2 added the deterministic graph, bounded revision behavior, and stub roles
while keeping model and repository-execution variability out of the loop. M1-C
established repository trust gates without a production claim. The initial M2
evidence/context read path is now merged as the pure helper documented above.
M3 model reasoning and M4 read-only repository intelligence remain separate
future increments with their own acceptance evidence. The current system must
not be described as a complete autonomous engineering OS.
