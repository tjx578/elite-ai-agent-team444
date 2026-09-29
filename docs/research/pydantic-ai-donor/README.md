# ARCH-DONOR-PYDANTIC-AI-01 — Pydantic AI donor research

## Status

`RESEARCH_ONLY / NO_RUNTIME_EFFECT / NO_AUTHORITY_EFFECT`

This file is a donor record, **not a roadmap**. All implementation ownership is
defined by the [Master Roadmap](../../architecture/roadmap.md).

- Repository: `tjx578/pydantic-ai-sentient`
- Reviewed revision: `05f2f35ca8af6f1382f06761c6a9a23dbd341728`
- Upstream: `pydantic/pydantic-ai`
- License observed: MIT
- Donor decision: `SELECTIVE_ADOPTION_HIGH_VALUE`
- Donor build/full test/live-provider integration: `NOT_EXECUTED`
- WOLF15 runtime effect: `NONE`
- WOLF15 authority effect: `NONE`

## Core decision

~~~text
Pydantic AI != WOLF15 Control Plane

Pydantic AI = model/provider/capability implementation donor
~~~

The full Pydantic AI `Agent` graph must not become a second orchestrator or
state owner. For CP1, the preferred pattern is the direct model request layer
(`pydantic_ai.direct`) behind WOLF15's own `sentient/model_gateway/`.

## Master CP routing

| Master CP | Donor material | Decision |
| --- | --- | --- |
| **CP1** | Direct model requests; Model/Provider/Profile separation; structured output; cancellation; timeout/retry taxonomy; usage and telemetry | **PRIMARY CURRENT DONOR SLICE** |
| **CP2** | RepoContext; semantic-boundary chunking; path/content-hash dedupe; ToolOutputLimits/spill patterns | FUTURE_CHECKPOINT -> DEFER |
| **CP3** | OpenTelemetry/instrumentation and durable execution ideas | FUTURE_CHECKPOINT -> DEFER |
| **CP4** | Realtime voice/audio/transcript patterns | FUTURE_CHECKPOINT -> DEFER |
| **CP5** | Progressive disclosure; deferred capability/tool loading; tool search | FUTURE_CHECKPOINT -> DEFER |
| **CP6** | Formal donor qualification of any code/provider/skill material | FUTURE_CHECKPOINT -> DEFER |
| **CP8** | Pydantic Evals dataset/case/evaluator/experiment/report separation | FUTURE_CHECKPOINT -> DEFER |

CP7 receives no direct authority from this donor. Tool/MCP capability present in
the donor is not part of CP1.

## CP1 extraction contract

Preferred target:

~~~text
Control Kernel
  -> Sentient reasoning
  -> sentient/model_gateway/
  -> PydanticAIDirectProviderAdapter
  -> Model / Provider / Profile
  -> real provider
  -> typed response
  -> WOLF15 ReasoningProposal validation
  -> evidence/controller checks
  -> Control Kernel
~~~

Required invariants:

~~~text
MODEL_OUTPUT != COMMAND
MODEL_OUTPUT != EVIDENCE
MODEL_OUTPUT != AUTHORITY
SCHEMA_VALID != FACTUALLY_VERIFIED
CAPABILITY_LOADED != CAPABILITY_AUTHORIZED
SEARCH_RESULT != QUALIFIED_TOOL
VECTOR_SIMILARITY != TRUTH
MEMORY != WORKFLOW_STATE
~~~

## CP1 donor acceptance topics

- schema-constrained output;
- cancellation that handles race/propagation correctly;
- timeout scopes that distinguish model request, tool/hook/MCP/run boundaries;
- retry taxonomy that does not retry policy denial as transient failure;
- usage accounting for input/output/cache/provider details;
- missing cost represented as `NOT_MEASURED`, not zero;
- model/provider/profile facts separated from WOLF15 authority.

## Knowledge/retrieval guidance for later checkpoints

The donor research recommends semantic/responsibility boundaries over fixed
line-count splitting, with roughly 800–1,800 tokens as a working chunk size only
when semantic completeness is preserved. Tests are evidence-on-demand rather
than default vector corpus content. API pointer/generated/large snapshot/VCR
material should not crowd the main semantic retrieval index.

These retrieval rules are candidate knowledge for CP2/CP5; they are not active
runtime behavior.

## Anti-patterns rejected

- full donor Agent as Control Kernel;
- automatic provider fallback in CP1;
- capability/profile/tool-search result becoming authority;
- planning/memory store becoming canonical workflow state;
- LLM judge becoming final verdict authority;
- untrusted MCP config becoming runtime authority;
- capability creation causing self-activation;
- missing price/cost becoming zero.

## Verification boundary

This record verifies only donor identity/source and architecture/research
mapping. It does not establish build success, donor test success, live provider
success, WOLF15 integration, performance gain, or capability qualification.
