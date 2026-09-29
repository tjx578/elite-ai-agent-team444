# WOLF15 Sentient — Final Target Repository Skeleton

## Status

**Canonical target tree after merge; implementation remains checkpoint-gated.**

This document replaces the former external skeleton as the in-repository target
tree. It is a destination map, not proof that every folder exists. Future
subsystems and README contracts are created only when the owning checkpoint
implements them.

## Canonical tree

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
│       │   └── providers/
│       ├── repositories/
│       ├── integrations/
│       │   ├── browser/
│       │   │   ├── webmcp/
│       │   │   │   ├── discovery/
│       │   │   │   ├── session/
│       │   │   │   ├── invocation/
│       │   │   │   ├── normalization/
│       │   │   │   └── receipts/
│       │   │   └── fallback/
│       │   │       └── browser_automation/
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

1. `control/` is the only authority/policy/lifecycle owner.
2. `orchestration/` composes work through `control/`; it is not a second
   authority chain.
3. `sentient/model_gateway/` is the cognitive-facing model gateway;
   `models/providers/` contains concrete model providers.
4. `mcp/` is backend/service MCP. `integrations/browser/webmcp/` is browser
   WebMCP. They are complementary and must not be collapsed.
5. `capabilities/providers/webmcp/` represents discovered/qualified providers;
   it does not execute the browser.
6. Browser fallback is separate from native WebMCP and reports a distinct
   execution class.
7. Root `/integrations/`, if used, is operational/config/deployment glue;
   runtime Python adapters belong under `src/wolf15_sentient/integrations/`.
8. Future folders appear only with their owning checkpoint and README contract.

## Checkpoint-to-skeleton ownership

| CP | Primary target areas |
| --- | --- |
| CP0 | current foundation and architecture governance |
| CP1 | `sentient/model_gateway`, `models/providers`, reasoning/evidence contracts |
| CP2 | `repositories`, `execution/repo_reader`, `context`, `evidence` |
| CP3 | `persistence`, `observability`, `security`, `api`, portions of `control`, generic receipts/recovery |
| CP4 | `owner`, `personal`, `intelligence`, `integrations/browser/webmcp`, Owner Console browser/voice surfaces |
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
orchestration authority/lifecycle -> control/
~~~

No migration is authorized by this skeleton alone.
