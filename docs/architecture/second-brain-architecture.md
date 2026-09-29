# Second Brain: evidence, knowledge, and memory

## Status and ownership

**Target design. Master ownership spans CP2, CP3 and CP4 without defining a
separate roadmap.** The repository currently defines `SourceRef`,
`GroundedClaim`, `ContextBundle`, `LearningEpisode`, and related contracts in
`src/wolf15_sentient/contracts/`. It has no source resolver, durable journal,
knowledge index, or personal-data store. The Control Kernel owns task state;
the Second Brain supplies context and receives verified outcome records.
It cannot edit a running task or grant authority.

## Evidence path

```text
scoped source request
  -> resolver with source-specific access control
  -> immutable source revision and observation receipt
  -> SourceRef[]
  -> freshness, conflict, and completeness checks
  -> ContextBundle + GroundedClaim[]
  -> answer with claim-level evidence and unknowns
  -> verified outcome -> optional episode/journal
```

`VERIFIED` requires more than a reference existing in a bundle: the later
resolver/evaluator must prove that the cited bytes and revision support the
claim. A document's assertion is `SOURCE_CLAIM` until independently checked.
`NOT_MEASURED` stays unknown and cannot be converted to zero or PASS. Conflicts
are retained with both source identities and a documented precedence rule.
The current contracts validate shape and internal references; they do not
perform source resolution or semantic verification.

## Memory classes

| Class | Intended contents | Lifecycle boundary |
| --- | --- | --- |
| Working | Bounded task-local context | Ephemeral; reconstructable from allowed sources |
| Episodic | Observed task outcomes and corrections | Append/supersede with lineage |
| Semantic | Curated source-bound knowledge | Versioned generations and as-of reads |
| Procedural | Evaluated skill/profile candidates | Separate lifecycle and approval |
| Audit | Decisions, denials, revocations, receipts | Append-only under policy |

These are information classes, not a requirement for five databases. Raw
private chain-of-thought is not canonical memory. The target stores concise
decisions, source references, outcome evidence, and failure classes without
secrets or unnecessary personal content. Retention and deletion policies
must be decided before any durable store is introduced.

## Consistency and failure rules

- Each source carries a stable ID, kind, locator under access control,
  revision, digest, observation time, and scope. Hashes bind content; they do
  not make an untrusted author trustworthy.
- Duplicate ID with the same digest is idempotent. Duplicate ID with a
  different digest is quarantined. Corrections create superseding records;
  a cache is not the canonical record.
- A missing revision, stale source, unresolved reference, access denial, or
  provenance conflict keeps the affected claim unverified. The assistant may
  still answer the supported part with an explicit gap.
- If optional memory is unavailable, the Kernel can continue a permitted
  baseline path without pretending that memory was consulted.

CP2 establishes the source/evidence read path: read-only resolver, context
assembler, fixed freshness/conflict policy, and tests showing unsupported
claims cannot be promoted. CP3 adds durability/observability; CP4 adds
owner-scoped personal/media retrieval. These are responsibilities inside the
Master Roadmap, not new Second Brain checkpoints. The [learning plane](learning-capability-adaptation.md) consumes
verified episodes later; it is not an alternate source of task authority.
