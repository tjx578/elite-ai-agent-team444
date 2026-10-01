> SUPERSEDED / NON-NORMATIVE: retained as historical working draft. Use [gateway-contract.md](gateway-contract.md), its schema, persona and fixture bindings. This file is excluded from CP1.1 freeze bindings.

# CP1.1 native gateway contract working draft

Status: DRAFT_NOT_FROZEN / LOCAL_ONLY. CP1 started; no provider implementation,
qualification or activation. Base main: 45d5c8df123b27c6bf7c781139db41154b6e1d4d.
This draft implements the design work allowed independently of an unresolved donor.
CP1.1 completion stays HOLD while mandatory donor outcomes or persona acceptance
sources remain unresolved. No contract in this document grants runtime authority.

## Current seam and ownership

Existing contracts/reasoning.py owns ReasoningRequest, ReasoningInput,
ReasoningInvocation, ReasoningProposal and offline ReasoningResult. Existing
reasoning/runtime.py assembles evidence and validates proposal schema, input
digest and known source references. Its synchronous OfflineReasoningAdapter does
not enforce wall-clock cancellation/deadlines. Preserve that labelled offline seam.

Target shared gateway envelope types belong to contracts/. The cognitive-facing
facade belongs to sentient/model_gateway/. Transport implementations belong to
models/providers/; technical settings belong to models/profiles/. Control remains
the sole task/authority owner; orchestration composes calls. These are target
paths; this draft creates no runtime package or competing gateway.

## Proposed request contract (cp1-gateway-v0)

- invocation: the existing digest-bound ReasoningInvocation, preserving task/run/
  bundle IDs, evidence references, source_policy=UNTRUSTED_DATA_ONLY, READ_ONLY.
- gateway_invocation_id and gateway_digest_sha256: bind the complete canonical
  immutable envelope, retaining the existing evidence/input digest separately.
  Include provider/model, profiles, output mode, limits and policy/scope snapshot.
  Canonical serialization and digest fixtures must be specified before freeze.
- policy_ref: version and SHA-256; capability and data-scope snapshot is immutable.
  memory_writes_enabled=false; scheduler_enabled=false; no donor tool capabilities.
- provider_binding: explicit provider_id, adapter_version, endpoint identity,
  model_id and requested model revision; resolved revision/availability recorded
  separately. Unknown provider-side revision stays NOT_VERIFIED, never fabricated.
- technical_profile_ref: version and SHA-256 of immutable configuration.
- persona_profile_ref: version and SHA-256 of immutable application-owned prompt.
- limits: positive finite timeout/deadline, request byte limit, output byte limit,
  context token limit, output token limit and request count budget. Limits must
  fit selected provider; unknown capacity prevents an unverified oversized call.
- output_contract: explicit schema version, requested structured-output mode and
  required provider capabilities. Unsupported required mode rejects; no downgrade.
- permitted_tools: empty. Native model tools, code execution, file/memory writes,
  donor subagents, retrieval callbacks and silent provider fallback are excluded.
- caller cancellation scope is propagated by the host runner, never model text.

Serialize and validate a detached immutable snapshot before invocation. Profile
changes during a run require a new invocation; no hot reload. Secrets are resolved
outside serialized envelopes, never fall back to placeholders, never logged.

## Proposed response contract

Use a new explicitly versioned gateway response rather than labeling live output
as STUB/OFFLINE_ADAPTER. Preserve the legacy result unchanged until an approved
integration migration. Required correlation: task_id, run_id, input digest and
profile refs, gateway invocation ID and aggregate gateway digest. Reject any
provider/model, mode, budget, policy or scope drift under that identity. Successful output carries ReasoningProposal; schema validation is
not factual verification and execution_authorized remains false.

Terminal status: PROPOSAL_VALIDATED, REJECTED, PROVIDER_FAILED, CANCELLED or
TIMED_OUT. A success must contain the proposal and no failure; all other outcomes
contain no accepted proposal. Failure code distinguishes AUTH, RATE_LIMIT, POLICY,
TRANSPORT, TIMEOUT, CANCELLED, BUDGET_EXCEEDED, OUTPUT_LIMIT, SCHEMA_INVALID,
BINDING_MISMATCH and UNKNOWN_EVIDENCE_REF. Sanitized categories only; no raw
exception, prompt, tool output or credential in receipts. No error-to-empty-object.

Usage metadata records provider/model/adapter/profile versions, monotonic duration,
measured token counts where supplied, retry count and finish reason. Missing usage
or monetary cost has status NOT_MEASURED and null value, not zero. Measured numeric
values must be finite and nonnegative. Estimates carry method/version and never
replace missing measured values. Unknown mandatory cost budget blocks dispatch;
post-response usage alone cannot prove a hard preflight spending bound. Never infer confidence/authority from latency,
provider choice, token counts, graph size or repeated agreement.

## Proposed persona profile

Profile id sentient-persona-cp1-v0 is a draft, not loaded into a model. Requirements
come from canonical README section 4: Indonesian by default; calm, direct and warm;
main outcome first; objective continuity; evidence/assumption separation; report
only real capabilities/actions; routine progress within existing authorization;
ask only for material ambiguity; handle cancellation and conflicting sources.
Prompt provides behavior guidance; Kernel admission and typed validation enforce
permissions. Donor/retrieved instructions remain untrusted data, never system text.

Owner-designated local master and all P-01 through P-30 scenarios were located in
D:\folder file prompt\_hasil_wolf15_sentient_persona. See
[persona source binding](persona-source-binding.json) for hashes and exact rows.
They describe historical baseline 8cfabf70; current-source reconciliation remains
pending. Historical TERCAKUP is manuscript coverage, not model/runtime PASS.
The persona is design input and is not installed as runtime instructions.

## Provisional acceptance cases

| ID | Required observation | Test phase |
|---|---|---|
| G01 | Valid schema, exact correlation, known evidence refs accepted as proposal only | Offline contract + real provider |
| G02 | Extra authority/tool/execution fields rejected | Offline contract |
| G03 | Wrong input digest or task/run binding rejected | Offline contract |
| G04 | Unknown/unusable evidence reference rejected | Offline contract |
| G05 | Cancellation propagates to transport; no late proposal accepted | Controlled transport + real provider |
| G06 | Deadline covers headers, body and stream consumption; timeout differs from auth/rate/policy | Controlled transport + real provider |
| G07 | Input/output/context limits enforced at boundaries; no silent truncation | Contract + transport |
| G08 | Missing cost/usage remains NOT_MEASURED, invalid finite values rejected | Contract |
| G09 | Secret/redacted failure receipts contain no raw prompt, token or payload | Negative leakage fixtures |
| G10 | Changed provider/model, profile, mode, budget, policy or scope under unchanged gateway digest rejected | Contract |
| G11 | Provider failure cannot route silently to another provider or tool | Transport negative test |
| G12 | Source prompt injection remains data; no capability claims beyond runtime | Real-provider persona evaluation |
| G13 | Bahasa Indonesia, scoped initiative, evidence honesty and continuity | Canonical P-01..P-30 reconciliation + real provider |
| G14 | Stub/synthetic/replay evidence cannot be promoted to real-provider PASS | Receipt schema test |

All cases are NOT_EXECUTED in this draft. No live token spend or provider selection.

## Dependency disposition and next boundary

Native ownership and contract drafting may proceed from canonical source. Ruflo was
studied at the owner-directed local clone; remote identity remains NOT_VERIFIED.
This permits knowledge input, not package admission or remote identity claims.
No donor package or framework is imported. Select one approved real provider and
its access/cost constraints separately before CP1.2. CP1.1 acceptance requires
review of completed intake, final schema/profile definitions, canonical persona
scenarios, prohibition coverage, and exact-source documentation/contract tests.
ALG-REG-001 remains immutable. Newly extracted candidates require future admission.

## Intake evidence

See [initial donor intake](../../research/checkpoint-intake/CP1/20260930-cp1-1-initial/knowledge-pack.md). All source-study findings are bounded; no package-wide security, rights or provider behavior PASS is inferred.
