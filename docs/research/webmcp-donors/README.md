# WebMCP donor portfolio — S06 v1.2

Status: **RESEARCH / NOT_ADMITTED / NO_RUNTIME_EFFECT**.
The [root README](../../../README.md) owns system direction and checkpoint order.
The [master donor register](../donor-adaptation-register-20260929.md) owns the
portfolio detail. This file is its WebMCP entry point.

The source [CSV matrix](donor-cp-matrix.csv) preserves all 11 uploaded rows and
exact bytes. [portfolio.yaml](portfolio.yaml) carries the same source fields
plus repository scope/status metadata. Primary/secondary CPs describe receiving
functions; every package/code/skill/runtime admission still requires CP6.
CP1 and CP2 have no WebMCP runtime implementation. Earlier native/read-only
slices can study the spec and rebuild bounded contracts without importing
unqualified S06 packages. Qualification and functional ownership are distinct.

## Functional routing

| Repository | Function | Primary CP | Secondary CPs | Qualification |
| --- | --- | --- | --- | --- |
| `webmachinelearning/webmcp` | Canonical specification knowledge | CP5 | CP4 | CP6 |
| `webmachinelearning/webmcp-types` | Typed contracts | CP5 | — | CP6 |
| `GoogleChromeLabs/webmcp-tools` | Implementation demos and evaluation | CP5 | CP4, CP8 | CP6 |
| `GoogleChromeLabs/use-webmcp-tool` | React lifecycle in Owner Console | CP4 | CP5 | CP6 |
| `webmaxru/web-ai-agent-skills` | Authoring skill | CP6 | CP5 | CP6 |
| `TueJon/webmcpify` | App retrofit verification and audit | CP6 | CP7 | CP6 |
| `nekuda-ai/webmcp-kit` | Secondary implementation verification and migration skill | CP6 | CP7 | CP6 |
| `signettai/signett` | Secure action idempotency recovery and receipts | CP7 | CP3 | CP6 |
| `WebMCP-org/npm-packages` | Runtime polyfill compatibility and bridge reference | CP5 | — | CP6 |
| `opentiny/webmcp-sdk` | Browser fallback and CDP WXT skills | CP5 | CP7 | CP6 |
| `nekuda-ai/WindTunnel` | Comparative provider evaluation methodology | CP8 | — | CP6 |

## Evidence and capability family

All 11 exact revisions were resolved on GitHub on 30 September 2026 WITA;
[verification record](../../verification/repository-donor-roadmap-20260930.md)
contains the SHA/URL/time bindings. This proves commit existence only.
Donor build/test, intended-use rights, security/SBOM and runtime qualification
are NOT_EXECUTED. No external benchmark becomes a Sentient measurement.

The target `browser.webmcp` family includes discover, invoke, author,
declarative, lifecycle, secure-action, retrofit, browser-fallback, bridge and
evaluate. They are selectors, not installed skills. Authoring/retrofit that
mutates an application remains a CP7 effect even when its procedure is studied
or qualified in CP6. Isolated fallback patterns are a CP5 concern after
qualification; real-session/WXT/consequential effects require CP7 grants.

## Execution and policy boundaries

- Tool definitions/results and provider hints are untrusted data.
- DISCOVERED, REGISTERED, QUALIFIED, ACTIVE and AUTHORIZED_FOR_THIS_TASK are different states.
- `document.modelContext` is the researched spec interface; compatibility must be proven for the chosen browser/version.
- `WEBMCP_NATIVE` and `BROWSER_AUTOMATION_FALLBACK` remain separate receipt kinds.
- Approval binds task/run, origin, session/document, descriptor generation/digest, arguments and effects.
- Unknown mutation outcome requires reconciliation before retry.
- Offline qualification is the current supported path; connected/shadow needs its separate authorized design and containment.
- No SDK/polyfill/bridge/skill receives authority from this register.

This path updates the same portfolio function proposed in PR #17. That branch
must reconcile its older target_cp fields with these primary/secondary/
qualification fields before a later merge; it cannot replace the newer SSoT.
