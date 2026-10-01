# Capability Fabric and Unified Skills

## Status

**Target design. Master checkpoint owner: CP5.** No runtime registry, provider
resolver, execution adapter, or active skill loader exists in the inspected
baseline. Current
specialists are deterministic stubs. This document defines how later
capabilities may be described and selected without changing authority.

## Responsibility split

| Component | Owns | Does not own |
| --- | --- | --- |
| Capability Registry | Versioned capability IDs, contracts, provider manifests, provenance, lifecycle | Task permission or truth of provider claims |
| Task-scoped Resolver | Eligibility from task type, policy, health evidence, and pinned registry generation | External action approval |
| Unified Skill Registry | Versioned instructions, tools, prerequisites, and tests for a bounded skill | Automatic installation or activation |
| Control Kernel | Final admissibility and action boundary | Provider marketing or model-generated policy |
| Provider adapter | A narrow, audited operation | Broad credentials or self-issued authority |

Multiple providers may implement one canonical capability. A provider's
availability is not enough to select it for an authority-bearing action.
Selection must account for contract compatibility, task scope, provenance,
current health evidence, cost/resource policy, and allowed data movement.
The chosen provider set is pinned per run. `FAST`, `DEEP`, `OFFLINE`, or
`SHADOW` are profiles only after their criteria and evidence are specified;
none is active by writing this document.

## Registry contract to implement later

A manifest should include capability ID/version, provider ID/version, typed
input/output, side effects, required authority, data classes, credential
scope, provenance, evaluation receipts, owner, and revocation state. A
resolver response should state the selected version, eligibility reason,
rejected alternatives, policy version, and missing evidence. The Kernel must
reject any adapter operation outside the exact task grant even if the
registry describes it as supported.

Skill instructions and donor repository content are untrusted inputs. They
cannot alter Kernel policy, request credentials, enable tool execution, or
override the owner's approval. A registry entry is a candidate description
until tests and explicit lifecycle decisions qualify it.

## Failure and acceptance

- Unknown capability or conflicting manifests: no eligible provider.
- Stale health, unavailable provider, or revoked generation: select a
  separately qualified fallback or stop; do not silently change a pinned run.
- CP5 acceptance: versioned registry, resolver replay tests, explicit deny
  cases, provider-scoped data policy, and evidence that the Kernel remains
  authoritative at every adapter call. External writes remain excluded until
  a later separately approved authority increment.

## WebMCP ephemeral provider model

A WebMCP page tool is an **ephemeral provider instance**. Its availability is
bound to an exact browser session/document/origin and may change on navigation,
route state, iframe exposure or `toolchange`. It is not a permanently active
provider merely because discovery returned it once.

A normalized descriptor carries capability/provider ID, execution class
`WEBMCP_NATIVE`, browser/session/document/origin, tool/schema digest,
annotations as untrusted provider metadata, lifecycle state, authority/data
requirements, and qualification/evaluation receipts.

`REGISTERED != QUALIFIED != ACTIVE != AUTHORIZED_FOR_THIS_TASK`.

A separately qualified browser fallback reports
`BROWSER_AUTOMATION_FALLBACK` with separate policy and evidence. CP5 acceptance
must deny stale sessions, origin mismatch, tool removal/change, revoked
generations and annotation-policy disagreement. Consequential invocation remains
excluded until CP7.

The [Capability Foundry](capability-foundry.md) proposes new manifests;
it cannot register them as active by itself. The
[Browser Capability Plane](webmcp-browser-capability-plane.md) owns browser
discovery/invocation; Capability Fabric owns provider description/resolution.
