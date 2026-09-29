# WOLF15 Sentient reference architecture

## Status and evidence

**Roadmap authority:** [Master Roadmap — CP0 to CP9](roadmap.md). Historical
M1/M2/M3/M4–M10 labels in this document identify source snapshots or prior
design vocabulary only; they do not define a parallel checkpoint sequence.


The [CP0 canonical ownership map](canonical-ownership.md) aligns the current
packages with this North Star and freezes ten architecture invariants. The
historical baseline below remains its original evidence snapshot; later
integration is recorded in [Current State](current-state.md).

**M1-B target boundary, 2026-09-28.** This is a design for future increments,
not a claim that the described services exist. The inspected baseline is
canonical `main` at `e24db7bc057ec4f2bcd9bf0599254effae49f18a`:
[`current-state.md`](current-state.md), the
[`Authority Model`](../governance/authority-model.md), ADR-001, ADR-004,
ADR-005, ADR-006, `src/wolf15_sentient/`, and the
[CI run](https://github.com/tjx578/wolf15-sentient/actions/runs/36373401788).
That baseline has a FastAPI `/tasks` and `/health` surface, a deterministic
in-memory LangGraph kernel, three deterministic role stubs, typed evidence and
learning contracts, and `READ_ONLY` as its only accepted runtime authority.
CI passed 56 tests on Python 3.11–3.13. Live model reasoning, source retrieval,
durable memory, execution adapters, and production runtime are not measured or
implemented by that evidence.
The proposed six divisions and 28 specialists remain an organizational
target; the three deterministic stubs are the only implemented roles.

## Decision boundary

WOLF15 Sentient is the product. Its Core may propose plans and responses;
the Control Kernel owns workflow state, admissibility, authority checks,
transitions, gates, and termination. Specialist roles and providers return
typed proposals or observations. They do not grant authority. Target systems,
including WOLF15 Trading, retain their own strategy, risk, and execution
ownership. The name “Sentient” describes a product goal, not consciousness.

| Responsibility | Target owner | Baseline at this snapshot |
| --- | --- | --- |
| Request validation, task state, transitions, gates | Control Kernel | Deterministic in-memory kernel |
| Intent, context use, plan, response synthesis | Sentient Core | No live model-backed Core |
| Bounded specialist work | Elite AI Agent Team OS | Three deterministic stubs |
| Sourced retrieval and knowledge | Intelligence & Knowledge / Second Brain | Contracts only; no resolver or store |
| Provider discovery and task-scoped selection | Capability Fabric / Unified Skills | No runtime registry or resolver |
| Browser/WebMCP capability discovery and invocation | Browser Capability Plane + Capability Fabric | Target only; no browser provider or WebMCP runtime |
| Donor extraction and offline qualification | Capability Foundry | Design only |
| Episode and candidate evaluation | Learning & Adaptation / REE | Learning contracts; REE is not wired |
| Personal services and approvals | Personal Assistant / Owner Console | Design only |

## Target flow

```text
Owner or approved event
  -> authenticated intake and explicit task scope
  -> Control Kernel: authority, state, and lifecycle
  -> Context assembler: versioned SourceRef and ContextBundle
  -> Sentient Core and bounded specialists: typed proposals
  -> Control Kernel: independent gates and adapter authorization
  -> authorized adapter or read-only response
       -> backend/service MCP when appropriate
       -> browser WebMCP when page/session capability is appropriate
       -> explicitly classified browser fallback only when needed
  -> outcome evidence and owner-visible result
  -> optional journal and offline candidate evaluation
```

Every future adapter call must be checked at the execution boundary. A mode,
model output, registry entry, credential, score, or `READY_WITH_CONDITIONS`
label cannot expand the task's authority. Missing, stale, conflicting, or
unmeasured evidence remains explicit and cannot become success by default.
An optional learning failure leaves the authorized baseline path available;
an integrity or authority ambiguity blocks the affected artifact.

The diagram is a responsibility map. It does not prescribe separate services,
databases, queues, or deployment platforms. The current `api`, `contracts`,
`agents`, and `orchestration` package folders remain in place. Renaming them
to `control` or `elite_team` requires a separate tested migration.

REE is a side process for verified outcomes and offline candidate evaluation.
Its proposed `ΔR` score and bounded `α/β/γ` updates are not a health certificate
or a model-training operation. Missing metrics remain `NOT_MEASURED`; a score
near zero can result from cancellation. Candidate weights cannot alter the
fixed evaluation rubric, critical vetoes, approved profile, or current task.
Active profile promotion is a separate approval and version-pinning event.
An offline result must carry metric provenance, normalizer/config versions,
and a check of the final candidate vector, including the `|δ| ≤ 0.05` bound.
The existing learning contracts do not implement this REE process or write
`alpha_beta_gamma.yml` or `reflective_heuristics.json`.

## Cross-cutting invariants

1. **One authority chain.** The Kernel mediates external effects; providers,
   memory, learning, and REE cannot self-approve or self-promote.
2. **Source-bound truth.** Claims carry source identity, revision, observation
   time, and evidence status. Source claims are not runtime observations.
3. **Version-pinned behavior.** A task pins relevant policy, provider,
   knowledge, and approved profile generations at intake. Mid-task updates
   do not silently change its behavior.
4. **Independent evaluation.** Candidate policy weights cannot change the
   fixed rubric or turn an unmeasured hard gate into PASS.
5. **Separate production decision.** Merge, deployment, secrets, production
   data, and broker actions require their own scoped owner authorization.
6. **Browser capability is not browser authority.** A discovered WebMCP tool,
   its annotations, active login session, page-local approval, or successful
   return cannot raise task authority.

## M1-B freeze and open decisions

This increment freezes ownership and dependency direction, not provider
choices, storage topology, retention periods, service levels, or activation
thresholds. Those require evidence and owner decisions in later milestones.
The [Final Target Skeleton](final-target-skeleton.md),
[Browser Capability Plane / WebMCP](webmcp-browser-capability-plane.md),
[Personal Assistant](personal-assistant-architecture.md),
[Second Brain](second-brain-architecture.md),
[Capability Fabric](capability-fabric.md),
[Capability Foundry](capability-foundry.md), and
[production reference](production-reference-architecture.md) define their
boundaries. The [roadmap](roadmap.md) names the verification gate for each
step. Existing ADRs retain their historical decisions; this reference does
not silently supersede them.
