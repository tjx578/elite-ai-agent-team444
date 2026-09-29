# WOLF15 Sentient — Master Repository Donor Register v1.2 (repository reconciliation)

**Generated:** 2026-09-29  
**Revision:** v1.2 — Hugging Face + WebMCP donor-to-checkpoint reconciliation  
**Purpose:** Consolidated donor-repository register for WOLF15 Sentient checkpoint planning.  
**Rule:** A donor repository is a source of patterns/capabilities, not an authority replacement. Control Kernel remains the sole WOLF15 authority owner.


**Repository revision:** `SSOT-2026-09-30.1` / `v1.2-reconciled.1`, 30 September 2026 WITA.  
**System SSoT:** [root README](../../README.md). [Checkpoint detail](../architecture/roadmap.md) is a derived view. This register owns donor identities and functional routing, not a second system roadmap.  
**Bound Sentient base:** `07c942cd62ec5e85a521ee47976559a55f35d8b8`.  
**Source:** owner-uploaded `WOLF15_SENTIENT_MASTER_REPOSITORY_DONOR_REGISTER_v1.2_WEBMCP(1).md`; source SHA-256 `611dd6feb2da7dc6e00b62c0353beee52d51838fd8796f192322fc1e6e4b065c`.  
**CSV source:** [11 unchanged S06 records](webmcp-donors/donor-cp-matrix.csv); source SHA-256 `ccbab9b16a945c3a97c6052b5a88acf1f26a9e525fb96bd360e56785890b2a33`.  
**Evidence:** [source checks and reconciliation](../verification/repository-donor-roadmap-20260930.md).

The uploaded register below is retained with the explicit amendments recorded
here. Original dates and reported HEADs describe its source snapshot. Only
exact-commit existence for 11 S06 revisions and the Transformers revision was
independently rechecked in this update. Current default HEADs, complete donor
contents, builds, rights/security and runtime fitness were not requalified.

## Repository reconciliation decisions

| ID | Source issue | Effective decision |
| --- | --- | --- |
| DR-01 | Donor register called master while root README is system SSoT | Register is the master donor portfolio; system order, goals, 28-role roster and gates remain in root README |
| DR-02 | Functional CP1–CP5 precedes donor qualification CP6 | Functional mapping is receiving ownership, not admission timing. Native foundations may learn/rebuild contracts first; donor package/code/skill/runtime acquisition remains gated by CP6 |
| DR-03 | Some source flows require shadow unconditionally | Offline qualification only under current policy. Connected/shadow requires a separately authorized design, containment and evidence path |
| DR-04 | Uploaded HEAD columns may look like fresh repo observations | Preserve as HEAD reported by source on 2026-09-29; do not replace assessment snapshots or claim fresh default HEAD verification |
| DR-05 | `hf.embedding` and `hf.image` coexist with specific family names | Treat as proposed aliases/general labels; canonical plural `hf.embeddings` and specific image selectors require explicit normalization before registry use |
| DR-06 | Framework license may be confused with model rights | Apache-2.0 is a source-reported framework claim; model weights/tokenizers/config/datasets and exact use require separate provenance/rights decisions |
| DR-07 | Old main docs still show CP0 pending | Align to historical CP0 CLOSED at `bad73335f518d89356b88cba1cc26730808cd224`; CP1 ACTIVE_NEXT / NOT_IMPLEMENTED |
| DR-08 | Similar donor files exist only in PR #17 | Reuse the same canonical register and WebMCP portfolio paths; reconcile that older proposal before any future merge |

No exception permits package adoption before its qualification gate. If a
CP1–CP5 slice requires donor import, hold that dependency until a separately
accepted qualification amendment or CP6 completion. Studying a protocol and
implementing a native contract is distinguished from admitting its external
SDK/skill/polyfill. See the [root prerequisite decision](../../README.md#urutan-implementasi-dan-qualification-donor).

## Evidence status vocabulary

- `VERIFIED_CURRENT_GITHUB` — repository metadata / current default-branch HEAD checked directly on GitHub.
- `BOUND_ASSESSMENT_SNAPSHOT` — exact SHA explicitly used by an existing WOLF15 donor assessment.
- `SOURCE_DERIVED` — mapping recovered from project/chat source material.
- `WATCH_CANDIDATE` — monitored/researched; not admitted as a WOLF15 capability.
- `NOT_ESTABLISHED` — source material is insufficient to identify an exact repository/SHA.
- `NOT_ADMITTED` — no runtime/capability authority granted.
- `INDEPENDENT_REVISION_VERIFIED` — the reported Git commit SHA was independently resolved on GitHub in this update; this does not imply build/test/license/runtime qualification.

---

## A. Primary donor portfolio — CP1–CP8

| ID | Repository | Assessment snapshot | HEAD reported by source (2026-09-29) | Upstream | CP routing | Primary value | Status |
|---|---|---|---|---|---|---|---|
| ARCH-DONOR-OPENJARVIS-01 | `tjx578/OpenJarvis-sentient` | `fbbdb23c86627c18b859369b19746a9245f1ce0b` | `fbbdb23c86627c18b859369b19746a9245f1ce0b` | `open-jarvis/OpenJarvis` | CP1, CP3, CP4, CP5, CP6, CP7, CP8 | model/provider abstraction; persistent runtime; connectors; MCP; sandbox; telemetry; controlled execution; adaptive candidates | `RESEARCH_DONOR_NOT_ADMITTED` |
| ARCH-DONOR-PYDANTIC-AI-01 | `tjx578/pydantic-ai-sentient` | `05f2f35ca8af6f1382f06761c6a9a23dbd341728` | `05f2f35ca8af6f1382f06761c6a9a23dbd341728` | `pydantic/pydantic-ai` | CP1 primary; CP2/CP5 secondary patterns; voice deferred to CP4 | typed model/provider layer behind WOLF15 ModelGateway; structured output; cancellation/timeout; progressive disclosure | `PROPOSED_DONOR_KNOWLEDGE_PACK / NOT_ADMITTED` |
| ARCH-DONOR-PAPERCLIP-01 | `paperclipai/paperclip` | local assessed clone `paperclip578@a9d636d73d59e56e0139fb7c5d5a2f2ca844d833` | `d172197117a14b80a1eb2d2835a0e7cce2679656` | — | CP3, CP4, CP5, CP6, CP7, CP8; CP9 optional projection | durable task/run/lease lifecycle; approvals; work management; skill provenance/versioning; owner visibility | `RESEARCH_DONOR_NOT_ADMITTED` |
| ARCH-DONOR-RUFLO-01 | `ruvnet/ruflo` | local assessed clone `multiagentruflo@f547cec013041a59b2f18921f5c861bf3d525825` | `fce8e6da5a6edda3791367b244066e6c67730196` | — | CP1, CP2, CP3, CP4, CP5, CP6, CP7, CP8 | provider interface; retrieval/graph memory; execution truth; guidance/capability contracts; handoff; candidate-only learning | `SELECTIVE_ADOPTION / NOT_ADMITTED` |

### Invariants for the primary portfolio

- Donor runtime **must not** replace WOLF15 Control Kernel.
- `REGISTERED ≠ QUALIFIED ≠ ACTIVE`.
- `HANDLER_RETURNED ≠ EXECUTED ≠ ACCEPTED ≠ VERIFIED`.
- No donor capability may self-promote into active runtime.
- Exact assessment SHA and current upstream HEAD are separate facts; newer does not automatically mean better.

---

## B. CP1 watch candidates

| Repository | HEAD reported by source (2026-09-29) | Intended use | Status |
|---|---|---|---|
| `BerriAI/litellm` | `684a1edd44efa3a7c7f0395ccfa1bf9803017ea2` | model/provider gateway and routing research | `WATCH_CANDIDATE` |
| `langchain-ai/deepagents` | `b1ebc5bd51aab19c1251197b1b8eb699c85cfc00` | agent harness / coding-agent implementation patterns | `WATCH_CANDIDATE` |

The uploaded source describes these as monitored with Pydantic AI for release/security/breaking-change relevance to CP1; no scheduled monitoring is established by this document. They are not canonical runtime providers by default.

---

## C. Legacy 8-folder donor set recovered from the archived checkpoint work

This set came from the older donor-adaptation roadmap. Its old CP numbering must not be silently treated as the current CP0–CP9 canonical numbering.

| Local/folder identity | Recovered GitHub identity | HEAD reported by source (2026-09-29) | Historical role | Status |
|---|---|---|---|---|
| `paperclip578` | `paperclipai/paperclip` | `d172197117a14b80a1eb2d2835a0e7cce2679656` | work/task lifecycle, approvals, audit, task board | mapped into primary portfolio |
| `multiagentruflo` | `ruvnet/ruflo` | `fce8e6da5a6edda3791367b244066e6c67730196` | assignment, handoff, provider/retrieval/memory patterns | mapped into primary portfolio |
| `context7` | `upstash/context7` | `83e972e8b0fa2fb9dde78c451358d4209a9c0236` | library/version documentation retrieval | `LEGACY_DONOR_REFERENCE` |
| `MCPkonektor` | `modelcontextprotocol/modelcontextprotocol` | `046fa30efd374370afb87ef830bd788eac5f217e` | MCP specification/schema/transport/security-boundary reference | `LEGACY_DONOR_REFERENCE` |
| `dashboardanimation` | `d3/d3` | `ca958d45217b4c15332d971b935451a6d4c978f4` | evidence graph/timeline/interactive visualization | `LEGACY_DONOR_REFERENCE` |
| `next.js` | `vercel/next.js` | `b829c6189bc3af485cb92f0c3f3d09bf81a8e6fe` (`canary`) | Owner Console / React framework reference | `LEGACY_DONOR_REFERENCE` |
| `tuyul_ea_dashboard` | historical WOLF15 repo `tjx578/tuyul_ea_dashboard`; upstream design identified as `hugodemenez/deltalytix` | historical WOLF15 audit: `a401ba16aca7171d34442292a41bf441a686dc9c`; source-reported upstream Deltalytix HEAD `7ef0342f88e9512b457c9f6f3d89e3bbc0cbd65c` | dashboard/widget/journal UX reference | `REFERENCE_ONLY`; transplant held |
| `unlimited_book` | Openlib / Flutter reader; exact GitHub upstream not proven by recovered source | `NOT_ESTABLISHED` | document catalog/library/reader patterns | `NOT_ESTABLISHED` |

---


## HUGGING FACE / TRANSFORMERS — ROADMAP INTEGRATION

**Donor ID:** `ARCH-DONOR-HUGGINGFACE-TRANSFORMERS-01`  
**Repository:** `tjx578/transformers-sentient`  
**Upstream:** `huggingface/transformers`  
**Assessment / source-reported observed SHA:** `6b07e4510e3f9667f5256656118515bcde306fc4`  
**License (framework, source-reported; intended-use rights NOT_EXECUTED):** `Apache-2.0`  
**Classification:** `RUNTIME_COMPONENT` + `CAPABILITY_DONOR` + `TOOL_PROVIDER` + `KNOWLEDGE_SOURCE`  
**Admission:** `RESEARCH_DONOR_NOT_ADMITTED`  
**Authority effect:** `NONE`  
**Runtime activation:** `FALSE`

### Canonical checkpoint routing

| CP | Hugging Face / Transformers role | Scope boundary |
|---|---|---|
| **CP1 — Real Sentient Reasoning** | Candidate `LOCAL_TRANSFORMERS_PROVIDER` behind WOLF15 `ModelGateway`; study OpenAI-compatible serving and model/profile abstraction | One-provider-first remains; model output is not evidence, command, or authority |
| **CP3 — Production Grade v1** | Model-serving lifecycle patterns: health, load/unload, device/dtype selection, quantization, cache/lifecycle telemetry | No automatic model download/load; production readiness must be verified separately |
| **CP4 — Personal JARVIS** | Local multimodal capabilities: ASR, text/audio, image/vision, multimodal inference | Voice/vision input still becomes a bounded task through Control Kernel; no direct external action |
| **CP5 — Capability OS** | Canonical capability family such as `hf.text-generation`, `hf.chat`, `hf.asr`, `hf.image`, `hf.multimodal`, `hf.embedding`, `hf.model-serving` | Registered capability is not automatically qualified or authorized |
| **CP6 — Capability Foundry** | Flagship donor for repository→capability extraction; inspect bundled skills, runtime, pipeline families, model interfaces; sandbox/evaluate before admission | Exact SHA, provenance, rights, security, overlap, offline sandbox/evaluation; shadow requires its separate authorized qualification path |
| **CP8 — Adaptive Intelligence** | Training/fine-tuning infrastructure as an offline candidate provider; experiment/evaluate model/profile improvements | No live self-modification, no auto-promotion, no candidate-controlled evaluator |

### Capability family

| Candidate family | Status |
| --- | --- |
| `hf.model-loader` | TARGET / NOT_ADMITTED |
| `hf.text-generation` | TARGET / NOT_ADMITTED |
| `hf.chat` | TARGET / NOT_ADMITTED |
| `hf.embeddings` | TARGET / NOT_ADMITTED |
| `hf.text-classification` | TARGET / NOT_ADMITTED |
| `hf.asr` | TARGET / NOT_ADMITTED |
| `hf.text-to-audio` | TARGET / NOT_ADMITTED |
| `hf.image-classification` | TARGET / NOT_ADMITTED |
| `hf.object-detection` | TARGET / NOT_ADMITTED |
| `hf.image-segmentation` | TARGET / NOT_ADMITTED |
| `hf.multimodal` | TARGET / NOT_ADMITTED |
| `hf.video` | TARGET / NOT_ADMITTED |
| `hf.quantization` | TARGET / NOT_ADMITTED |
| `hf.model-serving` | TARGET / NOT_ADMITTED |
| `hf.training` | TARGET / NOT_ADMITTED |
| `hf.finetuning` | TARGET / NOT_ADMITTED |


### Critical boundary

```text
TRANSFORMERS
= framework / runtime

MODEL CHECKPOINT
= trained model weights + model-specific license / provenance

WOLF15 SENTIENT
= orchestration + evidence + policy + capability selection
```

A framework license does **not** establish the license or admissibility of every model checkpoint. Model artifacts must be registered, pinned, licensed, scanned, evaluated, and approved separately.

`trust_remote_code` should remain `false` by default until a separately governed exception is approved.

### Roadmap effect

```text
CP ORDER CHANGE = NO

CP1  += local model-provider candidate
CP3  += model-serving operations patterns
CP4  += local multimodal / speech / vision capability candidates
CP5  += Hugging Face capability family + model/provider descriptors
CP6  += Transformers as flagship donor/admission test case
CP8  += offline training/fine-tuning candidate lifecycle
```

Hugging Face does **not** become a second orchestrator and does **not** replace Pydantic AI. A valid target composition is:

Control Kernel gates the Sentient ModelGateway. A task uses an admitted
provider adapter, which may eventually use Pydantic AI direct-provider patterns,
LOCAL_TRANSFORMERS_PROVIDER or another qualified provider. The candidates do
not create additional orchestrators or simultaneous-provider requirements.



## WEBMCP PORTFOLIO — S06 ROADMAP INTEGRATION

**Decision:** `PASS_DESIGN_MAPPING / NOT_ADMITTED`  
**Roadmap order change:** `NO`  
**CP1 WebMCP implementation:** `NONE`  
**CP2 WebMCP implementation:** `NONE`  
**Systematic qualification owner:** `CP6 Capability Foundry`

The final checkpoint decision places WebMCP as a browser capability family: CP3 owns receipt/recovery/observability patterns, CP4 owns read-only browser entry, CP5 owns ephemeral page/session providers, CP6 qualifies donors/SDKs/skills/polyfills/bridges, CP7 owns consequential browser effects, CP8 owns evaluation, and CP9 only integrates already-qualified components.

### Independent revision verification

All 11 reported S06 revisions were independently resolved as exact Git commits in their named GitHub repositories during the source update and rechecked on 30 September 2026 WITA for this repository reconciliation. The linked verification record binds the observations. This upgrades the narrow field `independent_revision_verification` from `NOT_EXECUTED` to `PASS_EXACT_COMMIT_EXISTS`.

This verification **does not** establish current default-branch HEAD, license compliance, build success, tests, security, SBOM, runtime fitness, or WOLF15 admission.

| Source | Repository | Verified revision | Role | Primary functional CP | Secondary functional CP | Qualification CP | Verification |
|---|---|---|---|---|---|---|---|
| S06 | `webmachinelearning/webmcp` | `0957b0b8f1e32c401d4248424719a4851d4202c4` | Canonical specification knowledge | **CP5** | CP4 | **CP6** | `PASS_EXACT_COMMIT_EXISTS` |
| S06 | `webmachinelearning/webmcp-types` | `a8d8292ff645b691bfdb529484d3c089e81e8c28` | Typed contracts | **CP5** | — | **CP6** | `PASS_EXACT_COMMIT_EXISTS` |
| S06 | `GoogleChromeLabs/webmcp-tools` | `a66c1be1caee78bb98b9781bf5cb4413ad2ccac7` | Implementation demos and evaluation | **CP5** | CP4, CP8 | **CP6** | `PASS_EXACT_COMMIT_EXISTS` |
| S06 | `GoogleChromeLabs/use-webmcp-tool` | `9f0dc6eddf88cff65ebe877f199d4547e74ab31e` | React lifecycle in Owner Console | **CP4** | CP5 | **CP6** | `PASS_EXACT_COMMIT_EXISTS` |
| S06 | `webmaxru/web-ai-agent-skills` | `03b778c8ef822c98b112fd3617050c72d78f4d60` | Authoring skill | **CP6** | CP5 | **CP6** | `PASS_EXACT_COMMIT_EXISTS` |
| S06 | `TueJon/webmcpify` | `c17d1f1382e306296becc0e8294106c477e13d40` | App retrofit verification and audit | **CP6** | CP7 | **CP6** | `PASS_EXACT_COMMIT_EXISTS` |
| S06 | `nekuda-ai/webmcp-kit` | `f0298ec9f26af13e477b9141ab4d8f2a6c23426d` | Secondary implementation verification and migration skill | **CP6** | CP7 | **CP6** | `PASS_EXACT_COMMIT_EXISTS` |
| S06 | `signettai/signett` | `cb9be5ff2e9ca669c14e596673355d1ce58d3924` | Secure action idempotency recovery and receipts | **CP7** | CP3 | **CP6** | `PASS_EXACT_COMMIT_EXISTS` |
| S06 | `WebMCP-org/npm-packages` | `1c7a398a77fa54e54b4d3fdd7ed05d19efb067d5` | Runtime polyfill compatibility and bridge reference | **CP5** | — | **CP6** | `PASS_EXACT_COMMIT_EXISTS` |
| S06 | `opentiny/webmcp-sdk` | `47a2b031dfd77db19e18b5e7621976c5885bd924` | Browser fallback and CDP WXT skills | **CP5** | CP7 | **CP6** | `PASS_EXACT_COMMIT_EXISTS` |
| S06 | `nekuda-ai/WindTunnel` | `5ca8644e23826ebb30108e7bad240b61043bfe67` | Comparative provider evaluation methodology | **CP8** | — | **CP6** | `PASS_EXACT_COMMIT_EXISTS` |

### Functional checkpoint interpretation

**CP1 — Real Sentient Reasoning**

```text
WebMCP runtime implementation = NONE
```

WebMCP may already exist as research knowledge, but CP1 remains one-real-model-provider-first. Browser capability work must not enlarge CP1.

**CP2 — Repository Intelligence**

```text
WebMCP runtime implementation = NONE
```

Repository/source analysis remains independent from browser tool execution. If a repository contains WebMCP code, CP2 may read/analyze it as source data only.

**CP3 — Production Grade v1**

Primary WebMCP-derived contribution:

- `signettai/signett` → idempotency, recovery, receipts, verification semantics.
- Cross-cutting target: durable execution receipts must distinguish success, ambiguity, cancellation, and recovery state.

No consequential browser mutation is authorized at CP3.

**CP4 — Personal JARVIS & Read-Only Intelligence**

Recommended donors:

- `webmachinelearning/webmcp` → read-only browser capability semantics.
- `GoogleChromeLabs/webmcp-tools` → Page Agent / read-only discovery and invocation patterns.
- `GoogleChromeLabs/use-webmcp-tool` → Owner Console React lifecycle tied to page/session state.

CP4 remains read-only. A discovered tool is not automatically authorized.

**CP5 — Capability OS**

Recommended donors:

- `webmachinelearning/webmcp`
- `webmachinelearning/webmcp-types`
- `GoogleChromeLabs/webmcp-tools`
- `GoogleChromeLabs/use-webmcp-tool`
- `webmaxru/web-ai-agent-skills` (only after qualification)
- `WebMCP-org/npm-packages`
- `opentiny/webmcp-sdk` for bounded/isolated provider patterns

Target capability family:

| Candidate family | Status |
| --- | --- |
| `browser.webmcp.discover` | TARGET / NOT_ADMITTED |
| `browser.webmcp.invoke` | TARGET / NOT_ADMITTED |
| `browser.webmcp.author` | TARGET / NOT_ADMITTED |
| `browser.webmcp.declarative` | TARGET / NOT_ADMITTED |
| `browser.webmcp.lifecycle` | TARGET / NOT_ADMITTED |
| `browser.webmcp.secure-action` | TARGET / NOT_ADMITTED |
| `browser.webmcp.retrofit` | TARGET / NOT_ADMITTED |
| `browser.webmcp.browser-fallback` | TARGET / NOT_ADMITTED |
| `browser.webmcp.bridge` | TARGET / NOT_ADMITTED |
| `browser.webmcp.evaluate` | TARGET / NOT_ADMITTED |


Required invariant:

```text
DISCOVERED
≠ REGISTERED
≠ QUALIFIED
≠ ACTIVE
≠ AUTHORIZED_FOR_THIS_TASK
```

**CP6 — Capability Foundry**

All 11 S06 repositories pass through CP6 qualification before code/runtime/skill admission.

CP6 responsibilities:

```text
PIN EXACT SHA
→ provenance
→ license/rights
→ security
→ architecture inspection
→ skill/tool/runtime extraction
→ overlap check
→ sandbox
→ evaluation
→ shadow only if its separate qualification path is authorized
→ admission decision
```

Primary CP6-specific donors:

- `webmaxru/web-ai-agent-skills`
- `TueJon/webmcpify`
- `nekuda-ai/webmcp-kit`

The remaining S06 repositories also pass CP6 as qualification inputs even if their functional owner is CP3/CP4/CP5/CP7/CP8.

**CP7 — Controlled Technology Builder**

Recommended donors:

- `signettai/signett` → authorization, confirmation, idempotency, recovery, receipts.
- `TueJon/webmcpify` → bounded retrofit/repair workflow after explicit approval.
- `nekuda-ai/webmcp-kit` → controlled migration/implementation after approval.
- `opentiny/webmcp-sdk` → real user-session/WXT browser control only under higher-authority grants.

Invariant:

```text
WEBMCP_NATIVE_READ
≠ CONSEQUENTIAL_ACTION

CONSEQUENTIAL_ACTION
→ prepare
→ review
→ approve
→ execute
→ receipt
→ verify authoritative state
```

**CP8 — Adaptive Intelligence**

Recommended donors:

- `GoogleChromeLabs/webmcp-tools` → WebMCP evaluation assets/patterns.
- `nekuda-ai/WindTunnel` → comparative provider evaluation methodology.

Metrics may include task success, execution time, token usage, cost, cancellation, failure mode, and mutation verification.

External benchmark results remain `NOT_MEASURED` for WOLF15 until reproduced on a WOLF15-owned workload.

**CP9 — Technology Company OS**

No new WebMCP donor is admitted merely because CP9 is reached. CP9 integrates only providers/skills/runtimes already qualified under their owning checkpoints.

### WebMCP security and authority invariants

```text
TOOL DEFINITION
= untrusted input

TOOL RESULT
= untrusted input

PROVIDER HINT
≠ policy

REGISTERED TOOL
≠ qualified capability

QUALIFIED CAPABILITY
≠ authorized action

PAGE / BROWSER SESSION
≠ Control Kernel authority
```

`WEBMCP_NATIVE` and `BROWSER_AUTOMATION_FALLBACK` must remain separate execution kinds in receipts.


## E. Current checkpoint meaning

Current canonical WOLF15 roadmap uses:

- **CP0** — Cognitive Foundation (CLOSED at its accepted SHA)
- **CP1** — Real Sentient Reasoning
- **CP2** — Repository Intelligence
- **CP3** — Production Grade v1
- **CP4** — Personal JARVIS
- **CP5** — Capability OS
- **CP6** — Capability Foundry
- **CP7** — Controlled Technology Builder
- **CP8** — Adaptive Intelligence
- **CP9** — Technology Company OS (integration only)

The recovered older 8-donor roadmap used a different CP numbering scheme. Any old donor-to-CP number must be reconciled before being promoted into the current roadmap.

---


## MASTER CP-BY-CP DONOR RECOMMENDATION MATRIX

This is the implementation-routing view. A donor may appear in multiple CPs because a repository can contribute different bounded capabilities. CP6 qualification is mandatory for external donor admission and is not a second runtime owner.

### CP1 — Real Sentient Reasoning

Recommended/known donors:

- `tjx578/pydantic-ai-sentient` — **primary provider-contract donor**.
- `tjx578/OpenJarvis-sentient` — model/provider abstraction patterns.
- `ruvnet/ruflo` — bounded provider interface / timeout / fallback patterns.
- `tjx578/transformers-sentient` — candidate local Transformers model provider.
- `BerriAI/litellm` — watch/research candidate; no automatic multi-provider routing.
- `langchain-ai/deepagents` — watch/research candidate; context accounting/agent-harness patterns only.

WebMCP donors in CP1: **none**.

### CP2 — Repository Intelligence

Recommended/known donors:

- `ruvnet/ruflo` — retrieval / graph reranking / candidate discovery patterns.
- `tjx578/pydantic-ai-sentient` — RepoContext, deduplication, context-spill/chunking patterns.
- `upstash/context7` — version-aware documentation retrieval reference.

WebMCP donors in CP2: **none**. WebMCP source can be analyzed as repository data, but not executed.

### CP3 — Production Grade v1

Recommended/known donors:

- `tjx578/OpenJarvis-sentient`
- `paperclipai/paperclip`
- `ruvnet/ruflo`
- `tjx578/transformers-sentient`
- `signettai/signett` — WebMCP secure receipt/recovery/idempotency patterns

### CP4 — Personal JARVIS & Read-Only Intelligence

Recommended/known donors:

- `tjx578/OpenJarvis-sentient`
- `paperclipai/paperclip`
- `ruvnet/ruflo`
- `tjx578/transformers-sentient`
- `upstash/context7`
- `d3/d3` — visualization reference
- `vercel/next.js` — Owner Console framework reference
- `hugodemenez/deltalytix` / historical `tuyul_ea_dashboard` — UX/dashboard reference only
- `unlimited_book` / Openlib — exact upstream still `NOT_ESTABLISHED`; document-library pattern only
- `webmachinelearning/webmcp`
- `GoogleChromeLabs/webmcp-tools`
- `GoogleChromeLabs/use-webmcp-tool`

### CP5 — Capability OS

Recommended/known donors:

- `tjx578/OpenJarvis-sentient`
- `paperclipai/paperclip`
- `ruvnet/ruflo`
- `tjx578/pydantic-ai-sentient`
- `tjx578/transformers-sentient`
- `modelcontextprotocol/modelcontextprotocol`
- `webmachinelearning/webmcp`
- `webmachinelearning/webmcp-types`
- `GoogleChromeLabs/webmcp-tools`
- `GoogleChromeLabs/use-webmcp-tool`
- `webmaxru/web-ai-agent-skills` after CP6 qualification
- `WebMCP-org/npm-packages`
- `opentiny/webmcp-sdk` for bounded provider/fallback patterns

### CP6 — Capability Foundry

All external donor code/skills/runtimes intended for admission are qualified here.

Priority portfolio includes:

- OpenJarvis
- Paperclip
- Ruflo
- Pydantic AI
- Hugging Face / Transformers
- all 11 S06 WebMCP repositories
- future donor repositories discovered later

CP6 admission never grants authority by itself.

### CP7 — Controlled Technology Builder

Recommended/known donors:

- `tjx578/OpenJarvis-sentient`
- `paperclipai/paperclip`
- `ruvnet/ruflo`
- `signettai/signett`
- `TueJon/webmcpify`
- `nekuda-ai/webmcp-kit`
- `opentiny/webmcp-sdk` only for approved real-session/consequential browser actions

### CP8 — Adaptive Intelligence

Recommended/known donors:

- `tjx578/OpenJarvis-sentient`
- `paperclipai/paperclip`
- `ruvnet/ruflo`
- `tjx578/pydantic-ai-sentient` via evaluation patterns / Pydantic Evals
- `tjx578/transformers-sentient` for offline training/fine-tuning candidate lifecycle
- `GoogleChromeLabs/webmcp-tools` evaluation assets/patterns
- `nekuda-ai/WindTunnel` comparative WebMCP/browser-provider evaluation methodology

### CP9 — Technology Company OS

Integration only. CP9 does not bypass CP3–CP8 qualification, approval, or evidence requirements and does not create a new donor-admission shortcut.

## F. Recommended canonical register fields

Future donor records should minimally bind:

```yaml
donor_id:
repository:
upstream:
assessment_sha:
current_observed_head:
observed_at:
license:
source_domain:
checkpoint_owners: []
candidate_capabilities: []
adoption_decision:
authority_effect: NONE
runtime_effect: NONE
qualification_status:
evidence_refs: []
```

## Register verdict

`WARN`

Core roadmap reconciliation is supported, and all 11 S06 WebMCP reported revisions now pass independent exact-commit existence verification. Material limitations remain:

- WebMCP build/test/license/SBOM/security/runtime qualification is still `NOT_EXECUTED`.
- No S06 donor is admitted or runtime-active merely because its reported commit exists.
- `unlimited_book` still cannot be bound to an exact GitHub repository from the recovered source material.
- Some legacy donor assessment SHAs remain distinct from current upstream HEADs and must not be silently substituted.

## Canonical artifact locations and maintenance

- System goals, architecture, 28 specialists and CP0–CP9: [root README](../../README.md).
- Complete derived checkpoint/substep view: [roadmap](../architecture/roadmap.md).
- S06 original routing data: [donor-cp-matrix.csv](webmcp-donors/donor-cp-matrix.csv).
- S06 typed research representation: [portfolio.yaml](webmcp-donors/portfolio.yaml).
- Qualification ownership and limits: [Foundry](../architecture/capability-foundry.md).
- Frozen algorithm generation: [ALG-REG-001](algorithm-donors/README.md), unchanged.

A donor revision update preserves assessment revision and lineage, records
observed_at plus exact evidence, and reruns relevant qualification when bytes,
dependencies, scope or environment change. Update CSV/YAML/README routing
together; never let branch-local donor documents override the root SSoT.
