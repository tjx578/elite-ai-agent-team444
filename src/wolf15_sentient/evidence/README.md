# Evidence and context contract

## Ownership and interface

CURRENT: `assemble_context(EvidenceContextInput)` in `context.py` is a pure
M2 evaluator of caller-supplied UTF-8 content, source references, claims and
explicit policy. It returns `EvidenceContextResult`: context, source/claim
assessments, conflicts and missing evidence. It validates content digests,
scope, revision and freshness. Without usable sources, context is `BLOCKED`.

## Dependencies and boundaries

Depends on [evidence contracts](../contracts/evidence.py); the
[reasoning bridge](../reasoning/README.md) consumes it. Source locators are
identifiers and are never dereferenced here. This code does not fetch URLs,
read repositories, write memory or invoke providers. Claimed `VERIFIED` status
cannot become verified fact merely from a matching digest. Semantic truth and
arbitrary prose conflict detection are outside the current evaluator.

## Verification and target

[Evidence tests](../../../tests/unit/test_evidence_runtime.py) exercise digest,
revision, scope, freshness, duplicate/conflicting sources and unmeasured claims.
See [M2 limits](../../../docs/architecture/m2-evidence-context-runtime.md).
Evidence/status changes require review of this README and downstream reasoning
and cognition consumers. Future `context/` and `evidence/` separation preserves
one source-assessment owner; retrieval and durable Second Brain need separate
acceptance, not implicit I/O inside this pure helper.

[Canonical ownership](../../../docs/architecture/canonical-ownership.md)
decides global ownership; this README describes the local contract.
