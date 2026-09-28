# Deterministic specialist stubs

## Ownership and interfaces

CURRENT: `stubs.py` implements `ArchitectStub`, `EngineerStub` and
`ReviewerStub`. They consume typed task/project/report inputs and return
`ArchitectureReport`, `ImplementationPlan` or `ReviewDecision`. Reviewer
scripts support deterministic approve/revise/block paths for offline tests.

## Dependencies and authority

These roles depend on [contracts](../contracts/README.md); the
[Control Kernel](../orchestration/README.md) calls them and owns the resulting
gate and transition decisions. Stub output is deterministic in-memory data.
It does not prove implemented code, executed tests, real model reasoning or
repository access. Roles cannot grant authority, bypass revision caps, mutate
workflow state, write files or deploy.

## Verification and target

[Workflow tests](../../../tests/unit/test_workflow_invariants.py) exercise role
validation, scripted reviews and bounded loops. Changes must review local input/
output ownership and Kernel consumers. The six-division/28-specialist roster
and eventual `elite_team/` package remain target organization. Migration and
real specialist behavior require separate typed contracts and acceptance;
adding a role name never activates a capability.

[Canonical ownership](../../../docs/architecture/canonical-ownership.md)
decides global ownership; this README describes the local contract.
