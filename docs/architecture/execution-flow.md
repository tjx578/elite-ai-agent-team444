# Execution Flow

## Scope

**Roadmap authority:** this file describes the current/historical deterministic
flow only. Future checkpoint order comes exclusively from the
[Master Roadmap](roadmap.md).


PR-2 implements the deterministic, in-memory control flow through `FINALIZE`. It uses LangGraph `1.2.10` as a state-machine runtime; Python policy owns transitions, gates, revision limits, typed validation, and finalization. Model reasoning and all external execution remain out of scope.

## End-to-end flow

```text
1. INTAKE
   validate request, identity, repository reference, and requested authority
      |
2. MODE_ROUTER
   choose exactly one project mode
      |
3. STATE_CREATION
   initialize mode, correlation, trace, and revision counters
      |
4. ARCHITECT
   emit typed ArchitectureReport
      |
5. ARCHITECTURE_REVIEW
   APPROVED -------------------------------+
   REVISION_REQUIRED -> bounded revision --|-- back to ARCHITECT
   BLOCKED_REQUIRES_OWNER -----------------+--> STOP
      |
6. ENGINEER
   emit typed in-memory ImplementationPlan
      |
7. VALIDATION
   validate the typed plan without external execution
      |
8. REVIEWER
   APPROVED -------------------------------+
   REVISION_REQUIRED -> bounded revision --|-- back to ENGINEER
   BLOCKED_REQUIRES_OWNER -----------------+--> STOP
      |
9. FINALIZE
   emit typed terminal state and complete execution trace
```

Repository execution and a delivery gate remain target architecture for later increments.

## State ownership

The deterministic orchestrator is the only component allowed to mutate workflow state or choose a transition. Roles return typed proposals. Tools return typed results. Neither may directly call the next role, approve its own work, raise task authority, or emit a production-ready decision without required evidence.

Current graph state includes:

- `task_id`, `run_id`, and `trace_id`;
- validated request and effective authority;
- project mode and routing reason;
- terminal status and final decision;
- typed role outputs and gate decisions;
- revision counters;
- failure code/reason when applicable;
- typed in-memory artifact and evidence references.

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

It includes a gate name, reason, evidence references, blocking findings, and revision count. Architecture and engineering each have a maximum of two revisions. A third `REVISION_REQUIRED` decision is converted to `BLOCKED_REQUIRES_OWNER` with `REVISION_LIMIT_EXHAUSTED`.

## Final decision contract

Terminal outcomes are:

```text
READY_WITH_CONDITIONS
NOT_READY
BLOCKED_REQUIRES_OWNER
```

`READY_FOR_PRODUCTION` is intentionally absent from the current contract. The default approved stub path produces `READY_WITH_CONDITIONS`; blocked gates, invalid typed output, and exhausted revisions produce `BLOCKED_REQUIRES_OWNER`. `NOT_READY` is a typed terminal value, but its reachable policy path remains subject to final PR-2 verification.

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
