# Learning & Capability Adaptation Plane

## Status

Target architecture derived from the WOLF15 Neuro Network research corpus and
adapted to WOLF15 Sentient. **Master checkpoint owner: CP8.** This document is
not a roadmap and does not activate learning, persistence, repository
execution, model training, or external mutation.

## Architectural decision

WOLF15 Sentient uses two planes with one authority chain:

- Control Kernel / Task Runtime owns task state, transitions, authority, gates, termination, and any permitted execution boundary.
- Learning & Adaptation Plane observes evidence-backed outcomes and produces evaluated candidates. It cannot raise authority or mutate an active task.

The research five-node loop is remapped as follows:

| Research node | WOLF15 Sentient component | Responsibility |
| --- | --- | --- |
| WOLF15 Alpha facts | Task/Evidence Runtime | Emit typed, source-bound observations and receipts |
| Learning Journal | Experience Journal | Append/supersede episodes, dedupe, quarantine, and preserve lineage |
| Domain Knowledge | Knowledge Generations | Versioned/as-of knowledge with provenance |
| Learning Orchestrator | Learning Orchestrator | Select frozen evidence sets, reflect deterministically where required, schedule evaluation |
| Adaptive Memory | Adaptive Memory | Append-only candidate, evaluation, routing profile, and lesson registry |

## Memory model

Memory is not one shared mutable brain.

| Memory class | Contents | Mutation model |
| --- | --- | --- |
| Working | Bounded task-local typed state and artifact references | Ephemeral/reconstructable |
| Episodic | Task episodes, failures, outcomes, corrections | Append/supersede |
| Semantic | Curated knowledge generations and derived indexes | Versioned generation |
| Procedural | Candidate skills, workflows, routing profiles, lessons | Versioned lifecycle |
| Audit | Approval, rejection, revocation, replay and evaluation receipts | Append-only |

Private chain-of-thought is not canonical memory. Store structured decisions, evidence references, state transitions, failure classes, and compact rationales.

## Evidence spine

The target evidence path is:

SourceRef -> ContextBundle -> GroundedClaim -> EvidenceBackedResult -> Episode -> Candidate -> Evaluation -> Promotion decision.

Every material claim carries evidence status and claim type. Missing or conflicting evidence remains explicit; it is never converted to zero or PASS.

## Candidate lifecycle

Candidate adaptation is append-only and versioned:

DRAFT -> REJECTED or OFFLINE_EVALUATED -> SHADOW -> APPROVAL_PENDING -> ACTIVE_WORKFLOW -> DISABLED or SUPERSEDED.

Activation is a separate authority event. A candidate producer cannot approve itself.

## Capability donors

Repository discovery is inventory, not authority. Donor order does not determine priority.

A donor is decomposed into canonical capabilities and compared against the registry as NEW, EQUIVALENT, PARTIAL_OVERLAP, SUPERSET, SUBSET, COMPLEMENTARY, or CONFLICTING. Multiple providers may coexist for one canonical capability.

Provider selection is task-scoped and can distinguish default, fast, deep, offline, or low-resource profiles. Active provider sets are pinned per run so a task cannot change implementation mid-flight.

## Routing and aggregation

Legacy routing patterns may be reused only for non-authoritative work such as read-only retrieval, analysis fan-out, evaluation, or capability discovery. Availability alone cannot select an authority-bearing executor.

Aggregation must preserve dissent and source identity. Weighted or consensus aggregation cannot average away a hard failure, policy veto, provenance conflict, or missing evidence.

## Async delivery and durability

When persistence is introduced, use an outbox/inbox pattern with idempotent consumers and durable acknowledgement. Cache or pub/sub infrastructure can optimize delivery but is not canonical truth.

Required semantics:

- at-least-once delivery tolerated by idempotency;
- duplicate same ID/digest is a no-op;
- same ID/different digest is quarantined;
- corrections are new superseding records;
- out-of-order gaps stay incomplete rather than being fabricated;
- optional learning outage returns the task system to baseline behavior.

## Offline optimizer boundary

A2Flow/MCTS-style optimization is limited to candidates such as task grouping, preprocessing order, retrieval strategy, worker scheduling, retry/backoff, batch size, evaluator sequence, or resource allocation.

It cannot change authority, bypass gates, silently rewrite evidence, approve its own candidate, or mutate external systems.

## Quality model

No scalar score can convert a failed or unmeasured hard gate into PASS.

Hard gates include contract validity, provenance, authority, security, deterministic replay where required, regression, and approval. Soft metrics may include latency, cost, resource use, coverage, and quality measurements with explicit definitions.

## Failure behavior

- Integrity, provenance, schema, or authority ambiguity: fail closed for the affected artifact.
- Optional learning/advisory unavailable or stale: baseline task path continues without that context.
- Conflicting sources: preserve conflict and precedence metadata.
- Candidate regression: reject or retain previous provider as fallback.
- Registry update during a task: existing run remains pinned to its original registry generation.

## Runtime boundary for this slice

This integration adds only contracts and documentation. It does not wire the learning plane into LangGraph, does not persist episodes, does not create a background worker, and does not activate adaptive routing.
