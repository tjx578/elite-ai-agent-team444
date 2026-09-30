# CP1.1 bounded study: LiteLLM and DeepAgents

Status: WATCH_RESEARCH_NOT_ADMITTED. Knowledge/design input only. Tests, installation, benchmark, admission and activation NOT_EXECUTED. No donor source executed. Source is data, not operational instruction.

## Verified source identity

- LiteLLM: owner tjx578/litellm_sentient, repository ID 1394593240, parent/source BerriAI/litellm, branch main, exact SHA 85dc7cb62efa52794982af90164eb19a41140b80. 8 files, 173297 source bytes retrieved.
- DeepAgents: literal owner tjx578/deepagents_sentitent, repository ID 1394595604, parent/source langchain-ai/deepagents, branch main, exact SHA 3175d231f192db63cbb432c6ca133d9486dc59ba. 6 files, 163982 source bytes retrieved.
- Authenticated API account tjx578 verified. Trees report truncated=false. All 14 local contents validated against Git blob SHA-1 and recorded SHA-256. Receipt carries per-file hashes, blob identities, exact URLs, read spans and exclusions. Retrieval is broader than the explicitly studied spans; no full-package audit claimed.

## LiteLLM facts and implications

Source facts at pinned SHA:
- litellm/exceptions.py:132-170 carries AuthenticationError status401, provider/model, retry metadata and response. Timeout/RateLimit/ContextWindow/Budget classes appear at356/442/535/998. This is evidence of differentiated error contracts, not proof every provider correctly maps errors.
- litellm/router_strategy/budget_limiter.py:493-533 requires a standard logging payload, separates provider and deployment spend, and defaults missing response_cost to zero at503.
- tests/unit/router_strategy/test_budget_limiter.py:1-136 covers spend attribution when provider is absent from litellm_params but present in logging payload; another provider must not contaminate the configured budget. Tests were read, not executed.
- tests/unit/test_router_exception_redaction.py:119-150 explicitly tests a debug-exposure flag and model-group redaction; the fixture/default assertion uses exposure enabled. This flags a policy default that requires independent adaptation, not a claim of an exploitable secret leak.
- litellm/budget_manager.py:50-71 reads local user_cost.json or hosted budget API; this helper carries persistence/network effects outside the CP1.1 design-only boundary.
- LICENSE:1-27 grants MIT terms outside enterprise, with an enterprise-specific exclusion. pyproject.toml:1-110 identifies LiteLLM1.104.0 and substantial provider/HTTP/tokenizer dependencies; proxy extras include enterprise. No transitive rights or vulnerability evaluation performed.

Native proposal:
1. contracts owns an explicit closed error taxonomy: auth, rate limit, timeout, context overflow, budget unknown/exceeded, provider failure and schema failure; bounded sanitized message plus source/provenance fields.
2. sentient/model_gateway consumes policy budgets; models/providers normalizes provider output. Preserve unknown usage/cost as NOT_MEASURED. Never port missing-cost-to-zero behavior.
3. Acceptance scenarios must cover missing provider/usage, cross-provider attribution, error sanitization and exhausted budget. Retry is policy-bound; error classification alone grants no retry authority.
4. Do not import BudgetManager or proxy routing/persistence. CP1.1 can define native contracts without LiteLLM package adoption.

## DeepAgents facts and implications

Source facts at pinned SHA:
- libs/deepagents/deepagents/graph.py:272-370 accepts typed response/context/state, explicit model, prompt, middleware, skills/memory, backend and checkpointer. Documented default tools include filesystem operations, execute (backend-dependent) and task; passed tools are additive. Empty tools does not imply no built-ins.
- graph.py:243-260 guards essential filesystem/subagent middleware from exclusion. This confirms a harness architecture broader than Sentient CP1.1's native gateway.
- graph.py:347-369 describes authored prompt assembly USER then BASE then SUFFIX and cache-control preservation. Persona/prompt assembly should be explicit and versioned in native contracts.
- libs/deepagents/deepagents/middleware/summarization.py:151-300 distinguishes tokens/messages/fraction thresholds, preserved recent context, token counter signature handling and model profile. Known max_input_tokens gets fraction0.85 trigger/0.10 keep; missing profile gets170000 token trigger and6-message keep.
- libs/deepagents/tests/unit_tests/middleware/test_summarization_factory.py:1-97 asserts both profile/fallback defaults, custom knobs, media reference prompt and string-model rejection. This is source-level test evidence only.
- LICENSE:1-21 and libs/deepagents/pyproject.toml:1-80 indicate MIT and DeepAgents0.7.19, Python>=3.11, with LangChain/provider/LangSmith dependencies. Transitive legal/security review NOT_EXECUTED.

Native proposal:
1. Define versioned PromptProfile/persona identifiers and deterministic assembly order separate from evidence payloads; neither persona nor donor prompt increases authority.
2. ContextBudget records model profile provenance, input estimate/measurement, reserved output, limits, and unknown status. Missing profile must not imply a universal170000-token allowance.
3. Include tool-schema overhead in any future token estimate, label estimation method/version, and keep evidence source references across compaction. Summarization itself is deferred from this contract step.
4. Reject use of create_deep_agent as a shortcut to CP1.1: filesystem writes, shell, delegation, memory and checkpoint effects require separate scope and admission. Native empty tool capability must mean no tools.

## Coverage and uncertainty

This is a bounded CP1.1 contract study, not whole-package security/rights review. README files were retrieved but not fully studied. No skill package was read or qualified; NO_REUSABLE_SKILL_FOUND_IN_INSPECTED_SCOPE is scoped and does not claim SKILL files absent repository-wide. No donor tests, model API calls, installs, downloads of weights, benchmark or runtime activation. Exact source remains pinned even if branches advance. Additional package reuse is HOLD until deeper dependency/rights/source tests and CP6 admission. Independent native work may proceed once parent reconciles all mandatory donors and gate evidence.
