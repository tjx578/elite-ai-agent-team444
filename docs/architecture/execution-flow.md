# Execution Flow

## Scope

This is the target control flow. PR-1 currently implements only request validation, `INTAKE`, `MODE_ROUTER`, and `STATE_CREATION`, then returns `FOUNDATION_COMPLETE` with no final readiness decision. The remaining nodes below are target architecture. A milestone may implement only a prefix and must report that limitation explicitly.

## End-to-end flow

```text
1. INTAKE
   validate request, identity, repository reference, and requested authority
      |
2. AUTHORITY_CHECK
   reduce request to the effective least-privilege authority
      |
3. MODE_ROUTER
   choose exactly one project mode
      |
4. PLAN
   select applicable roles and gates without increasing authority
      |
5. ARCHITECT
   emit typed ArchitectureReport
      |
6. ARCHITECTURE_REVIEW
   APPROVED -------------------------------+
   REVISION_REQUIRED -> bounded revision --|-- back to ARCHITECT
   BLOCKED_REQUIRES_OWNER -----------------+--> STOP
      |
7. ENGINEER
   emit typed ImplementationPlan or isolated change set
      |
8. VALIDATION
   collect test, security, and performance evidence required by scope
      |
9. REVIEWER
   APPROVED -------------------------------+
   REVISION_REQUIRED -> bounded revision --|-- back to ENGINEER
   BLOCKED_REQUIRES_OWNER -----------------+--> STOP
      |
10. DELIVERY_GATE
    report only / patch / isolated worktree / draft PR, as authorized
      |
11. FINAL
    typed decision, evidence summary, limitations, and owner actions
```

## State ownership

The deterministic orchestrator is the only component allowed to mutate workflow state or choose a transition. Roles return typed proposals. Tools return typed results. Neither may directly call the next role, approve its own work, raise task authority, or emit a production-ready decision without required evidence.

Minimum state fields are expected to include:

- `task_id`, `run_id`, and `trace_id`;
- validated request and effective authority;
- project mode and routing reason;
- current node and terminal status;
- typed role outputs and gate decisions;
- revision counters;
- evidence and artifact references;
- errors, timestamps, and owner approval references.

## Project-mode branches

### `GREENFIELD_SYSTEM_MODE`

Selected when there is no existing repository to inspect and the objective is to design or build a new system. Missing repository context must not be fabricated.

### `EXISTING_REPO_MODE`

Selected when the primary objective is to inspect, explain, repair, or improve an existing repository without redefining it as a successor system.

### `HYBRID_EVOLUTION_MODE`

Selected when an existing repository is an input and the objective explicitly includes a next-generation design, significant architectural evolution, or migration. Repository presence alone is insufficient.

Ambiguous classification must be surfaced in the routing reason or stopped for owner clarification when the distinction changes the deliverable materially.

## Gate contract

A gate decision has one of these statuses:

```text
APPROVED
REVISION_REQUIRED
BLOCKED_REQUIRES_OWNER
```

It includes a gate name, reason, evidence references, blocking findings, and revision count. A revision loop has a configured finite maximum; the initial target is two revisions. Exceeding that maximum terminates with `BLOCKED_REQUIRES_OWNER`.

## Final decision contract

Terminal outcomes are:

```text
READY_FOR_PRODUCTION
READY_WITH_CONDITIONS
NOT_READY
BLOCKED_REQUIRES_OWNER
```

`READY_FOR_PRODUCTION` is unavailable unless all required runtime, test, security, operations, and deployment evidence has been collected for the exact artifact and environment. A local deterministic or stub workflow cannot produce that claim truthfully.

## Execution trace

Every attempted node produces an append-only event with, at minimum:

```text
task_id / run_id / trace_id
node
started_at / finished_at
status
input_reference / output_reference
decision and evidence references
error category (when applicable)
```

Trace data is evidence of what the controller attempted and observed. It does not itself prove that an external deployment, remote CI run, or production state is healthy.

## Fail-closed rules

Stop rather than continue when:

- request or role output fails schema validation;
- requested authority is absent, expired, or broader than policy allows;
- a target or path cannot be resolved safely;
- required gate evidence is unavailable;
- a revision or retry limit is exceeded;
- an adapter returns an unclassified error;
- a model requests a transition or tool outside its contract.
