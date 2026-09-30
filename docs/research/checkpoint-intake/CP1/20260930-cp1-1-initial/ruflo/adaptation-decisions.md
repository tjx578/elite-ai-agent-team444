# Ruflo adaptation decisions

Mode: LOCAL_OWNER_DIRECTED_SOURCE; remote owner/fork identity NOT_VERIFIED. Admission NOT_EXECUTED.

| Pattern | CP1.1 decision | Native ownership / proof |
|---|---|---|
| Typed request/response and differentiated errors | LEARN_REBUILD_NATIVE | contracts schema; models/providers normalization; negative schema/error fixtures |
| Context/model/profile and cost descriptors | LEARN_REBUILD_NATIVE | sentient/model_gateway policy, contracts provenance/measurement states |
| Shallow isLLMResponse | REJECT_DIRECT_REUSE | schema validation must verify types, required fields, ranges and unknown handling |
| Missing price becomes0; fixed confidence0.7; stream completion100 | REJECT_AS_MEASURED_EVIDENCE | explicit NOT_MEASURED or ESTIMATED with versioned estimator; calibrate separately |
| Select first provider when all unavailable | REJECT_IN_CP1_1 | fail closed; authorized fallback policy remains separate |
| Raw request in error event | REJECT_DIRECT_REUSE | sanitized bounded receipt, no raw secrets/tool payloads |
| Health timers, caching/fallback, package execution | DEFER | beyond contract freeze; qualification/admission required |
| 268 skill paths | INVENTORY_ONLY | separate bounded source study before any candidate extraction |

No donor code or package is copied into Sentient. Native CP1.1 document can cite these source lessons; runtime implementation and capability admission remain later gates. New algorithm proposals enter future generation queue, never edit frozen ALG-REG-001. Local source study does not resolve canonical remote manifest identity; retain source override explicitly.
