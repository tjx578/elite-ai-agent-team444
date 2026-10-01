# M2 evidence and context runtime

**Historical implementation label.** This M2 name identifies a CP0 foundation
slice only; it is not a current checkpoint. External repository/source
resolution belongs to CP2 in the [Master Roadmap](roadmap.md).

`wolf15_sentient.evidence.assemble_context` is a pure, read-only evaluator. The
caller supplies source text, `SourceRef` metadata, claims, and an explicit
`EvidencePolicy`. The function does not open `SourceRef.locator`, read a file,
make a network request, write memory, or connect to the active workflow.

## Input and replay

`EvidenceContextInput` carries stable bundle, task, and run IDs. Its policy
specifies version `m2-v0`, task scope, required revision, evaluation time, and
maximum source age in seconds. Supplying the same input, including policy and
evaluation time, produces the same serialized result. The result carries the
full policy, its version, assessments, and any assembled `ContextBundle`.

Each `SuppliedSource` is UTF-8 text provided by the caller. The evaluator
compares its SHA-256 digest with its matching `SourceRef`, enforces a 1,000,000
byte limit per source, and checks scope, revision, and freshness. Invalid UTF-8,
missing content, conflicting duplicate IDs, digest mismatches, stale or future
observations, and scope or revision mismatches make that source unusable. Two
references for the same kind, locator, scope, and revision with different
digests are both quarantined as a provenance conflict.

If no usable source remains, `EvidenceContextResult.status` is `BLOCKED` and
`bundle` is `null`. The evaluator does not manufacture a source to satisfy
`ContextBundle.source_refs`' one-source minimum. When some sources are usable,
the bundle retains them and lists missing or rejected evidence. A declared
source disagreement remains in both the typed conflict list and the bundle;
the evaluator assigns no precedence. It does not infer semantic disagreement
from arbitrary natural-language text.

## Claim boundary

A referenced source must be usable, and the exact claim text must occur in
each referenced source. This proves only that the source contains that text.
Even a caller-submitted `VERIFIED` claim is downgraded to `SOURCE_CLAIM` until
independent validation exists. Unknown references, unusable sources, absent
literal support, duplicate claim IDs, and unevaluated derivations are rejected
with explicit issues. `NOT_MEASURED` remains `UNKNOWN` and is never treated as
zero or a pass.

`READY` means this context assembly had no detected gaps or conflicts; it is
not a production-readiness verdict and does not certify source assertions as
facts. `PARTIAL` preserves usable context alongside gaps or conflicts. The
output authority is always `READ_ONLY`. Source text is data, including text
that resembles instructions or file paths.

The synthetic acceptance tests are in `tests/unit/test_evidence_runtime.py`.
Model reasoning, repository acquisition, LangGraph wiring, persistent memory,
REE activation, and workflow authority are outside this change.
