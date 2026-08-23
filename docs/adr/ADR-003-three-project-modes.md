# ADR-003: Three Project Modes

- **Status:** Accepted
- **Date:** 2026-08-24
- **Implementation status:** Target contract; router foundation is an early milestone

## Context

Greenfield design, work on an existing repository, and significant evolution of an existing system need different evidence and deliverables. A large set of overlapping modes would make routing and acceptance criteria unstable.

## Decision

The top-level router returns exactly one of three modes:

1. `GREENFIELD_SYSTEM_MODE` — no existing repository is the work source; the objective is a new system.
2. `EXISTING_REPO_MODE` — an existing repository is the source of truth and the primary objective is inspection, repair, or incremental improvement.
3. `HYBRID_EVOLUTION_MODE` — an existing repository is an input and the objective explicitly includes major evolution, successor architecture, or migration.

Subtypes such as audit, bug fix, security review, or MVP design may refine planning, but they do not become additional top-level modes.

Mode is independent of authority. For example, `HYBRID_EVOLUTION_MODE` with `READ_ONLY` authority may produce analysis and a migration plan but cannot change the repository.

## Routing inputs

The router uses validated facts, including:

- whether a repository reference was supplied and resolved;
- the declared objective;
- an explicit evolution or migration intent;
- any owner-selected override permitted by policy.

Repository presence without evolution intent defaults to `EXISTING_REPO_MODE`. No repository defaults to `GREENFIELD_SYSTEM_MODE`. Hybrid mode requires both a repository and explicit evolution intent.

## Consequences

### Positive

- routing behavior remains small, explainable, and testable;
- each mode can have clear evidence requirements;
- adding specialist roles does not multiply top-level modes.

### Costs

- ambiguous prompts sometimes require owner clarification;
- specialized workflows need secondary metadata or planning rules.

## Guardrails

- The router returns a reason with the selected mode.
- It does not infer that a named repository is accessible.
- It does not infer write or production authority from the mode.
- An explicit override is recorded in the trace.

## Alternatives rejected

- **One universal mode:** obscures important differences in source-of-truth and deliverables.
- **A mode per agent specialty:** couples routing to organization structure and becomes difficult to govern.
- **Implicit hybrid classification from repository presence:** misclassifies ordinary audits and fixes.

## Verification

At minimum, tests cover no-repository greenfield selection, repository existing-mode selection, repository plus explicit evolution intent, invalid references, ambiguous intent, and authority invariance.
