# Donor adaptation register — normalized to Master CP0–CP9

## Status

`RESEARCH_REGISTER / NOT_A_ROADMAP / NO_RUNTIME_EFFECT`

This register preserves the useful donor analysis from the uploaded legacy
13-checkpoint planning summary while removing its alternative checkpoint
numbering. The only checkpoint authority is
[WOLF15 Sentient Master Roadmap — CP0 to CP9](../architecture/roadmap.md).

The uploaded summary referenced local-only planning artifacts
(`donor-adaptation-checkpoints.md`, `checkpoint-plan.json`, and a roadmap
verification receipt). Those files were not present in the inspected remote
repository, so they are not treated as canonical GitHub documents.

The summary's repository baseline
`8cfabf70b2927c7eaf73ae8983df4f9ca7c069fb` is historical. Current
checkpoint ownership must use the Master Roadmap and current repository state,
not that older planning baseline.

## Donor normalization

| Donor/source | Useful patterns preserved | Master CP owner(s) | Boundary |
| --- | --- | --- | --- |
| **paperclip578 / Paperclip** | task/run lifecycle, lease, budget, recovery, approval, audit, task-board patterns | CP3, CP4, CP7 | no second scheduler/state/authority owner |
| **multiagentruflo / Ruflo** | execution-reality semantics, claim/handoff, provider/capability matching, memory-policy patterns | CP3, CP5, CP7, CP8 | registration is not execution; bypass/default-permission and error-hiding patterns rejected |
| **context7** | library/version-aware technical documentation retrieval | CP2, CP4, CP5 | external query is source retrieval, not evidence truth or authority |
| **MCPkonektor / MCP specification/tooling** | capability negotiation, typed tool results, error envelopes, transport/security boundaries | CP3, CP5, CP6 | schema/tool hints do not create business connector authority |
| **dashboardanimation / D3** | evidence graph, timeline, brush/zoom, keyed visual updates | CP4 | visualization is presentation, not truth or score authority |
| **next.js** | Owner Console web foundation, server/client boundary, BFF/route-handler patterns | CP4 | framework/version choice requires its own implementation evidence |
| **tuyul_ea_dashboard / Deltalytix reference** | journal/review/filtering/widget UX patterns | CP4, CP6 | code transplant blocked until rights/security/data-contract qualification |
| **unlimited_book / Openlib patterns** | document catalog, personal library, reader position and file-hash patterns | CP2, CP4 | not a ready RAG/evidence system; download/storage/evidence path must be rebuilt |
| **Pydantic AI donor** | direct model/provider/profile, structured output, cancellation/usage; later RepoContext, progressive disclosure, realtime voice, evals | CP1 primary; CP2/CP4/CP5/CP8 deferred | full Agent graph cannot become WOLF15 Control Kernel |
| **WebMCP donor portfolio** | browser-native tool discovery/invocation, skills, security, polyfill/bridge/fallback and evaluation patterns | CP4, CP5, CP6, CP7, CP8 | page tool/annotation/session cannot raise authority |

Exact source revisions that are not present in the uploaded donor-summary text
remain `NOT_AVAILABLE_IN_UPLOADED_SUMMARY`; this register does not invent
missing hashes. Detailed exact-revision records already present for Pydantic AI
and WebMCP are linked below.

## Detailed donor records

- [Pydantic AI donor](pydantic-ai-donor/README.md)
- [WebMCP donor portfolio](webmcp-donors/README.md)
- [Frozen algorithm donor corpus](algorithm-donors/README.md)

## Retired 13-CP numbering

The former `CP-00..CP-12` plan is not carried forward. Its responsibilities
are normalized in the Master Roadmap's **Retired and normalized planning
labels** section. Donor records may state a Master CP owner but may never create
their own CP sequence.

## Research vs implementation rule

~~~text
DONOR DISCOVERED
!= QUALIFIED
!= ACTIVE
!= AUTHORIZED_FOR_THIS_TASK
~~~

Research for a future checkpoint may be completed early. Implementation remains
`FUTURE_CHECKPOINT -> DEFER` until the Master Roadmap opens that CP.
