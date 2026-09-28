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
   a full package identity. Record whether ownership, license, or explicit
   permission allows the requested use, including execution, copying,
   modification, and redistribution where applicable. Merely reading terms is
   not a rights pass.
3. **Behavior qualified:** bounded positive and negative cases, errors,
   cancellation, side effects, and contribution against a fixed baseline are
   measured in the intended environment. Pin the workload, expected outcomes,
   harness, baseline implementation, and baseline configuration used for those
   measurements. Run unadmitted candidate code, the evaluator, harness, and
   collector only inside a disposable, filesystem-contained offline sandbox with
   no host credentials or host network access, no external network egress,
   read-only source mounts, and writable scratch outside the repository. Use
   only in-sandbox fixtures for network-dependent cases. Before executing any
   candidate, evaluator, harness, or collector code, enforce scope-approved
   limits on process count, CPU, memory, scratch storage, and wall time, with
   termination on breach. Missing or unenforceable limits block execution.
   This version supports offline qualification only; connected or shadow
   qualification is unsupported and blocked until a separately authorized
   design, containment model, evidence profile, and evaluation path are
   approved. Record actual side effects. If containment cannot be established,
   behavior qualification is `NOT_EXECUTED`. Never fall back to direct
   developer or workbench host
   execution.
4. **Exact-byte evaluation:** private evidence is evaluated with a separately
   qualified `$evaluate-agent-skill` and immutable `common-skill/v1` profile.
   The authenticated receipt must bind the subject, evaluator, profile,
   collector, evidence, environment, evaluated scope, and qualification policy
   identities below. The evaluator consumes evidence; it does not run tests or
   scanners on behalf of the collector. A valid `PASS_LOCAL` applies only to
   those bound bytes, environment, scope, and policy.
5. **Scoped admission:** an immutable, authenticated owner or authorized policy
   decision records the allowed task, environment, authority, dependencies,
   expiry, and revocation
   path. It must cite a qualification receipt whose evaluated scope and
   authority match the requested admission scope and whose bound environment
   matches the target host/runtime, installed artifacts, and data/egress
   boundary. It must confirm a compatible rights outcome for that exact use,
   verify the receipt's issuer, verdict, bindings, and policy revision against
   an independently controlled attestation or trusted append-only record, and
   set admission expiry no later than receipt expiry. A task outside the
   evaluated task class or permitted operations, side effects, authority, or
   data/egress boundary needs new evaluation. So does a change to the pinned
   qualification corpus, expected outcomes, environment, policy, dependency,
   harness, baseline, or executable artifact. A new real-task input within
   the admitted class and boundaries does not itself change the qualification
   workload or require re-evaluation. The package author does not approve
   their own package.
6. **Installation or activation:** only the separately authorized target is
   changed. Workbench use does not install a Sentient runtime capability.

## Required evaluation receipt bindings

| Component | Required identity in the receipt |
| --- | --- |
| Subject | Candidate package revision and `subject_tree_digest` of the full package; if built or installed before execution, exact built artifact and installed-tree digests plus build recipe, configuration, and toolchain identities |
| Evaluator | Evaluator package revision and `evaluator_tree_digest` of its full package; if built or installed before execution, exact built artifact and installed-tree digests plus build provenance |
| Profile | `common-skill/v1` plus digest of the immutable profile artifact actually used |
| Qualification policy | Immutable policy revision and digest of the full policy artifact applied to this run |
| Collector | Exact collector `id@version`, immutable implementation revision, full-package tree digest, and exact built/installed artifact digests with build provenance when applicable; for a non-Git distribution, use an equivalent immutable artifact identity and digest, never a fabricated Git SHA |
| Dependencies | Digest of the resolved dependency lock or manifest and content digests of every installed direct and transitive dependency artifact used by the subject, evaluator, collector, harness, or baseline implementation, including platform-specific artifacts; versions alone are insufficient |
| Workload and baseline | Immutable revision and digest of the task/benchmark corpus, expected outcomes, test harness, baseline implementation, and baseline configuration used for behavior and contribution checks |
| Evidence | Shared `run_id`, digest of the collected evidence bundle, and environment identity including relevant host/runtime/platform versions and runtime or host-image artifact digests where applicable |
| Evaluated scope | Versioned, immutable scope artifact and its digest, naming task class, permitted operations and side effects, authority level, relevant data/egress boundary, and an owner-approved maximum receipt age |
| Time and expiry | Trusted UTC `evaluated_at`, `issued_at`, and `expires_at` bound to the verdict; `evaluated_at` must not follow `issued_at`, and `expires_at` must follow `issued_at` and cannot exceed `evaluated_at` plus the approved maximum receipt age |
| Receipt authenticity | Trusted issuer identity and either a verifiable attestation over the verdict and every binding above or a receipt ID in an independently controlled append-only store containing that same issuer, verdict, and bindings |

### Canonical digest format

Every digest above uses SHA-256 and is recorded as lowercase, 64-character
hexadecimal with an explicit `sha256:` prefix. A single-file artifact is
digested over its exact bytes. A multi-file package, installed dependency,
manifest, or evidence bundle uses `tree-v1`: hash the UTF-8 prefix
`skill-tree-v1` followed by a line-feed byte (`0x0A`), then one entry per source
entry sorted by the raw UTF-8 bytes of its normalized relative path. Each entry
is serialized as an unsigned 32-bit big-endian path-byte length, path bytes,
one-byte type (`1`
regular file, `2` symbolic link, `3` directory), unsigned 32-bit big-endian
canonical mode, unsigned 64-bit big-endian payload-byte length, and the 32 raw
bytes of SHA-256 over the payload. File payloads are exact file bytes; symbolic
link payloads are exact link-target bytes without following the link; directory
payloads are empty. Include empty directories. The only canonical mode values
are `0o100644` for a regular non-executable file, `0o100755` for an executable
file, `0o040755` for a directory, and `0o120000` for a symbolic link. Convert
Git `100644`, `100755`, `040000`, and `120000` to those values respectively.
For archives, require an explicit Unix entry type and permission bits: accept
only `0644` or `0755` for regular files and `0755` for directories; map a
symbolic-link entry to `0o120000` and bind its exact target bytes. Reject
special bits, other modes, missing mode metadata, and unsupported entry types.
Never substitute the checking host's default permissions.
For an installed tree, also bind a security-metadata manifest by digest in the
receipt and verify canonical ownership and the absence of unapproved ACLs,
file capabilities, extended attributes, and other security-relevant metadata
before comparing identities. This manifest is part of each applicable
installed-artifact binding. The approved environment defines the canonical
owner and allowed security metadata; unverifiable or mismatched metadata
blocks qualification or admission even when `tree-v1` digests match.

Paths are nonempty, relative Unicode NFC strings with `/` separators. Reject
backslashes, drive prefixes, absolute paths, empty, `.` or `..` components,
repeated or trailing separators, invalid Unicode, and duplicate paths after
normalization. Also reject paths that alias under the intended target
filesystem's case-folding or path-equivalence rules; those rules are part of
the bound environment. Reject any path with an ancestor present as a
non-directory entry (for example, file `bin` alongside `bin/tool`). Reject
symbolic links that escape the package root
when resolved. The producer and verifier reject the same invalid tree rather
than letting an extractor choose which entry wins.

The receipt names `tree-v1` for every tree digest and records the immutable
revision separately from the content digest. A Git commit or Git tree ID alone
is not a `tree-v1` digest. For a single-file manifest, hash its exact bytes;
for a multi-file manifest, use `tree-v1`. Producer and verifier independently
recompute and compare the same typed digest before accepting a binding. An
unknown algorithm, encoding, or serialization version blocks `PASS_LOCAL`.

### Authenticated receipt representation

`skill-qualification-receipt/v1` is a UTF-8 JSON object with exactly five
top-level keys: `schema_version`, `schema_digest`, `verdict`, `issuer_id`, and
`bindings`. `verdict` is exactly one of `PASS_LOCAL`, `FAIL`, `NOT_EXECUTED`, or
`NOT_MEASURED`. The `bindings` object has exactly one key for each receipt row
above except Receipt authenticity: `subject`, `evaluator`, `profile`,
`qualification_policy`, `collector`, `dependencies`, `workload_baseline`,
`evidence`, `evaluated_scope`, and `time_expiry`. Each value follows a separately
pinned, immutable nested-field schema whose SHA-256 digest is `schema_digest`;
the verifier must match that digest to the owner-approved schema for this
version. Until that schema and its independent parser tests exist, no receipt
may pass.
All identity, digest, and timestamp fields are strings; UTC timestamps use the
single form `YYYY-MM-DDTHH:MM:SSZ`. Arrays of artifact identities are sorted by
their canonical serialized bytes and contain no duplicates. Reject missing,
unknown, or duplicate keys at any level, non-NFC strings, non-canonical digest
or timestamp text, and JSON numbers in receipt identity fields.
Reject non-NFC strings before JCS serialization; do not silently normalize
strings, because JCS preserves their Unicode content.

Serialize the complete payload with [RFC 8785 JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785.html)
(JCS), then attest those exact UTF-8 bytes with an independently trusted issuer
key and approved signature algorithm. The signature envelope is outside the
payload and identifies the key and algorithm. The verifier strictly parses the
payload, checks its versioned schema and all bindings, reserializes it with JCS,
requires byte-for-byte equality, and only then verifies the signature and
issuer trust. For the append-only alternative, the trusted store must retain
those same canonical payload bytes under a stable receipt ID and authenticate
the issuer. A valid signature over non-canonical or ambiguous bytes is not an
admissible receipt.

All bindings must refer to the same evaluation run. Any artifact, input,
configuration, or installed dependency that can change the measured behavior,
expected result, or verdict needs an immutable identity and content digest in
the receipt or in a digest-bound manifest. A matching subject and evidence
bundle is insufficient if the evaluator, profile, policy, dependency artifacts,
workload, harness, or baseline changes. A missing or mismatched binding,
unverifiable receipt origin, or untrusted time also blocks `PASS_LOCAL`; record
`NOT_EXECUTED` or `NOT_MEASURED` as appropriate until verified. The collector's
digest identifies its bytes; independent review and behavior tests are still
needed to establish that it produces valid evidence. A candidate author's
self-reported verdict or receipt is not authenticated evidence. This table
defines required fields, not an assertion that receipts or digests have already
been collected for any SK-01 candidate.

A qualification receipt does not grant authority. `PASS_LOCAL` for one scope
cannot be reused as a pass for another scope or a more privileged operation.
Admission requires a separate immutable decision artifact authenticated by an
owner-approved signature or an independently controlled, append-only trusted
record. It binds the decision issuer, referenced receipt ID and canonical
payload digest, exact admitted scope artifact and digest, task class,
operations, side effects, authority, target environment and installed
artifacts, dependency and data/egress boundary, rights outcome, issued time,
expiry, and revocation reference. The verifier authenticates that artifact
and checks every authority-bearing field against the requested use; mutable
prose or a mere citation of a valid receipt cannot authorize admission.
Admission must compare the requested scope artifact and digest with the
evaluated scope in the receipt, verify the attestation or trusted record, and
match the policy revision and digest in force for admission before separately
authorizing any allowed effects. It must compare the bound host/runtime,
installed subject/evaluator/collector and dependency artifacts and
data/egress boundary with the target environment. It must separately compare
the receipt's pinned qualification corpus with the approved evaluation
record, not with the new real-task input. A mismatch needs a new
evaluation in a contained replica of that target; an offline-only receipt
cannot admit connected or more privileged use. Using a trusted clock, admission
must check that evaluation and issuance are not in the future and the receipt
has not expired. The admission expiry must be no later than receipt expiry;
an admitted procedure becomes invalid when its receipt expires and needs a new
receipt and admission review before further use. Missing or invalid timestamps
or an unapproved freshness limit block admission. A policy change requires a
new evaluation receipt before new admission under that policy.

## Rights gate for the requested use

The rights decision is specific to the package bytes and admission scope:

| Evidence outcome | Gate result | Admission |
| --- | --- | --- |
| Ownership, license, or explicit permission is verified and compatible with the requested use | `PASS_LOCAL` for the rights check | May proceed only if all other gates pass |
| Ownership, license, or permission cannot be established | `NOT_MEASURED` | Blocked |
| Terms or ownership are verified incompatible with the requested use | `FAIL` | Blocked |

This applies to development-workbench use and later product use; a workbench
pass does not imply redistribution or runtime rights. It is consistent with
the [Capability Foundry boundary](../architecture/capability-foundry.md), where
unknown license or provenance blocks adoption. This gate does not choose an
open-source license for the WOLF15 Sentient repository.

## Bootstrap of the first evaluator

The evaluator is itself a `DESIGN_CANDIDATE_ONLY` in SK-01. It cannot grant its
own first qualification. Establish a limited external trust root first:

1. An independent reviewer inventories and pins the evaluator's complete
   package revision/tree digest, the exact profile artifact and digest, its
   dependencies, the qualification policy revision and digest, the collector's
   immutable implementation identity and full package digest, the intended
   offline environment and scope, the dependency artifacts, the fixed fixture
   and baseline artifacts, the approved freshness limit, compatible rights for
   that scope, the `tree-v1` digest procedure and receipt-v1 schema/parser,
   disposable offline sandbox, and independently controlled receipt issuer,
   trusted clock, and attestation or append-only record mechanism.
2. An owner grants a one-time, narrowly bounded permission to execute only the
   pinned evaluator, collector, and harness inside that sandbox for bootstrap
   tests. This is not a qualification pass or permission for host or product
   use.
3. A separate test harness exercises fixed positive, negative, malformed,
   stale, forged-binding, and failure fixtures with independently specified
   expected verdicts. It also rejects non-canonical trees, duplicate receipt
   keys, altered signed bytes, expired receipts, and environment mismatches.
   It records actual outputs and side effects and binds the resulting verdict
   and all receipt identities through the trusted mechanism; the evaluator
   does not manufacture its own evidence or expected results.
4. An owner or authorized policy decision reviews those receipts and grants
   narrowly scoped offline evaluator use at the pinned identities. This is a
   bootstrap admission for evaluation only, not product activation or
   permission to install packages, merge, deploy, or mutate external systems.
5. Only then may the pinned evaluator assess other candidates from separately
   collected evidence under the receipt bindings above. A new evaluator or
   profile version returns to independent bootstrap review; it cannot approve
   itself or silently inherit the old verdict.

If the external review, fixtures, profile, collector, policy identity, digest
procedure, sandbox containment, receipt authenticity, or scoped authorization
cannot be verified, the bootstrap remains `NOT_EXECUTED` or `NOT_MEASURED` and
no candidate receives `PASS_LOCAL` through this path.

| Gate | Required evidence before promotion |
| --- | --- |
| G0 — host inventory | Actual active, inactive, aliased, and shadowed packages and host version |
| G1 — package identity | Full package bytes, canonical `tree-v1` digest, revision, and source provenance |
| G2 — structure and rights | Valid entrypoint, required helpers and dependencies, plus a compatible rights result for the requested use |
| G3 — authority and privacy | No authority from donor text; unadmitted code and collection stay in a disposable offline sandbox without host credentials, host network access, external egress, or repository writes, with enforced process, CPU, memory, scratch-storage, and wall-time limits; secrets and personal data stay within scope |
| G4 — behavior | Positive, negative, timeout, cancellation, and failure outcomes on pinned fixture and harness bytes, with sandbox containment and side effects recorded; connected qualification remains blocked pending a separate authorized path |
| G5 — function | Contract fit and ownership boundaries against the target task |
| G6 — contribution | Fixed-task comparison for quality, latency, cost, and resource use against pinned corpus, expected outcomes, baseline implementation, and configuration |
| G7 — evaluator | Fresh, authenticated receipt-v1 result with canonical signed payload and digests for subject, evaluator, immutable profile, qualification policy, collector implementation, built/installed artifacts and their security metadata, dependencies including baseline closure, qualification corpus, baseline, evidence, environment, evaluated scope, and time/expiry bindings above |
| G8 — admission | Authenticated immutable owner/policy decision binding every authority-bearing field and the receipt; verified receipt issuer and verdict, current policy identity, exact scope, authority, environment, installed-artifact and security-metadata, dependency, and pinned qualification-corpus match to receipt, compatible rights, and admission expiry no later than receipt expiry |
| G9 — maintenance | Re-evaluation and a new authenticated receipt after relevant source, built/installed artifact or security metadata, dependency, qualification corpus, harness, baseline, host, policy, or permission change, or receipt expiry; an in-scope new real-task input alone does not trigger re-evaluation |

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
