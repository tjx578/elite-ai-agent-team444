# ADR-006 — Controlled Learning and Capability Adaptation Plane

## Status

PROPOSED

## Context

The private WOLF15 Neuro Network research corpus contains useful concepts for asynchronous learning, memory classes, provenance, repository capability discovery, workflow optimization, and candidate evaluation. It also contains legacy mechanisms and claims that are not suitable for direct adoption, including mutable shared-state truth, pseudo-signatures, scalar release scores, unbounded reasoning memory, and self-promotion paths.

WOLF15 Sentient already separates model proposals from a deterministic Control Kernel. Any learning mechanism must preserve that boundary.

## Decision

WOLF15 Sentient will adopt a separate Learning & Adaptation Plane.

The Control Kernel remains the only owner of workflow state, transitions, authority checks, gates, and termination. Learning components may observe evidence-backed episodes and produce candidates, evaluations, lessons, provider preferences, and advisory context. They cannot increase authority or directly activate a change.

Memory is divided into working, episodic, semantic, procedural, and audit classes. Canonical memory stores structured facts and evidence references, not private chain-of-thought.

Repository discovery and capability extraction feed the Capability Fabric through versioned manifests and evaluation. Discovery never implies eligibility or authority.

Optional learning failure must not degrade the baseline task path. Integrity or authority ambiguity fails closed for the affected artifact.

## Consequences

Positive:

- learning can evolve independently of the hot path;
- capability donors can be adopted without bloating the core;
- candidate changes remain reversible and evidence-bound;
- multiple providers can coexist and be selected by task profile;
- source conflicts and incomplete evidence remain visible.

Costs:

- additional contracts and lifecycle states;
- future persistence needs durable journal/registry stores;
- evaluation corpora and replay receipts must be maintained;
- activation requires a separate promotion mechanism.

## Explicitly rejected

- automatic self-promotion;
- learning-driven authority escalation;
- Redis or any mutable cache as canonical memory;
- one aggregate score as release authority;
- raw hidden reasoning as durable memory;
- dynamic availability-based selection of authority-bearing execution;
- treating a simulator, README, or source claim as runtime proof.

## Verification for this ADR slice

The first executable slice is contract-only. Tests must prove that unmeasured claims remain UNKNOWN, VERIFIED claims require evidence references, evidence references resolve inside their ContextBundle, and learning candidates cannot represent external mutation or active promotion without evaluation/approval bindings.

No workflow wiring is authorized by this ADR.
