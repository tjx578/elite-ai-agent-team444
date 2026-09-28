# Deterministic Control Kernel

## Ownership and interfaces

CURRENT: `workflow.py` owns the in-memory LangGraph graph, gate decisions,
bounded revision loops and termination. `run_workflow(TaskRequest)` returns a
typed `WorkflowResult`; `WorkflowDependencies` supplies trusted role stubs.
`transitions.py` validates legal transitions/required state; `state.py` builds
foundation state; `mode_router.py` selects the three engineering project modes.

The graph proceeds through intake, routing, state creation, architect,
architecture review, engineer, validation, reviewer and finalization. Each
architecture/engineering revision loop allows at most two revisions. The Kernel
owns state and authority; neither a role report nor a metric can own them.

## Dependencies and limits

Depends on [contracts](../contracts/README.md) and [agents](../agents/README.md);
[API](../api/README.md) calls it. Default roles are deterministic stubs.
There is no model, repository reader, tool executor, persistent checkpoint or
learning integration. `READY_WITH_CONDITIONS` assesses stub workflow completion
and grants no operational permission. Trusted dependency injection is a local
test seam, not a sandbox for arbitrary code.

## Verification and target

[Workflow invariant tests](../../../tests/unit/test_workflow_invariants.py)
cover transition failures, invalid outputs, correlation, revision caps and
authority limits; integration tests exercise the HTTP path. Responsibility
changes require review of this README, role contracts, transitions and tests.
The target separates `control/` policy/lifecycle from `orchestration/`
composition through one authority chain. That migration is not performed here.

[Canonical ownership](../../../docs/architecture/canonical-ownership.md)
decides global ownership; this README describes the local contract.
