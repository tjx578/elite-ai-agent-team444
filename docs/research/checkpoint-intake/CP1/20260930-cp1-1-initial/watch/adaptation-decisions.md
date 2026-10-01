# CP1.1 adaptation decisions: WATCH donors

Both donors remain WATCH_RESEARCH_NOT_ADMITTED. Neither is required as a runtime dependency.

| Donor | Decision | CP1.1 owner and allowed slice | Required native verification |
|---|---|---|---|
| LiteLLM | LEARN / REBUILD NATIVE CONTRACT | contracts: error and measured/unknown usage fields; models/providers: future normalization; sentient/model_gateway: bounded policy | auth/rate/timeout/context/schema outcomes; missing costs remain unknown; no raw error credentials; no cross-provider cost attribution |
| DeepAgents | LEARN / REBUILD NATIVE CONTRACT | contracts: prompt/profile/context schema; sentient/model_gateway: deterministic assembly; control retains workflow authority | missing profile fails boundedly; prompt version/order fixed; evidence not instructions; no implied tools from empty list; no automatic offload |

Deferred/rejected for this slice:
- LiteLLM package/proxy/Router/BudgetManager integration: DEFER_CP6_ADMISSION; persistence, routing and network effects exceed CP1.1.
- Missing response cost interpreted as zero: REJECT for Sentient evidence semantics.
- DeepAgents harness, filesystem/shell/subagents, memory and summarization backend: DEFER_OUT_OF_CP1_1.
- Universal170000-token fallback without model profile: REJECT as Sentient capability claim.
- New algorithm/skill candidate automatically activated or written into ALG-REG-001: REJECT. Frozen registry remains immutable; future candidate admission queue only.

No copied implementation or executable skill proposed. skill-candidates.json contains two KNOWLEDGE_ONLY records, both NOT_ADMITTED and activation_authority=false. Independent review and parent scope/baseline reconciliation are pending. Bounded study supplies design evidence; it does not establish tested integration, package trust, provider availability, cost calibration, or operational capability.
