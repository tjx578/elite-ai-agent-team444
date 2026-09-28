# WOLF15 Sentient identity migration

## Completed identity migration

The original migration was prepared over PR-2 commit
`df43c93e12b2ff68ce4fe1c2d3778a6052886413`. PR #1–#4 are now merged into
the canonical [tjx578/wolf15-sentient](https://github.com/tjx578/wolf15-sentient)
repository. The original PR-3 model-adapter worktree remains separate. See
[ADR-005](../adr/ADR-005-product-identity.md).

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

The repository was renamed to `tjx578/wolf15-sentient`. The canonical remote
is `https://github.com/tjx578/wolf15-sentient.git`; the former repository slug
is legacy. PR #1–#4 remained intact and merged in order. The resulting `main`
commit `64ae79f1b1bd1924d8402bc45d74dc2133f8b37e` passed the
[final CI run](https://github.com/tjx578/wolf15-sentient/actions/runs/36372815613):
56 tests plus installed identity checks on Python 3.11, 3.12, and 3.13.
No deployment or production mutation was performed.

## Recovery

The historical `codex/sentient-identity` branch and original PR-3 model-adapter
checkout remain available. Future corrections to the merged migration should
use a new reviewed PR. Consumers of the old package must adopt the new import,
distribution, entrypoint, and health identity together.
