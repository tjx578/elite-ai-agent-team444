# Skill adoption plan

SK-01 versions a historical selection result so development can prioritize
package review now. It creates no loader, registry, connector, or active skill
inside WOLF15 Sentient. The [catalog](../research/skill-selection/catalog.json)
is documentation; the [qualification policy](../governance/skill-qualification-policy.md)
controls what evidence is needed before a package can be used in a scope.

| Lane | Earliest use | Required boundary |
| --- | --- | --- |
| Development workbench | M2–M5 tasks, one package at a time after qualification | Codex may use an admitted procedure to help build or review source; the procedure gains no product authority |
| Product capability | Directed read-only patterns at M6; governed registry at M7 | Versioned contract, pinned resolver, denial/replay tests, consent and kernel policy |
| Capability Foundry | M8 | Donor provenance, isolation, overlap comparison, offline/shadow evaluation and independent admission |
| Learning and REE | M10 | Verified episodes and fixed-rubric evaluation; no self-promotion |

The first review batch is `agent-scout-explorer`, `agent-specification`,
`retrieval-knowledge-structurer`, `agent-planner`, `agent-coder`,
`agent-tester`, `agent-reviewer`, and `verification-quality`. Review the
packages needed by the next task first; the other 212 selectors remain
documented candidates. A task can proceed with repository tools if a candidate
has not qualified. Its contribution must not be reported as proven.

For overlapping selectors, compare contract and behavior before aliasing or
replacement. A similar name is not equivalence. Provider choice must follow
the task and available evidence. The owner area in the catalog is a proposed
work assignment, not an implemented six-division or 28-specialist roster.

Milestones in the [canonical roadmap](roadmap.md) stay in order. M2's initial
pure evidence/context evaluator merged in PR #11; SK-01 does not wire it to a
skill loader. M3 model adapters, M4 repository intelligence, and M5 service
hardening remain separate implementation work. M6 read-only personal briefs
do not grant send/write permission. M7 is the first governed runtime skill
registry; M8 and M10 have their own evidence and approval gates.
