# Offline reasoning boundary

## Ownership and interfaces

CURRENT M3-A: `select_task_route`, `prepare_reasoning`, and `run_reasoning`
in `runtime.py` map `ReasoningRequest` to controller-owned `ReasoningInput`
and `ReasoningResult`. Four task kinds are supported; only engineering selects
an Existing/Greenfield/Hybrid project mode. The default `StubReasoningAdapter`
is labelled as a stub. `OfflineReasoningAdapter` accepts trusted local code.

## Evidence, dependencies and authority

The bridge recomputes [M2 evidence](../evidence/README.md), supplies usable
content, retains missing/conflicting evidence and binds the complete input by
digest. The adapter receives a detached input. Proposals must echo the digest
and reference usable source IDs. `PROPOSAL_VALIDATED` proves contract/binding/
reference checks only; prose remains untrusted. `execution_authorized=false`.

This library depends on contracts, evidence and the existing engineering mode
selector. It is not connected to `/tasks` or the active graph. It has no real
provider, repository reader, tool, retry, persistent memory or REE. An injected
Python adapter is not isolated by this protocol. Byte limits and caught timeout
exceptions do not enforce a transport deadline or establish factual accuracy.

## Verification and next boundary

[Reasoning tests](../../../tests/unit/test_reasoning.py) cover evidence,
mutation, digest/reference rejection, adapter failures and authority injection.
[M3-A details](../../../docs/architecture/m3a-reasoning-contracts.md) describe
the narrow English/Indonesian routing limits. CP1/M3-B must prove one provider,
cancellation and budgets behind these contracts. It must resolve gateway
ownership before adding parallel target paths. Contract/route changes require
README impact review and SCRS consumer review.

[Canonical ownership](../../../docs/architecture/canonical-ownership.md)
decides global ownership; this README describes the local contract.
