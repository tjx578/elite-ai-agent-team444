# Offline gateway validation

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

Run `python -m pytest tests/unit/test_gateway_contracts.py tests/unit/test_gateway_validation.py`
with the locked development environment. Tests use synthetic frozen fixtures
and native offline reasoning input, including byte/digest substitution, missing
or extra fields, budget inconsistencies and unknown evidence. No network or
real provider is used. Existing historical freeze artifacts remain unchanged.
