# Shared contracts

## Ownership and interfaces

CURRENT: Pydantic schemas define accepted input, typed output, field bounds
and structural invariants. `models.py` owns foundational task/workflow types;
`task.py` re-exports foundation types; `execution.py` owns correlated
execution events. `evidence.py`, `reasoning.py` and `cognition.py` define the
M2, M3-A and SCRS boundaries. `learning.py` defines episode/candidate and
advisory-generation data only.

Consumers import concrete types or the intentional exports in `__init__.py`.
Reasoning and cognition types are available in their own modules. A schema is
not an executor, persistence store, policy admission decision or factual proof.

## Authority and dependency direction

Runtime subsystems depend on these types. Contracts must not import provider,
workflow, storage or UI implementations. `Authority` currently admits only
`READ_ONLY`; reasoning fixes execution authorization false and SCRS fixes
advisory/no-modulation effects. A proposed extra field cannot confer permission.
Missing evidence, unmeasured telemetry and rejected inputs remain distinguishable.

## Verification and evolution

Tests in [tests](../../../tests/README.md) exercise schema rejection,
correlation, required candidate evaluation/approval references, authority denial,
finite numbers and lifecycle binding. Reference presence does not authenticate
an approval; no candidate activation consumer exists. Changes to defaults, enums, required fields or serialization require
consumer and compatibility review. No alias or synthesized historical
provenance may silently bridge a breaking contract change. New target schemas
arrive with the subsystem that owns them.

[Canonical ownership](../../../docs/architecture/canonical-ownership.md)
decides global ownership; this README describes the local contract.
