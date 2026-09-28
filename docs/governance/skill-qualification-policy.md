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
4. **Exact-byte evaluation:** private evidence is evaluated with a separately
   qualified `$evaluate-agent-skill` and immutable `common-skill/v1` profile.
   The receipt must bind the subject, evaluator, profile, collector, evidence,
   and environment identities below. The evaluator consumes evidence; it does
   not run tests or scanners on behalf of the collector. A valid `PASS_LOCAL`
   applies only to those bound bytes, environment, and scope.
5. **Scoped admission:** an owner or authorized policy decision records the
   allowed task, environment, authority, dependencies, expiry, and revocation
   path. The package author does not approve their own package.
6. **Installation or activation:** only the separately authorized target is
   changed. Workbench use does not install a Sentient runtime capability.

## Required evaluation receipt bindings

| Component | Required identity in the receipt |
| --- | --- |
| Subject | Candidate package revision and `subject_tree_digest` of the full package |
| Evaluator | Evaluator package revision and `evaluator_tree_digest` of its full package |
| Profile | `common-skill/v1` plus digest of the immutable profile artifact actually used |
| Collector | Exact collector `id@version` that produced the evidence |
| Evidence | Shared `run_id`, digest of the collected evidence bundle, and environment identity including relevant host/runtime/dependency versions |

All bindings must refer to the same evaluation run. A matching subject and
evidence bundle is insufficient if the evaluator or profile changes. A missing
or mismatched binding blocks `PASS_LOCAL`; record `NOT_EXECUTED` or
`NOT_MEASURED` as appropriate until the missing component is verified. This
table defines required fields, not an assertion that receipts or digests have
already been collected for any SK-01 candidate.

## Bootstrap of the first evaluator

The evaluator is itself a `DESIGN_CANDIDATE_ONLY` in SK-01. It cannot grant its
own first qualification. Establish a limited external trust root first:

1. An independent reviewer inventories and pins the evaluator's complete
   package revision/tree digest, the exact profile artifact and digest, its
   dependencies, and the intended offline environment.
2. A separate test harness exercises fixed positive, negative, malformed,
   stale, forged-binding, and failure fixtures with independently specified
   expected verdicts. It records actual outputs and side effects; the
   evaluator does not manufacture its own evidence or expected results.
3. An owner or authorized policy decision reviews those receipts and grants
   narrowly scoped offline evaluator use at the pinned identities. This is a
   bootstrap admission for evaluation only, not product activation or
   permission to install packages, merge, deploy, or mutate external systems.
4. Only then may the pinned evaluator assess other candidates from separately
   collected evidence under the receipt bindings above. A new evaluator or
   profile version returns to independent bootstrap review; it cannot approve
   itself or silently inherit the old verdict.

If the external review, fixtures, profile, collector, or scoped authorization
cannot be verified, the bootstrap remains `NOT_EXECUTED` or `NOT_MEASURED` and
no candidate receives `PASS_LOCAL` through this path.

| Gate | Required evidence before promotion |
| --- | --- |
| G0 — host inventory | Actual active, inactive, aliased, and shadowed packages and host version |
| G1 — package identity | Full package bytes, tree digest, revision, and source provenance |
| G2 — structure | Valid entrypoint, required helpers, and available dependencies |
| G3 — authority and privacy | No authority from donor text; secrets and personal data stay within scope |
| G4 — behavior | Positive, negative, timeout, cancellation, and failure outcomes |
| G5 — function | Contract fit and ownership boundaries against the target task |
| G6 — contribution | Fixed-task comparison for quality, latency, cost, and resource use |
| G7 — evaluator | Fresh result with subject, evaluator, immutable profile, exact collector, evidence, and environment bindings above |
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
