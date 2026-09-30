# Ruflo local donor study for CP1.1

Source mode LOCAL_OWNER_DIRECTED_SOURCE. User directed local D:\REPO CLONE instead of implicit upstream fallback. Exact clean clone HEAD f547cec013041a59b2f18921f5c861bf3d525825; canonical Sentient base45d5c8df123b27c6bf7c781139db41154b6e1d4d. Local remotes name tjx578/multiagentruflo and ruvnet/ruflo, but these are SOURCE_CLAIM from git config, not live identity verification. Repository ID and remote fork ancestry NOT_VERIFIED. Parent's earlier visible owner inventory did not resolve a matching fork; local source authorization permits this study without claiming remote identity repaired.

9 exact Git blobs,85042bytes acquired and hashed. Every local file matches its Git blob SHA-1 and has SHA-256 in receipt. Source acquisition used subprocess timeout30seconds and finished in about3seconds; no donor execution/install/clone. See intake-receipt.json for paths/blobs/study spans. Study status PARTIAL_COVERAGE; this is a bounded provider-contract slice.

## Source facts

Paths below are relative to v3/@claude-flow/providers unless stated otherwise.

- src/types.ts:139-211 defines request/response, optional requestId and metadata, tool choice, token usage, optional cost and finish reason. src/types.ts:248-294 distinguishes rate limit (retryable) from authentication/model-not-found (nonretryable). src/types.ts:300-375 describes provider health/model/cost interfaces. These are useful distinctions for native contracts; their presence does not prove runtime implementation correctness.
- src/types.ts:410-419 response guard only checks object plus id/content/provider property existence. It does not validate value types, usage completeness or schema conformity. Native validation must be strict enough to reject malformed provider payloads.
- src/base-provider.ts:385-426 returns zeros when pricing is missing, otherwise estimates tokens as ceil(characters/4), with fixed confidence0.7. These are heuristic/default values, not calibrated evidence. Sentient must preserve unknown pricing and label estimates with method/version; confidence must not silently become factual certainty.
- src/base-provider.ts:166-181 initialization optionally starts scheduled healthchecks and always calls an initial healthcheck. src/base-provider.ts:236-240 emits the request with an error event. Do not transplant lifecycle or raw request emission into a design-only gateway slice.
- src/provider-manager.ts:151-290 performs selection, optional caching and fallback. When no providers report available, selection tries the first provider anyway at220-221. Cost selection compares estimated totals without measuring their confidence. This is unsuitable as a fail-closed Sentient availability contract.
- src/openai-provider.ts:194-219 uses AbortController/timeout for fetch, but clears timeout before response.json. At256-279 streaming final usage estimates prompt size and assigns completionTokens100; missing pricing becomes zero. Native acceptance must cover body/stream deadline, cancellation and explicit estimated-versus-measured usage.
- src/__tests__/provider-integration.test.ts:1-76 loads dotenv, uses actual credentials, skips tests when keys unavailable and logs response/usage/cost. Source was read only; no .env read and no test execution. Presence of integration tests is not observed provider PASS.
- Root LICENSE is MIT with notice retention. Root package claude-flow3.5.48 uses zod/semver plus optional agent/vector modules; provider package3.0.0-alpha.6 uses events, Node>=20 and optional @ruvector/ruvllm. Dependency safety, exact lockfile reproducibility and legal admission NOT_EXECUTED.
- README headings/features were indexed only. Do not promote cost-optimization marketing into benchmark evidence.

## Native CP1.1 design input

Proposal: contracts owns a versioned immutable request and response schema. Request includes explicit provider/model/profile versions, evidence references, deadline and policy budget; requestId is required for traceability. Response differentiates measured usage, estimated usage and NOT_MEASURED, plus sanitized typed error. models/providers translates provider payload, sentient/model_gateway enforces cognitive policy, control retains workflow/authority ownership.

Persona/prompt profile and model identity belong to explicit config with provenance, not defaults inferred from donor model lists. This local code contains model/version names that are historical source claims; they do not prove provider availability today.

Acceptance proposals: reject malformed response field types; missing pricing stays unknown; estimated streaming completion count never treated as measured; unavailable provider fails without implicit fallback; timeout covers full response consumption; cancellation propagates; failure receipts exclude raw request/body/credentials; cost/confidence must not grant authority.

## Skills and coverage

268 SKILL.md paths enumerated in the exact tree; contents were not studied. Therefore no existing skill source is extracted or qualified. One KNOWLEDGE_ONLY candidate documents the native contract lesson. NO_REUSABLE_SKILL_FOUND_IN_INSPECTED_CONTENT is scoped to the9 source files, not a claim the repository contains no skills.

Other adapters, security implementations, middleware, memory, swarm/learning and full tests remain outside the bounded slice. Independent review pending. ALG-REG-001 remains immutable. No runtime capability, admission, installation, activation or authority change.
