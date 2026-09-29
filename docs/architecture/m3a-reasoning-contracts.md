# M3-A: task routing and evidence-bound offline proposals

## Scope and entry point

`wolf15_sentient.reasoning.run_reasoning` is an explicit library entry point.
It takes a `ReasoningRequest` and an optional trusted offline adapter. Existing
`/tasks`, foundation helpers, and the active LangGraph workflow are unchanged.
The HTTP endpoint still runs the deterministic engineering kernel; callers
use this new library entry point to exercise M3-A routing.

The request separates owner intent from evidence. A caller may set a typed task
kind; otherwise a narrow English/Indonesian leading-verb heuristic selects
conversation, research, engineering, or incident. Unknown phrasing defaults to
conversation. This is not general language understanding. Only engineering
invokes the existing Existing/Greenfield/Hybrid selector. Its English evolution
rules remain unchanged; multilingual evolution detection is not implemented.

| Request | Route | Boundary |
| --- | --- | --- |
| Jelaskan dokumen ini | Conversation | No Architect/Engineer call |
| Rancang konsep Bruno dari kebutuhan ini | Engineering / Greenfield | Proposal preparation only |
| Analisis repository ini | Research | REPOSITORY_READER_NOT_AVAILABLE |
| Diagnose this incident | Incident | No remediation execution |

## Evidence and adapter contract

The bridge recomputes M2 from supplied input, rather than accepting a caller's
READY receipt. Only accepted source content enters the adapter. The complete M2
result preserves policy, assessments, rejected claims, missing evidence,
conflicts, and effective claim status. Source content is labelled
`UNTRUSTED_DATA_ONLY` and never selects routing or authority.

Task/run/bundle IDs, route, intent, repository reference, evidence, and controller
limitations are serialized and bound by SHA-256. Each proposal echoes that
digest. The adapter receives an independent copy so mutation cannot alter the
controller receipt. The digest binds an invocation, not permission or truth.

`ReasoningProposal.model_json_schema()` supplies the provider-neutral schema.
Outputs allow a summary, candidate claims, and proposed steps; they cannot set
authority, validation status, workflow state, or execution permission. Claims
allow SOURCE_CLAIM, ASSUMPTION, and NOT_MEASURED. References must identify usable
input sources. The controller retains its own context and limitations.

`PROPOSAL_VALIDATED` means schema, input binding, and reference checks passed.
It does not prove factual correctness, entailment, instruction-injection
resistance of a model, or completed actions. Free text remains untrusted even
if it asserts success. Consumers must present controller limitations and
context alongside proposals. `execution_authorized` is always false.

## Limits and failures

M3-A has a 1,000,000-byte serialized input limit, a 100,000-byte serialized
output limit, and field/list bounds. These are offline contract limits, not
provider resource guarantees. Inputs admit at most 32 source references, 32
content items, 128 claims, and 128 declared conflicts to bound M2 pair checks.
These limits do not establish
provider transport, cost, or production capacity guarantees. One adapter call
is made without retries. Timeout exceptions and provider exceptions produce
classified failures without exposing private exception details. Invalid output
is rejected. Input validation/budget errors raise before the call. Failures
never fall back to a successful stub result.

The default stub is labelled STUB and states that no reasoning occurred.
Injected adapters are labelled OFFLINE_ADAPTER. Adapter code must be trusted;
this Python protocol is not a sandbox and cannot enforce a hard deadline.
CP1 must implement an approved provider runner with deadlines, cancellation,
token/output/cost limits, and separate live receipts. Real model behavior,
including source-instruction containment, remains NOT_EXECUTED here.

## Master checkpoint mapping

The M2/M3-A/M3-B/M4/M5/M7/M8/M10 labels in this historical implementation
record identify earlier slices only. Current planning uses the
[Master Roadmap](roadmap.md).

| Target | Current implementation | Master CP |
| --- | --- | --- |
| Offline reasoning intake/proposal contracts | `contracts/reasoning.py`; `reasoning/runtime.py` | CP0 historical foundation |
| Caller-supplied evidence bridge | `evidence/context.py` | CP0 historical foundation; external source/repository resolution expands in CP2 |
| Real model adapter | Protocol/output schema only | **CP1** |
| Repository intelligence | Reader unavailable | **CP2** |
| Durable authenticated service | No storage/runtime wiring | **CP3** |
| Personal JARVIS/voice/browser | Not present | **CP4** |
| Skills / Capability OS | Not active | **CP5** |
| Capability Foundry | Not active | **CP6** |
| Controlled writes | Not active | **CP7** |
| Learning / REE | No active profile or memory writes | **CP8** |

Old uncommitted `elite_team` adapter work was inspected without modification.
Reusable patterns are provider-neutral generation, controller-owned schema,
and sanitized errors. Its four engineering roles and LangGraph injection were
not copied into this task-kind seam. Qualification of 25 skill design candidates
remains separate; M3 does not wait for the entire catalog.

`tests/unit/test_reasoning.py` covers routing, evidence preservation, rejected
sources, schema/binding/reference rejection, failure handling, adapter mutation,
determinism, and offline source-instruction boundaries. Existing tests remain
unchanged. Offline passes do not establish live reasoning or production readiness.
