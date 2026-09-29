# CP1.1 gateway wire contract candidate

Lifecycle status is recorded only in cp1.1-freeze-receipt.json. This versioned definition supersedes the earlier prose draft for wire layout only; it does not activate code or select a provider. Ownership: contracts owns reusable wire types, sentient/model_gateway owns cognitive validation, models/providers owns transport mapping, models/profiles owns technical profiles. Control retains task state, grants, gates and cancellation.

## Exact wire definition

[gateway-schema.json](gateway-schema.json) defines draft-v0 request/response. All objects reject unknown fields and require declared fields; explicit nulls represent unknown values. No silent defaults. [persona-profile.yaml](persona-profile.yaml) is design metadata, not a loaded prompt. [acceptance-scenarios.json](acceptance-scenarios.json) maps P-01 through P-30; tests remain NOT_EXECUTED on a model.

The request wraps an immutable envelope and its SHA-256. The envelope includes gateway ID, task/run/bundle/input digest, provider/model/revision, technical/persona/policy profile hashes, data scope, limits, output schema and known evidence references. It uses a content-addressed reference to the existing ReasoningInput instead of duplicating its bytes. Before dispatch the host MUST retrieve the supplied exact bytes, validate the existing ReasoningInvocation digest/contract and correlate task/run/bundle and evidence refs. The offline fixture reference is synthetic; this host integration is NOT_IMPLEMENTED. Never resolve an arbitrary URL from a digest or model output.

Response echoes gateway identity, full digest and correlation. A proposal is schema/reference validated only; execution_authorized is false. Declared profile/schema/source hashes must match actual approved bytes before dispatch; the fixture verifier does not provide approval or artifact storage. Provider/model identity cannot change within an invocation. Retry count is zero and no fallback is permitted in this candidate.

## Canonical serialization: cp1-json-integer-nfc-v0

This is a restricted project profile, not a claim of RFC 8785 conformance. UTF-8 without BOM, no trailing newline or whitespace. JSON object keys are ASCII and sorted lexicographically; arrays preserve order. Strings must already be NFC and valid Unicode, with no unpaired surrogate. Use JSON escapes for controls, quote and backslash, leave other characters as UTF-8; slash is unescaped. Reject duplicate keys, floats/exponents, NaN/Infinity and integers outside signed 53-bit safe range. Values are null, booleans, safe integers, strings, arrays and objects. No stripping, normalization, type coercion or default insertion during verification.

Canonical bytes are defined by the supplied serializer and checked-in byte fixtures. Parser reserialization must equal supplied bytes. Digest is lowercase SHA-256 of the entire envelope; the outer gateway_digest_sha256 is excluded to avoid self-reference. It is a content binding, not a signature or authorization. Preserve the existing ReasoningInput digest semantics independently; existing input serialization is not redefined by this wire profile.

[fixtures/manifest.json](fixtures/manifest.json) records exact fixture hashes. Fixtures are SYNTHETIC_OFFLINE and NOT_DEPLOYABLE, including provider, pricing/profile and input references. No production binding is inferred. Any wire rule/schema/profile change invalidates freeze candidate review and requires new hashes and fixture review.

## Failure, budgets and prohibited behavior

Failure codes are closed in the schema; receipts omit arbitrary raw error text. Unknown usage/cost is null with NOT_MEASURED. Estimates require method/version and cannot count as measured. Costs use integer currency microunits; token/time counts are integers. Required financial limits need a verified pricing snapshot and enforceable preflight bound; otherwise BUDGET_NOT_MEASURED before dispatch. Token reservation must cover prompt/evidence/schema overhead plus output. Full enforcement requires actual tokenizer/provider data and is NOT_EXECUTED here.

A monotonic host deadline covers transport headers, body, stream and cancellation cleanup; cooperative generation max_time is insufficient. Reject late proposals. Host cancellation and policy have priority over provider output. No timeout enforcement is claimed by schema validation. Collector timeouts are a separate evidence class: compute retry was instrumented, historical LiteLLM/DeepAgents acquisition was not; never retroactively promote that receipt.

[prohibition-matrix.md](prohibition-matrix.md) records all58 normative source rows. No tool/repository authority, memory writes, scheduler, deployment, capability/REE activation, fallback or hidden model switch. Do not persist raw prompts, tool payloads, secrets or unrestricted internal reasoning. Preserve source conflicts; no first/latest-source truth override, voting truth, uncalibrated confidence or double-counting as uncertainty reduction. Trading/broker/strategy/owner-psychology logic stays outside the core. Logs alone do not prove learning; no adaptive mutation or self-promotion.

## Reproduction and remaining gates

Run `python verify_contract_fixtures.py` from this directory with jsonschema 4.26.0 (the recorded local environment). The runner is an offline documentation verifier, not an installed gateway. It validates positive/negative wire fixtures and deterministic bytes. No donor code or provider is invoked.

Final freeze additionally requires review of exact schema/profile/matrix bytes, provider/model/technical/policy binding structure and validation rules, exact persona guidance and assembly, applicable design evidence and a freeze receipt. Concrete provider selection belongs to CP1.2, enforcement implementation to CP1.3, and real-provider acceptance to CP1.6. Their pending execution is not a CP1.1 design-freeze blocker. Consult the separate receipt for local freeze/publication status. Provider behavior, timeout/cancellation, actual structured output, costs, injection resistance and persona behavior are later real-provider gates; no offline result promotes them to PASS.

## Review corrections for candidate v0

Nonblank textual identifiers and proposal strings must have no leading/trailing whitespace; reject before hashing, never normalize silently. This wire profile is intentionally stricter than a Pydantic parser that trims text. The gateway proposal remains within m3a-v0 semantics after validation.

revision_status SUPPLIED_NOT_VERIFIED means a revision string was supplied, not that it is immutable or resolved. NOT_VERIFIED with null means no revision is available. No PINNED claim is accepted by syntax alone; selected provider-specific resolution evidence must establish what is actually immutable before deployment.

Fixed SHA/UUID/currency strings have exact lengths. Cancellation and timeout status/code mappings work both directions. Successful receipts reject measured usage above declared output/cost/context-reservation limits and elapsed time at/after timeout. These checks detect inconsistent receipts; they do not prove provider metering honesty, preflight spend enforcement or physical interruption. Missing metrics remain NOT_MEASURED.

## Persona assembly binding

The exact guidance hash and three-component deterministic assembly are defined in persona-profile.yaml. Historical Windows paths are provenance only and never runtime loaders. Provider mapping must preserve trusted guidance/snapshot versus untrusted task data; no environment override or hidden prompt concatenation.
