# WOLF15 Sentient — Final Target Repository Skeleton

## Status

**Derived target map; implementation remains checkpoint-gated.**

The [root README §11](../../README.md#11-skeleton-main-dan-skeleton-tujuan-akhir)
is the canonical target tree. This selective subsystem map retains the earlier
WebMCP proposal as a navigation aid; it does not replace the complete README tree
or prove that any future folder exists. Reconciled against canonical
`main@1410df328615325a7f8ac76574e6bf4b57bad68e` on 2026-10-01.

It maps target paths to the [Master Roadmap](roadmap.md) but does not define a
second checkpoint sequence. CP numbering/order and gates derive from root
README §10; `roadmap.md` summarizes them. Future
subsystems and README contracts are created only when the owning checkpoint
implements them.

## Derived subsystem map

~~~text
wolf15-sentient/
├── src/
│   └── wolf15_sentient/
│       ├── api/
│       ├── sentient/
│       │   ├── intent/
│       │   ├── cognition/
│       │   ├── task_router/
│       │   ├── planner/
│       │   ├── delegation/
│       │   ├── synthesis/
│       │   ├── model_gateway/
│       │   └── response/
│       ├── control/
│       │   ├── state/
│       │   ├── transitions/
│       │   ├── authority/
│       │   ├── policy/
│       │   ├── gates/
│       │   ├── approvals/
│       │   ├── idempotency/
│       │   ├── termination/
│       │   └── recovery/
│       ├── contracts/
│       │   ├── task.py
│       │   ├── execution.py
│       │   ├── evidence.py
│       │   ├── context.py
│       │   ├── capability.py
│       │   ├── skill.py
│       │   ├── repository.py
│       │   ├── memory.py
│       │   ├── learning.py
│       │   ├── evaluation.py
│       │   ├── approval.py
│       │   ├── provider.py
│       │   ├── observability.py
│       │   ├── media.py
│       │   └── webmcp.py
│       ├── orchestration/
│       ├── elite_team/
│       │   ├── intelligence/
│       │   ├── architect/
│       │   ├── engineering/
│       │   ├── reviewer/
│       │   ├── optimizer/
│       │   └── maintenance/
│       ├── owner/
│       ├── personal/
│       ├── intelligence/
│       │   └── media/
│       │       ├── intake/
│       │       ├── normalize/
│       │       ├── transcript/
│       │       ├── segmentation/
│       │       ├── extraction/
│       │       └── gap_detection/
│       ├── context/
│       ├── evidence/
│       ├── knowledge/
│       ├── memory/
│       ├── capabilities/
│       │   ├── registry/
│       │   ├── resolver/
│       │   ├── providers/
│       │   │   └── webmcp/
│       │   ├── fingerprints/
│       │   ├── overlap/
│       │   ├── lifecycle/
│       │   ├── profiles/
│       │   ├── generations/
│       │   └── pinning/
│       ├── capability_factory/
│       │   ├── discover/
│       │   ├── provenance/
│       │   ├── licensing/
│       │   ├── security/
│       │   ├── inspect/
│       │   ├── extract/
│       │   ├── normalize/
│       │   ├── overlap/
│       │   ├── package/
│       │   ├── sandbox/
│       │   ├── evaluate/
│       │   └── promote/
│       ├── skills/
│       ├── tools/
│       ├── mcp/
│       │   ├── gateway/
│       │   ├── registry/
│       │   ├── clients/
│       │   ├── policy/
│       │   └── receipts/
│       ├── models/
│       │   ├── providers/
│       │   └── profiles/
│       ├── repositories/
│       ├── integrations/
│       │   ├── media/
│       │   │   └── youtube/
│       │   │       ├── resolver/
│       │   │       ├── metadata/
│       │   │       ├── captions/
│       │   │       └── client/
│       │   ├── speech/
│       │   │   ├── stt/
│       │   │   └── tts/
│       │   ├── browser/
│       │   │   └── webmcp/
│       │   │       ├── discovery/
│       │   │       ├── session/
│       │   │       ├── invocation/
│       │   │       ├── normalization/
│       │   │       └── receipts/
│       │   ├── personal/
│       │   └── external_services/
│       ├── execution/
│       │   ├── repo_reader/
│       │   ├── worktree/
│       │   ├── git/
│       │   ├── github/
│       │   ├── browser/
│       │   │   └── fallback/
│       │   └── receipts/
│       ├── evaluation/
│       ├── learning/
│       ├── ree/
│       ├── security/
│       ├── persistence/
│       └── observability/
├── apps/
│   └── owner-console/
│       ├── app/
│       ├── components/
│       ├── features/
│       │   ├── command/
│       │   ├── projects/
│       │   ├── runs/
│       │   ├── approvals/
│       │   ├── artifacts/
│       │   ├── knowledge/
│       │   ├── memory/
│       │   ├── capabilities/
│       │   ├── skills/
│       │   ├── models/
│       │   ├── voice/
│       │   ├── browser/
│       │   └── system/
│       ├── hooks/
│       ├── lib/
│       └── generated/
├── skills/
│   └── webmcp/
│       ├── SKILL.md
│       ├── references/
│       │   ├── spec-canon.md
│       │   ├── consumer.md
│       │   ├── authoring.md
│       │   ├── security.md
│       │   ├── compatibility.md
│       │   └── evaluation.md
│       └── procedures/
│           ├── retrofit.md
│           ├── verify.md
│           └── fallback.md
├── knowledge/
├── configs/
├── evals/
├── db/
├── integrations/
├── tests/
├── docs/
├── scripts/
└── infra/
~~~

## Ownership constraints

1. `control/` owns task/workflow state, authority, policy, admission and
   termination. Capability Fabric (`capabilities/`) owns provider/capability
   lifecycle under Kernel admission; these are distinct lifecycle domains.
2. `orchestration/` composes work through `control/`; it is not a second
   authority chain.
3. `sentient/model_gateway/` is the cognitive-facing model gateway;
   `models/providers/` contains concrete model providers and `models/profiles/`
   contains technical model-family capability/quirk facts. Neither profile nor
   provider metadata grants authority.
4. `mcp/` is backend/service MCP. `integrations/browser/webmcp/` is browser
   WebMCP. They are complementary and must not be collapsed.
5. `capabilities/providers/webmcp/` represents discovered/qualified providers;
   it does not execute the browser.
6. Browser fallback is separate from native WebMCP and reports a distinct
   execution class.
7. Root `/integrations/`, if used, is operational/config/deployment glue;
   runtime Python adapters belong under `src/wolf15_sentient/integrations/`.
8. Future folders appear only with their owning checkpoint and README contract.
9. CP4 uses a bounded native fixed read-only profile with Kernel admission
   before browser invocation; CP5 owns the general dynamic registry/resolver.
10. Donor package/code/skill/runtime imports require CP6 qualification and
    separate admission. Connected/shadow qualification remains blocked pending
    its own approved design, containment and evidence path.

## Checkpoint-to-skeleton ownership

| CP | Primary target areas |
| --- | --- |
| CP0 | current foundation and architecture governance |
| CP1 | `sentient/model_gateway`, `models/providers`, `models/profiles`, reasoning/evidence contracts |
| CP2 | `repositories`, `execution/repo_reader`, `context`, `evidence` |
| CP3 | `persistence`, `observability`, `security`, `api`, portions of `control`, generic receipts/recovery |
| CP4 | `owner`, `personal`, `intelligence/media`, `integrations/media`, `integrations/speech`, `integrations/browser/webmcp`, Owner Console voice/browser surfaces |
| CP5 | `capabilities`, `skills`, `tools`, `mcp`, `models`, WebMCP provider representation |
| CP6 | `capability_factory`, `evaluation`, WebMCP donor/security qualification |
| CP7 | `execution`, approvals/idempotency, Git/GitHub and consequential browser actions |
| CP8 | `learning`, `ree`, `evaluation`, mature cognition and memory |
| CP9 | integrated checkpoint-proven product; no authority shortcut |

## Current-to-target migration

~~~text
reasoning/      -> sentient/
cognition/      -> sentient/cognition/
agents/         -> elite_team/
orchestration task/workflow state and authority -> control/
provider/capability lifecycle -> capabilities/ under Kernel admission
~~~

No migration is authorized by this skeleton alone.
