# Canonical responsibility and checkpoint map

## Authority and status

This is the canonical CURRENT-to-TARGET ownership map. It aligns the
[North Star](super-intelligence-reference-architecture.md) with the in-repository
[Final Target Skeleton](final-target-skeleton.md) without creating future
packages. The last verified pre-WebMCP-amendment canonical main is
`dd5cf74ce47e395cf859a2b5130790129af01e16` (PR #16). A target path is a
design destination, not an implemented import.
Historical records in [Current State](current-state.md) remain bound to their
own revisions. [Authority policy](../governance/authority-model.md) governs
permissions; architecture names, README files and scores cannot grant them.


The [Master Roadmap](roadmap.md) is the only normative checkpoint sequence.
This ownership map may assign responsibilities to CP0–CP9 but does not define
a second ordering, milestone alias, or checkpoint gate.

The Control Kernel is the single owner of authority, workflow state, gates,
transitions and termination. Reasoning, specialists, memory and learning
provide proposals or evidence to it. Moving files requires a separate tested
migration and an explicit ownership decision; parallel target names do not
authorize duplicate implementations.

## Current implementation to target skeleton

All package paths below are relative to `src/wolf15_sentient/` unless qualified.

| Responsibility | CURRENT implementation | TARGET skeleton / owner | Status and delivery boundary |
| --- | --- | --- | --- |
| HTTP intake and health | `api/app.py`; `main.py` ASGI export | `api/`, future `apps/owner-console/` client | CURRENT deterministic `/tasks`; authenticated service CP3 |
| Typed boundaries | `contracts/` task, execution, evidence, learning, reasoning, cognition schemas | `contracts/` | CURRENT; add schemas only with the owning subsystem |
| Authority, gates, transitions and workflow state | `orchestration/workflow.py`, `state.py`, `transitions.py`, `mode_router.py` | `control/` owns policy/lifecycle; `orchestration/` composes work through it | FOUNDATION; one owner today, no physical split in CP0 |
| Intent routing and reasoning proposals | `reasoning/runtime.py` with labelled stub and trusted offline adapter seam | `sentient/` intent/task_router/planner/synthesis; model gateway | CP0 historical offline foundation; one real provider belongs to CP1 |
| Evidence and context assembly | `evidence/context.py`; caller-supplied source content | `evidence/` provenance/claims; `context/` assembly/budget/freshness | CP0 historical helper; external repository/source resolution belongs to CP2 |
| Cognitive telemetry | `cognition/reflex.py`, cognition contracts | `sentient/cognition/` with observability integration | SCRS v0 CURRENT offline/advisory; calibration and mature use CP8 |
| Specialist organization | `agents/stubs.py`: Architect, Engineer, Reviewer | `elite_team/`: six divisions and 28 roles | Three CURRENT deterministic stubs; full roster TARGET |
| Repository intelligence | Repository reference and explicit missing-reader limitation only | `repositories/`; bounded `execution/repo_reader/` | CP2 TARGET; no current reader |
| Evidence-Grounded Second Brain | CP0 evidence and learning/memory-class contracts | `context/`, `evidence/`, `knowledge/`, `memory/` | CP2 source/evidence expansion, CP3 durability, CP4 owner-scoped read intelligence |
| Unified Skill System | SK-01 catalog, assessment and qualification policy in `docs/` | package `skills/` engine; root `skills/` procedure packages | Governance CURRENT; 25 priority design candidates, zero qualified-by-catalog claims; runtime registry CP5 |
| Capability Fabric and multi-provider registry | Offline reasoning protocol only; no provider registry | `capabilities/`, `models/`, `tools/`, `mcp/` | CP5 TARGET; one narrow real model provider begins in CP1 |
| Capability Foundry | Design and qualification policy | `capability_factory/` | CP6 TARGET; donors require provenance, rights, isolation and independent admission |
| Learning and REE | `contracts/learning.py`; separate offline REE development lane | `learning/`, `ree/`, `evaluation/` | CP8 TARGET; no current evaluator activation or profile mutation |
| Personal assistant | Architecture documents only | `owner/`, `personal/`, `intelligence/`, `integrations/` | CP4 TARGET, initially read-only |
| Browser Capability Plane / WebMCP | Research and architecture only; no browser provider | `integrations/browser/webmcp/`, `capabilities/providers/webmcp/`, `contracts/webmcp.py`, root `apps/owner-console/features/browser/` | CP4 read-only discovery/invocation; CP5 provider resolution; CP7 consequential actions; runtime absent |
| Owner-controlled execution | Authority and approval design only | `execution/` controlled boundary plus Kernel approval contracts | CP7 TARGET; no current writer/executor |
| Owner interface | External HTML design reference; no tracked console application | root `apps/owner-console/` | CP4 interface track TARGET; Next.js/TypeScript and SSE |

The post-CP0 addendum selects sentient/model_gateway/ as the single
cognitive-facing gateway owner. Concrete provider implementations belong to
models/providers/. The earlier models/gateway/ blueprint name must not become
a competing gateway. These are target responsibilities; this change adds no
runtime packages.

ReasoningPlan has one contract owner, contracts/. Sentient produces proposals;
orchestration coordinates workflow semantics through Control Kernel-owned
state, authorization, transitions and termination. Neither plans nor model
outputs grant tool authority. See the [adoption canon](algorithm-adoption-canon.md).

Control and orchestration must not become competing authority chains.
Current `api/`
and `contracts/` stay in place; `agents/` to `elite_team/` is a later migration.

## Frozen North Star

The complete product target remains: **Sentient Core / Neural Orchestrator**,
**Control Kernel**, **Elite Specialist Organization**, **Evidence-Grounded
Second Brain**, **Unified Skill System**, **Capability Fabric**, **Capability
Foundry**, **Multi-provider Registry**, **Durable Memory**, **Learning**,
**REE**, **Browser Capability Plane (WebMCP + explicitly classified browser fallback)**,
and **Owner-Controlled Execution**. CP0 completes their foundation;
it does not narrow the product to a telemetry library or install the target
roster. Product-specific systems such as WOLF15 Trading remain external owners
of their own domain policy and execution.

## Ten architecture invariants

1. Control Kernel owns authority.
2. Model output is proposal.
3. Evidence outranks confidence.
4. Missing evidence remains `NOT_MEASURED`.
5. Memory does not own workflow state.
6. Skill trust cannot increase authority.
7. Donor order does not define priority.
8. Candidate cannot self-promote.
9. A run pins relevant generations.
10. External side effects use a controlled boundary.

These are both design constraints and audit questions. Where the relevant
subsystem is absent, compliance means it remains absent and cannot be
activated by a score or document. It does not mean future provider pinning,
durable approval, sandboxing or distributed replay protection has been tested.
Current concrete bindings include the CP0 evidence helper source revision/policy,
the historical offline reasoning input digest, and SCRS complete profile digest plus event lifecycle. Future generations need
their own implementation and acceptance evidence.

## Local README contract policy

> No Major Subsystem Without README Contract.
>
> No Responsibility Change Without README Impact Review.
>
> README explains local ownership; canonical architecture decides global ownership.

Every current major subsystem README records: responsibility, public inputs and
outputs, dependencies and consumers, authority/side-effect limits, verification
paths, current limitations, and the target migration boundary. CP0 creates only
the seven current package READMEs plus architecture and tests READMEs. A future
major subsystem receives its README in the same change that introduces it.

A PR changing responsibility must identify affected READMEs, update this map
when global ownership changes, and explain any intentionally unaffected local
contract. Review checks for a single owner and valid cross-links. This is a
review policy; no automated README gate is claimed. Historical receipts are
preserved rather than rewritten as current evidence.

## Neural Orchestrator UX reference

The owner-designated `WOLF15_Sentient.html` is the **Neural Orchestrator UX
Reference Prototype**, with a future production destination of
`apps/owner-console/` (Next.js/TypeScript + SSE). CP0 records that relationship;
it creates no frontend application, backend transport, voice integration or
production service.

The exact named file was not available in the bounded attachment/Downloads
inventory used for this review. A supplied local variant,
`WOLF15_Sentient_Interactive.html`, was inspected as static source: it contains
neural visualization, browser voice controls, listening/responding/speaking
states, stop/interrupt controls and session cleanup. Its help text explicitly
states that an AI backend is not connected. These are source observations;
browser, microphone and end-to-end acceptance were NOT_EXECUTED. The variant
is not asserted to be byte-identical to the owner-designated prototype.

External source bindings (not vendored or loaded by runtime):

- `WOLF15_SENTIENT_TARGET_SKELETON.md`: SHA-256
  `ece61cd656b967364257cd2a683077021dec69e8b20d069dcef6cbf3b54ef5b9`.
- `WOLF15_Sentient_Interactive.html`: SHA-256
  `e9951da81f88fcd317185bba151839b66190b36ee8c48ee43488cf4fc9e9b959`.

The canonical mapping and UX designation above are repository decisions; the
local source digests permit later reconciliation without claiming that those
external files are portable repository dependencies.

## Browser capability ownership rules

- `mcp/` owns backend/service MCP.
- `integrations/browser/webmcp/` owns browser-session discovery,
  normalization, invocation and receipts.
- `capabilities/providers/webmcp/` owns provider representation for the
  Capability Registry/Resolver, not browser execution.
- `execution/browser/fallback/` owns later bounded automation fallback and
  reports `BROWSER_AUTOMATION_FALLBACK`, never `WEBMCP_NATIVE`.
- `apps/owner-console/features/browser/` presents browser state, approvals
  and receipts; it is not the authority root.

A page tool is session-bound. `Registered != Qualified != Active !=
Authorized-for-this-task`. WebMCP annotations are provider assertions and
policy inputs, not proof or authority.

The former external `WOLF15_SENTIENT_TARGET_SKELETON.md` remains historical
input. [Final Target Skeleton](final-target-skeleton.md) is the in-repository
target tree; it creates no empty runtime packages.
