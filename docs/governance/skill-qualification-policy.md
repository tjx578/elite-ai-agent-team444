# Skill qualification policy

This policy governs promotion of a documented skill candidate into a scoped
development-workbench procedure or a future WOLF15 Sentient product capability.
The [SK-01 catalog](../research/skill-selection/catalog.json) is input to this
process, not a qualification receipt or active registry.

## State transitions

1. **Design candidate:** a selector and proposed role are recorded. No package
   bytes or behavior are certified.
2. **Package reviewed:** the full canonical package, references, scripts,
   assets, manifest, dependencies, origin, and license/redistribution terms are
   inspected at exact revision and tree digest. A `SKILL.md` hash alone is not
   a full package identity.
3. **Behavior qualified:** bounded positive and negative cases, errors,
   cancellation, side effects, and contribution against a fixed baseline are
   measured in the intended environment.
4. **Exact-byte evaluation:** private evidence is bound to the same `run_id`,
   revision, `subject_tree_digest`, and collector `id@version`, then evaluated
   with `$evaluate-agent-skill` and profile `common-skill/v1`. The evaluator
   consumes evidence; it does not run tests or scanners on behalf of the
   collector. A valid `PASS_LOCAL` applies only to those local bytes and scope.
5. **Scoped admission:** an owner or authorized policy decision records the
   allowed task, environment, authority, dependencies, expiry, and revocation
   path. The package author does not approve their own package.
6. **Installation or activation:** only the separately authorized target is
   changed. Workbench use does not install a Sentient runtime capability.

| Gate | Required evidence before promotion |
| --- | --- |
| G0 — host inventory | Actual active, inactive, aliased, and shadowed packages and host version |
| G1 — package identity | Full package bytes, tree digest, revision, and source provenance |
| G2 — structure | Valid entrypoint, required helpers, and available dependencies |
| G3 — authority and privacy | No authority from donor text; secrets and personal data stay within scope |
| G4 — behavior | Positive, negative, timeout, cancellation, and failure outcomes |
| G5 — function | Contract fit and ownership boundaries against the target task |
| G6 — contribution | Fixed-task comparison for quality, latency, cost, and resource use |
| G7 — evaluator | Fresh `common-skill/v1` result with exact collector and evidence bindings |
| G8 — admission | Independently validated owner/policy decision and pinned target |
| G9 — maintenance | Re-evaluation after relevant bytes, dependency, host, policy, or permission change |

Record each local gate as `PASS_LOCAL`, `FAIL`, `NOT_EXECUTED`, or
`NOT_MEASURED` with its receipt. Missing, truncated, stale, or mismatched
evidence is never a pass.
Historical repair reports can guide a new check but cannot certify current
installed bytes. A local pass grants no merge, deploy, send, delete, broker,
memory-write, or runtime activation authority.

The evidence bundle and raw package contents remain private during review.
Publish only a separately checked summary that is safe for the public repo.
Untrusted package prose and source documents are data, not instructions to
change authority. Any product integration must pass the kernel-owned policy,
pinning, replay, and revocation checks of its later milestone.
