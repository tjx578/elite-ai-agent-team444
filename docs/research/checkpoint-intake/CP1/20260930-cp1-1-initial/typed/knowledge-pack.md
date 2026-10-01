# CP1.1 typed donor knowledge pack

Status: KNOWLEDGE_EXTRACTED / PARTIAL_COVERAGE / NOT_ADMITTED. Source reading only; no donor code installed, imported, executed or tested. Exact refs, blob identities, content hashes, fetched coverage and narrower reviewed spans are in intake-receipt.json. Both owner IDs, parent and source match the manifest, verified live using authenticated account tjx578. No upstream substitution.

## Pydantic AI

Pinned owner tjx578/pydantic-ai-sentient (1394496138), main@05f2f35ca8af6f1382f06761c6a9a23dbd341728. Eleven files fetched, 219669 bytes. Nontruncated tree inventory; semantic coverage deliberately narrower than fetched bytes.

Source facts:
- output.py:129-242 separates ToolOutput and NativeOutput, tracks explicit names/schema-facing descriptions and strict mode, rejects negative per-tool retry count. NativeOutput strict mode is conditional on provider support. Schema mode is therefore a request capability, not evidence of runtime validation by itself.
- usage.py:456-623 distinguishes request limits checked before requests from token limits checked after responses. Pre-counting is optional. CostNotFoundWarning indicates configured cost cannot be enforced when cost is missing. This is a useful limitation, not a safe default to import unchanged.
- tests/test_usage_limits.py:45-87 provides source-level fixtures for request/input/output/total limit failures with a TestModel. These tests were read, not run.
- tests/test_settings.py:15-74 discovers provider settings types and checks provider-specific prefixes; shared settings do not erase provider-specific options.
- pydantic_ai_slim/pyproject.toml:59-95 declares dependencies including anyio, httpx2, pydantic, pydantic-graph and optional provider SDKs. LICENSE declares MIT. Package installation and transitive rights/security assessment were not performed.

CP1.1 inference/proposal:
- Freeze explicit schema/output mode, schema version, provider capability requirements, request deadline and bounded retry policy in native contracts.
- Distinguish requested mode from validated response outcome. Reject unsupported required modes rather than silently reducing the contract.
- Preserve unknown usage/cost as NOT_MEASURED and separate preflight estimates from provider-measured values. A warning-only cost gate is insufficient when a hard financial budget is required.
- Keep reusable contracts owned by contracts, cognitive validation in sentient/model_gateway and SDK-specific translation in models/providers. No Pydantic AI package adoption is proposed.

## OpenJarvis

Pinned owner tjx578/OpenJarvis-sentient (1365880169), main@fbbdb23c86627c18b859369b19746a9245f1ce0b. Eleven files fetched, 88214 bytes. Nontruncated tree inventory; only selected engine/types/prompt/test spans reviewed.

Source facts:
- core/types.py:14-103 models message roles, nullable content, tool-call payloads and a conversation cap; Message.text maps None to empty text. tests/core/test_types.py covers nullable content and window behavior.
- engine/_base.py:12-49 has an explicit context-length error subclass and conservative context-specific markers. Lines 99-120 estimate tokens using character count; tests/engine/test_base.py checks inclusion of tool/reasoning metadata.
- engine/_openai_compat.py:41-75 applies explicit/environment credential precedence and a timeout. Tests in test_openai_compat_api_key.py bind presence/absence of bearer headers and URL normalization.
- engine/_openai_compat.py:85-172 permits kwargs passthrough, retries a HTTP 400 with tools removed, embeds upstream error bodies in exceptions, and substitutes estimated/default token values for missing provider values. These patterns conflict with strict Sentient authority, redaction and NOT_MEASURED boundaries if copied literally.
- agents/prompt_loader.py:1-84 reads mutable filesystem prompt/few-shot overrides and returns None/[] on missing or failed reads. This is a design contrast to CP1.1 immutable/versioned prompt profiles; no path-traversal exploit is claimed from this bounded inspection.
- tests/engine/test_structured_output.py includes mocked JSON object/schema request propagation; this is test-source evidence, not provider acceptance evidence.
- LICENSE and pyproject declare Apache-2.0; dependencies include provider SDKs, datasets, telemetry and messaging packages. Full package/NOTICE/transitive review is pending and no package reuse is approved.

CP1.1 inference/proposal:
- Use typed, redacted provider outcomes with distinct timeout/context/schema/auth errors.
- Version and bind persona/prompt profile in the request; prevent arbitrary local override loading within the cognitive boundary.
- Keep unknown, measured and estimated usage distinct. Do not silently remove required tools/schema or resubmit a changed request.
- Retain conceptual adapter/message separation; rebuild narrow native contracts rather than copy the broad agent/engine runtime.

## Coverage and qualification

No executable SKILL source was studied; this is not a claim that such files do not exist. Two reconstructed development-review workflow candidates are proposals in skill-candidates.json. Full provider execution, durable runtime, lifecycle learning, comprehensive rights/security audit and package qualification remain NOT_EXECUTED. Donor tests were not run. No independent review is claimed by this author. Native CP1.1 contract design may use these findings after parent synthesis/review; donor code/package/skill admission remains deferred to CP6. ALG-REG-001 remains immutable.
