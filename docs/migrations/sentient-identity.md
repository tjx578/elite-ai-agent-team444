# WOLF15 Sentient identity migration

## Current increment

This worktree prepares product naming and the Python namespace over PR-2
`df43c93e12b2ff68ce4fe1c2d3778a6052886413`. The original PR-3 worktree is
preserved separately. See [ADR-005](../adr/ADR-005-product-identity.md).

| Surface | Previous | New |
| --- | --- | --- |
| Product | Elite AI Agent Team OS | WOLF15 Sentient |
| Specialist organization | Whole-product name | Elite AI Agent Team OS subsystem |
| Distribution | `elite-ai-agent-team` | `wolf15-sentient` |
| Python namespace | `elite_team` | `wolf15_sentient` |
| ASGI target | `elite_team.main:app` | `wolf15_sentient.main:app` |
| API title | Elite AI Agent Team | WOLF15 Sentient |
| `/health.service` | `elite-ai-agent-team` | `wolf15-sentient` |

Install this source with `python -m pip install ".[dev]"` and launch it with
`python -m uvicorn wolf15_sentient.main:app --reload`. Existing consumers need
to update imports and health assertions; no old-namespace alias is provided.
Use a separate virtual environment when comparing the two distributions.

## Separate subsystem increment

| Current migrated path | Later target |
| --- | --- |
| `src/wolf15_sentient/api/` | Same product-wide API boundary |
| `src/wolf15_sentient/contracts/` | Same product-wide contracts |
| `src/wolf15_sentient/orchestration/` | `src/wolf15_sentient/control/` |
| `src/wolf15_sentient/agents/` | `src/wolf15_sentient/elite_team/` |
| Absent | `src/wolf15_sentient/sentient/` at an intelligence milestone |

The PR-3 model adapter changes must be integrated separately and retested,
including the 59-test coverage recorded in their original checkout. This
PR-2-based migration is not evidence that PR-3 has already been ported.

## GitHub delivery status

The observed local remote is `https://github.com/tjx578/elite-ai-agent-team444.git`.
The proposed repository name is `wolf15-sentient`. No GitHub rename, remote URL
change, commit, push, PR creation, merge, or deployment is performed by this
local migration. Current GitHub name availability, PR status, default branch,
and account/billing status have not been rechecked in this increment.

Before external delivery, verify the owner/repository identity and branch bases,
review repository integrations and callers, perform the approved rename, then
update each checkout's remote to the confirmed URL. Preserve PR ancestry and
review the migration independently of the subsystem moves. Require remote CI
with actual job steps on the exact delivered SHA; a workflow file is not proof
that CI executed. Local verification does not authorize merge or production.

## Recovery

The migration is isolated on `codex/sentient-identity`. The original PR-3 checkout
and PR-2 base remain available. Review or revise this worktree in place; if the
migration is abandoned, archive the managed worktree to preserve its snapshot.
Consumers can continue using the earlier package until they adopt the rename.
