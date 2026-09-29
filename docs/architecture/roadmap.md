# WOLF15 Sentient Master Roadmap — CP0 to CP9

## Authority

This file is the **single normative checkpoint roadmap** for WOLF15 Sentient.

Only the checkpoint identifiers defined here are valid for current planning:

`CP0, CP1, CP2, CP3, CP4, CP5, CP6, CP7, CP8, CP9`.

Other documents may describe architecture, historical implementation slices,
donor mappings, research batches, PR history, or legacy milestone names, but
they **must not define another checkpoint sequence**. If any other document
conflicts with this file, this file controls checkpoint ownership and ordering;
the conflicting document must be corrected, reclassified as historical/research
evidence, or removed.

The [Final Target Skeleton](final-target-skeleton.md) defines where checkpoint
responsibilities land. [Canonical ownership](canonical-ownership.md) defines
which subsystem owns them. [Current State](current-state.md) records what is
actually implemented. None of those documents may create a second roadmap.

## Current position

- **CP0 — Cognitive Foundation:** `CLOSED / PASS`.
  Accepted architecture baseline:
  `bad73335f518d89356b88cba1cc26730808cd224`.
  Post-close documentation/research addenda do not reopen CP0.
- **CP1 — Real Sentient Reasoning:** `ACTIVE_NEXT / NOT_IMPLEMENTED`.
- **CP2–CP9:** `LOCKED / FUTURE_CHECKPOINT`.
- Current runtime authority remains `READ_ONLY`.
- Browser/WebMCP, capability registry, Foundry, controlled writes, learning/REE,
  and production deployment are not activated by this roadmap.

PR #16 / `dd5cf74ce47e395cf859a2b5130790129af01e16` froze the
documentation-only `ALG-REG-001` addendum after CP0. The current WebMCP/master
roadmap documentation branch is also documentation-only and does not change
the CP0 acceptance SHA.

## Master sequence

| CP | Official name | Primary outcome | Status |
| --- | --- | --- | --- |
| **CP0** | Cognitive Foundation | Deterministic Control Kernel foundation, typed contracts, offline evidence/reasoning foundation, governance and architecture invariants | **CLOSED / PASS** |
| **CP1** | Real Sentient Reasoning | One real model provider through the WOLF15 Model Gateway with typed output, cancellation and measurable budgets; no tool authority | **ACTIVE_NEXT** |
| **CP2** | Repository Intelligence | Exact-revision repository/source reading, structural analysis, provenance and evidence-bound reports | **LOCKED** |
| **CP3** | Production Grade v1 | Authenticated, durable, observable, recoverable **read-only** service | **LOCKED** |
| **CP4** | Personal JARVIS & Read-Only Intelligence | Owner interface, voice, personal/media connectors, Second Brain read path and read-only Browser/WebMCP capability | **LOCKED** |
| **CP5** | Capability OS | Versioned Capability Registry/Resolver, Unified Skills, tools, backend MCP and ephemeral WebMCP provider resolution | **LOCKED** |
| **CP6** | Capability Foundry | Controlled donor discovery, provenance, rights, extraction, sandbox/evaluation and candidate qualification | **LOCKED** |
| **CP7** | Controlled Technology Builder | Exact approved repository/personal/browser actions with prepare/review/approve/execute receipts | **LOCKED** |
| **CP8** | Adaptive Intelligence | Verified episodes, independent evaluation, REE/adaptation candidates, temporal validation and controlled promotion | **LOCKED** |
| **CP9** | Technology Company OS | End-to-end integration of all checkpoint-proven capabilities without weakening earlier authority/evidence gates | **LOCKED** |

Implementation gates are sequential:

~~~text
CP0 -> CP1 -> CP2 -> CP3 -> CP4 -> CP5 -> CP6 -> CP7 -> CP8 -> CP9
~~~

Research for later checkpoints may happen early, but its implementation status
must remain:

~~~text
FUTURE_CHECKPOINT
-> DEFER
-> NO RUNTIME ACTIVATION
~~~

Research discovery never changes checkpoint order.

---

## CP0 — Cognitive Foundation

### Objective

Freeze the WOLF15 identity, deterministic authority chain, typed control
contracts, source/evidence rules, offline reasoning seam, cognitive
observability foundation, repository trust controls and architecture ownership.

### Accepted foundation

CP0 includes the already-integrated historical slices for:

- deterministic API/router/state/trace foundation;
- deterministic orchestration and bounded revision loops;
- repository trust/CI/CodeQL foundation;
- M2 caller-supplied evidence/context helper;
- SK-01 governance/catalog work;
- M3-A offline reasoning contracts and evidence bridge;
- SCRS v0 advisory observability;
- canonical ownership and final architecture invariants.

Those labels are historical implementation names, **not separate current
checkpoints**.

### Acceptance

CP0 is accepted at
`bad73335f518d89356b88cba1cc26730808cd224`, with exact-main CI and
CodeQL PASS recorded for that source. The Control Kernel remains the authority
owner and runtime authority remains read-only.

### Allowed after closeout

Documentation-only research/addenda may:

- pin donor source revisions;
- record provenance and licenses;
- define anti-patterns;
- map research to CP1–CP9;
- improve target architecture documentation.

They may not activate providers, tools, skills, browser access, memory writes,
repository writers, learning or deployment, and they do not reopen CP0.

---

## CP1 — Real Sentient Reasoning

### Objective

Replace the labelled offline/stub reasoning path with **one real model
provider** behind a narrow WOLF15-owned cognitive gateway while keeping the
Control Kernel, evidence spine and workflow authority unchanged.

### Canonical ownership

~~~text
Control Kernel
  -> Sentient reasoning
  -> sentient/model_gateway/
  -> models/providers/<provider>
  -> real model API
  -> WOLF15 typed validation
  -> ReasoningProposal
  -> evidence/controller checks
  -> Control Kernel
~~~

`sentient/model_gateway/` is the single cognitive-facing gateway owner.
`models/providers/` contains concrete providers. No second
`models/gateway/` authority/gateway is created.

### Primary donor input

`ARCH-DONOR-PYDANTIC-AI-01` is the highest-value current CP1 donor:

- repository: `tjx578/pydantic-ai-sentient`;
- reviewed snapshot:
  `05f2f35ca8af6f1382f06761c6a9a23dbd341728`;
- license: MIT;
- decision: selective adoption;
- preferred CP1 pattern: `pydantic_ai.direct` / direct model/provider/profile
  abstraction behind WOLF15's gateway;
- full Pydantic AI `Agent` graph is **not** a WOLF15 orchestrator.

### Required deliverables

- provider-neutral `ModelGateway` request/response contract;
- one concrete real provider adapter;
- explicit Model / Provider / Profile separation;
- schema-constrained `ReasoningProposal`;
- cancellation propagation;
- distinct deadline/timeout scopes;
- bounded input/output/context/token/request/cost controls where measurable;
- usage telemetry with missing cost represented as `NOT_MEASURED`, not zero;
- typed provider failure taxonomy;
- exact model/provider identity in execution receipts;
- evidence binding preserved before/after model calls.

### Acceptance

CP1 passes only when a real provider proves:

- valid typed output accepted;
- invalid/malformed output rejected;
- cancellation terminates the affected request;
- timeout is distinguishable from provider/auth/rate-limit/policy failures;
- token/context/usage limits are measurable and enforced where defined;
- provider/model identity and usage are observable;
- no model output can set workflow state, factual truth or authority;
- no silent multi-provider fallback changes behavior mid-run;
- no tool/MCP/repository/memory execution authority is introduced.

### Explicitly excluded

- repository reading or mutation;
- runtime skill registry;
- tool execution;
- MCP capability activation;
- durable personal memory;
- voice/JARVIS runtime;
- WebMCP/browser runtime;
- adaptive/self-learning behavior.

Pydantic AI patterns discovered for CP2, CP4, CP5 and CP8 remain
`FUTURE_CHECKPOINT -> DEFER`.

---

## CP2 — Repository Intelligence

### Objective

Make repositories and approved technical sources readable as exact,
source-bound evidence without granting write authority.

### Required deliverables

- `RepositorySnapshotReader` bound to exact revision/digest;
- repository tree/source map;
- language-aware parser/AST where justified;
- dependency/import graph;
- source location and provenance model;
- read-only resolver producing `SourceRef` and bounded `ContextBundle`;
- evidence-grounded repository findings;
- context/chunking policy based on semantic/responsibility boundaries;
- spill/handle strategy for oversized tool/repository output;
- explicit freshness/conflict/missing-source behavior.

Pydantic AI donor patterns that may inform CP2 include `RepoContext`,
path/content-hash deduplication and context/tool-output spill patterns. They do
not become donor-instruction authority.

### Acceptance

- requested repository resolves to an exact immutable revision;
- material finding traces to file/source bytes and location;
- stale/missing/conflicting evidence remains explicit;
- donor `AGENTS.md`, `CLAUDE.md`, README and code comments are treated as data;
- oversized source output does not silently overflow model context;
- repository access is demonstrably read-only;
- branch name alone is never runtime identity.

### Explicitly excluded

- repository/file writes;
- worktree/branch creation;
- shell/test execution as a mutation path;
- automatic donor code execution;
- capability activation.

---

## CP3 — Production Grade v1

### Objective

Turn the read-only cognitive system into an authenticated, durable, observable
and recoverable service before adding personal or mutating capabilities.

### Required deliverables

- authenticated owner/caller boundary;
- durable task/run/event persistence;
- idempotent task submission and replay rules;
- cancellation and restart recovery;
- lease/fencing semantics where concurrency needs them;
- durable audit/outbox/receipt semantics;
- structured logging, tracing and metrics;
- readiness checks tied to real dependencies;
- secret/credential isolation;
- staging and rollback evidence;
- generic execution-reality envelope.

The execution contract must preserve:

~~~text
HANDLER_RETURNED != EXECUTED
EXECUTED != ACCEPTED
ACCEPTED != VERIFIED
SIMULATED != REAL
FALLBACK != EQUIVALENT_SUCCESS
~~~

Pydantic AI OpenTelemetry patterns and Signett-style cancellation,
idempotency/recovery ideas are research donors here; WOLF15 owns the contract.

### Acceptance

- duplicate requests do not create ambiguous duplicate canonical runs;
- restart/cancellation/recovery preserves task truth;
- auth/policy denial produces no side effect;
- receipts bind source/config/provider/run identity;
- required dependency failure changes readiness;
- logs/traces do not leak credentials or private prompt/source payloads;
- rollback restores exact software without restoring revoked authority.

### Explicitly excluded

- personal connector writes;
- browser/WebMCP runtime actions;
- dynamic Capability OS activation;
- repository mutation;
- learning-driven behavior changes.

---

## CP4 — Personal JARVIS & Read-Only Intelligence

### Objective

Give the owner a JARVIS-style read-only interface across voice, permitted
personal/media sources and browser-native capabilities while preserving the
same Kernel task/authority path as text/API requests.

### Required deliverables

- Owner Console interface over stable contracts;
- voice/STT/TTS or realtime-voice transport with interruption/cancellation;
- owner-scoped read-only personal connectors;
- evidence-bound Second Brain retrieval for permitted personal/project sources;
- YouTube/media intake with metadata, transcript/caption provenance,
  segmentation, knowledge extraction and explicit limitations;
- browser session abstraction;
- WebMCP discovery and **read-only** invocation;
- `WEBMCP_NATIVE` receipt with origin/session/document/tool identity;
- explicit `BROWSER_AUTOMATION_FALLBACK` classification if a separately
  qualified fallback is later used.

Pydantic AI realtime-voice patterns may be a donor here. WebMCP donor patterns
are defined in `docs/research/webmcp-donors/`.

### Acceptance

- voice and text resolve to the same typed task/authority path;
- missing connector/media transcript remains partial/`NOT_MEASURED`;
- third-party media/web/page text is data, never instruction authority;
- one permitted real read-only personal source is proven end to end;
- one allowed WebMCP page tool is discovered and invoked read-only with receipt;
- navigation/tool removal/session change invalidates stale WebMCP descriptors;
- isolated browser context is the default unless an owner explicitly authorizes
  a higher-scope logged-in browser session.

### Explicitly excluded

- sending messages;
- calendar/file/account writes;
- purchases/bookings/approvals/deletes;
- repository mutation;
- page-local confirmation as owner authority.

---

## CP5 — Capability OS

### Objective

Create one governed capability plane for skills, tools, backend MCP, model
providers and ephemeral browser/WebMCP providers.

### Required deliverables

- versioned Capability Registry;
- task-scoped Capability Resolver;
- Unified Skill registry/loader;
- provider manifests and revocation;
- canonical tool descriptors;
- backend MCP gateway/registry contracts;
- provider health/evidence metadata;
- task/run generation pinning;
- progressive disclosure so full procedures/tools load only when relevant;
- bounded tool search;
- WebMCP page tools normalized as ephemeral providers.

Pydantic AI progressive disclosure, deferred tool loading and tool-search
patterns may inform this checkpoint.

### Core invariants

~~~text
DISCOVERED != QUALIFIED
QUALIFIED != ACTIVE
ACTIVE != AUTHORIZED_FOR_THIS_TASK
CAPABILITY_LOADED != CAPABILITY_AUTHORIZED
TOOL_SEARCH_RESULT != QUALIFIED_TOOL
~~~

### Acceptance

- only qualified providers can be selected;
- provider/capability generation is pinned for the run;
- revoked/stale providers fail closed;
- policy disagreement overrides provider/tool hints;
- WebMCP session/origin/tool changes invalidate ephemeral provider state;
- skill/tool instructions cannot raise authority or request unapproved secrets;
- registry availability does not bypass per-call Kernel authorization.

### Explicitly excluded

- automatic donor acquisition;
- self-installation;
- consequential external actions;
- candidate self-promotion.

---

## CP6 — Capability Foundry

### Objective

Allow WOLF15 to discover and qualify new knowledge/capability donors without
copying entire frameworks or granting them runtime authority.

### Required deliverables

~~~text
donor discovery
  -> exact revision pin
  -> provenance / rights / license
  -> dependency / security inspection
  -> architecture reconstruction
  -> canonical capability extraction
  -> overlap / conflict analysis
  -> sandbox / offline evaluation
  -> shadow qualification
  -> candidate manifest
  -> separate admission decision
~~~

This checkpoint owns operational donor qualification. Documentation-only donor
research may exist earlier, but it does not substitute for CP6 qualification.

### Donor sets already researched

- Pydantic AI donor;
- WebMCP specification/skills/runtime/evaluation donors;
- frozen `ALG-REG-001` algorithm donor corpus;
- other future donors recorded as research inputs.

### Acceptance

- exact source/revision and provenance are reproducible;
- rights/license uncertainty blocks code adoption;
- donor instructions never execute by being read;
- overlap/equivalence is compared by contract/behavior, not name;
- security, dependency and data-egress boundaries are recorded;
- sandbox/offline/shadow evaluation is independent of candidate claims;
- only a candidate manifest emerges; Foundry cannot activate itself.

### Explicitly excluded

- fetch -> import -> execute;
- bulk skill overwrite;
- mutable/latest runtime dependency by default;
- automatic production installation;
- direct capability activation.

---

## CP7 — Controlled Technology Builder

### Objective

Permit exact owner-approved effects after the read-only system, Capability OS
and Foundry have proven their boundaries.

### Required deliverables

- action proposal and preview;
- exact task/owner/target/resource/action binding;
- artifact/input digest binding;
- expiry/revocation/replay protection;
- isolated worktree;
- bounded file/shell/test/Git operations;
- feature branch and draft PR workflow;
- controlled personal actions;
- consequential WebMCP/browser actions;
- idempotency/operation journal where an effect can be ambiguous;
- execution receipt and independent postcondition verification.

### Acceptance

- no write occurs without the exact required grant;
- `READ_ONLY` is enforced by operation allowlist, not a label;
- list-time tool filtering never replaces call-time authorization;
- ambiguous mutation outcomes reconcile against authoritative state;
- repository work cannot directly mutate protected/default main;
- browser/page approval alone cannot authorize WOLF15;
- every effect is auditable and reversible where the domain allows it.

### Explicitly excluded

- autonomous merge;
- autonomous deployment;
- unreviewed sending/purchase/booking/delete;
- unrestricted shell or credential access.

---

## CP8 — Adaptive Intelligence

### Objective

Learn from verified outcomes without allowing the learner, candidate or model
to control its own evaluator or promotion.

### Required deliverables

- verified episode/outcome journal;
- fixed, versioned evaluation rubrics;
- baseline vs candidate replay;
- held-out and temporal validation;
- provider/skill/retrieval/WebMCP regression suites;
- shadow evaluation;
- drift and persistence analysis;
- bounded optimizer/REE candidate lifecycle;
- owner/governance approval and versioned activation;
- rollback/supersession path.

Pydantic Evals is a strong donor for dataset/case/evaluator/experiment/report
separation. WebMCP Evals and WindTunnel-style methodology may support browser
capability comparison. Donor benchmark claims must be reproduced on WOLF15
workloads before they become WOLF15 evidence.

### Acceptance

~~~text
verified outcome
  -> Episode
  -> Candidate
  -> Replay
  -> Held-Out / Temporal Evaluation
  -> Shadow
  -> Independent Review
  -> Owner Approval
  -> Versioned Activation
~~~

- candidate cannot change the fixed evaluator/rubric;
- missing measurements remain `NOT_MEASURED`;
- regression/hard-gate failure cannot be averaged into PASS;
- online learning cannot silently alter active routing;
- current runs stay pinned to their original approved generations.

### Explicitly excluded

- self-promotion;
- model-written memory becoming verified fact;
- LLM-as-judge as sole verdict authority;
- adaptive authority escalation.

---

## CP9 — Technology Company OS

### Objective

Integrate the checkpoint-proven product into one operational WOLF15 Sentient
system without creating a new authority shortcut.

### Integrated target

CP9 composes:

- Sentient Core / Neural Orchestrator;
- Control Kernel;
- Elite Specialist Organization;
- Evidence-Grounded Second Brain;
- Personal JARVIS and media/voice interface;
- Browser Capability Plane / WebMCP;
- Capability OS and Unified Skills;
- Capability Foundry;
- Controlled Technology Builder;
- Adaptive Intelligence / REE;
- Owner Console and operational observability.

### Acceptance

- each subsystem enters CP9 with its own earlier checkpoint evidence;
- end-to-end task/run/authority/evidence receipts remain traceable;
- multi-provider/fallback behavior preserves execution reality;
- partial subsystem failure fails closed or degrades explicitly;
- personal/browser/repository actions retain exact approval boundaries;
- capability/adaptation generations are pinned and reversible;
- production deployment requires its own exact-artifact operational approval.

CP9 cannot waive any CP0–CP8 invariant.

---

## Retired and normalized planning labels

### Retired 13-checkpoint draft

The uploaded planning draft that defined `CP-00` through `CP-12` is
**retired as a checkpoint authority**. Its useful responsibilities are folded
into this master sequence as follows:

| Retired draft | Master owner |
| --- | --- |
| CP-00 baseline/status | **CP0** |
| CP-01 manual donor/adaptation register | documentation-only donor research under **CP0**; operational qualification under **CP6** |
| CP-02 source/evidence acquisition | **CP2** |
| CP-03 reasoning adapter | **CP1** |
| CP-04 read-only repository audit | **CP2** |
| CP-05 persistent task/run/event | **CP3** |
| CP-06 authenticated/observable service | **CP3** |
| CP-07 Owner Console | **CP4** |
| CP-08 personal brief + document library | **CP4** |
| CP-09 Capability Fabric/skill registry | **CP5** |
| CP-10 Capability Foundry | **CP6** |
| CP-11 approved actions | **CP7** |
| CP-12 Learning/REE | **CP8** |
| no equivalent in retired draft | **CP9** integrated product |

No document may revive `CP-00..CP-12` as a parallel roadmap.

### Legacy M/PR labels

Historical documents may retain names such as M1, M2, M3-A, M3-B, M4–M10 or
PR-0…PR-8+ because they identify old implementation/research artifacts.
They are **not current scheduling identifiers**.

For interpretation only:

| Historical label | Master checkpoint |
| --- | --- |
| M0/M1/M2, SK-01, M3-A, SCRS v0 historical foundation slices | CP0 |
| M3-B / real provider | CP1 |
| M4 | CP2 |
| M5 | CP3 |
| M6 | CP4 |
| M7 | CP5 |
| M8 | CP6 |
| M9 | CP7 |
| M10 | CP8 |
| integrated product / no former M equivalent | CP9 |

New planning, issue, PR, ADR, donor assessment and status documents must use
the master CP0–CP9 identifiers.

## Change-control rule

A new research discovery may change **what** belongs inside a checkpoint, but
not checkpoint numbering or order unless the owner explicitly approves a
master-roadmap revision.

Every future architecture/research document must therefore state one of:

- `MASTER_CP_OWNER: CPx`;
- `HISTORICAL_ONLY`;
- `FUTURE_CHECKPOINT -> DEFER`;
- `OUT_OF_ARCHITECTURE`.

No additional CP sequence, milestone roadmap, or parallel tracker is canonical.
