# Offline gateway validation and host observations

This CP1.2 prerequisite implements the frozen CP1.1 wire profile as an offline
library. `canonical.py` parses bounded bytes and rejects duplicate keys,
noncanonical serialization, non-NFC strings, unsafe integers and coercion.
`validation.py` checks strict request/response types, envelope digests,
correlation, evidence references and receipt consistency. Reusable wire types
belong to `contracts/model_gateway.py`.

`bind_reasoning_input` accepts already-supplied exact bytes, validates the
existing `ReasoningInvocation` contract and requires task/run/bundle and known
source identities to match. It preserves M3-A serialization independently from
gateway canonical JSON. It does not resolve URLs, open caller paths or retrieve
input by itself. Returned models are copies; validators revalidate supplied
request models before subsequent binding because callers can mutate them.

The schema is [gateway-schema.json](../../../../docs/architecture/cp1/gateway-schema.json)
and semantic rules are in the [frozen contract](../../../../docs/architecture/cp1/gateway-contract.md).
No trusted profile is approved by a matching hash alone. Concrete provider/model
selection, approved artifact storage, persona assembly and provider role mapping
remain unimplemented. There is no dispatch function, transport, provider SDK,
automatic fallback, `/tasks` integration or change to READ_ONLY authority.

Receipt usage and elapsed-time checks detect inconsistent claims. They do not
measure provider usage, enforce a physical deadline, interrupt work or establish
a spend bound. Unknown costs remain null/NOT_MEASURED; estimates are not promoted
to measurements. Provider-specific metering, cancellation and live persona
acceptance remain CP1.3–CP1.6 gates. This increment does not close CP1.2 or CP1.

## Provider-neutral CP1.3–CP1.5 prerequisite candidate

This additive, offline increment is stacked on the unmerged CP1.2 wire candidate.
It does not close a substep or depend on a selected provider. README §10 gates
successive checkpoints; §12 requires authorized merge and resulting-main evidence
before closure. Independent work inside CP1 may remain draft while those gates
are pending. The frozen wire contract and historical receipts are unchanged.

`admission.py` accepts a host-owned `InvocationWindow` created before dispatch
and a callback supplying fresh Control observations in the same monotonic clock
domain. It checks invocation/digest binding, policy, cancellation and deadline
before and after output validation. Observation timestamps must lie inside the
measured callback interval. Cancellation takes priority over policy and timeout;
host rejection also supersedes malformed provider output. A returned response
still has `execution_authorized=false`. Control owns state and must recheck before
later consumption: this is a point-in-time rejection check, not an atomic grant.
No cancellation registry, scheduler, transport or physical interruption is added.
Blocking callbacks, transport and cleanup require future host enforcement.

`telemetry.py` freshly validates a detached request and raw response and returns
an allowlisted, frozen `GatewayTelemetry` value. It includes only fixed outcome
categories, UUID/hash bindings, numeric usage, currency and descriptor digests.
Arbitrary provider/model/profile/method identifiers are not emitted as text.
Digests bind canonical descriptors; they do not anonymize low-entropy values or
approve them. There is no logging, persistence, sink or publication authorization.
The evidence class explicitly remains wire-reported, not independently measured;
`provider_reported_elapsed_ms` cannot stand in for host timing. Host rejection
exceptions are not automatically converted into provider telemetry receipts.

Concrete provider selection, approved profile resolution, tokenizer/pricing data,
enforceable spend bounds, transport cancellation/cleanup and live persona
acceptance remain pending. Synthetic tests cannot close CP1.3–CP1.6.

Run `python -m pytest tests/unit/test_gateway_contracts.py tests/unit/test_gateway_validation.py tests/unit/test_gateway_admission.py tests/unit/test_gateway_telemetry.py`
with the locked development environment. Tests use synthetic frozen fixtures
and native offline reasoning input, including byte/digest substitution, missing
or extra fields, budget inconsistencies and unknown evidence. No network or
real provider is used. Existing historical freeze artifacts remain unchanged.
