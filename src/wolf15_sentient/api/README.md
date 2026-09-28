# API contract

## Ownership and interface

CURRENT: [app.py](app.py) owns FastAPI transport and `create_app()`.
`GET /health` returns product identity/version through `HealthResponse`;
`POST /tasks` validates `TaskRequest` and returns `WorkflowResult` from
`orchestration.run_workflow`. The public ASGI export is
`wolf15_sentient.main:app`.

## Boundary and dependencies

Transport depends on [contracts](../contracts/README.md) and the
[Control Kernel](../orchestration/README.md). It does not own authority,
workflow transitions or reasoning. Health reports process identity, not
provider health or production readiness. The current API is in-memory and
accepts only `READ_ONLY`; it has no authentication/durable service claim.
M2, M3-A and SCRS are explicit library entry points, not HTTP endpoints.

## Verification and changes

[API tests](../../../tests/integration/test_api.py) cover identity, validation,
workflow correlation and fail-closed behavior. CI also imports the installed
ASGI app outside the checkout. A route or response change must review this
README, schemas, API tests and consumers. CP3 may add authenticated durable
service behavior only with its own acceptance evidence; future Owner Console
is a client of the same authority chain.

[Canonical ownership](../../../docs/architecture/canonical-ownership.md)
decides global ownership; this README describes the local contract.
