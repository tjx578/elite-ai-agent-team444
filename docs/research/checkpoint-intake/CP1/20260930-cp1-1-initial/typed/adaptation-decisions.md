# CP1.1 adaptation decisions: typed donors

| Donor | Slice / owner | Decision | Verification before native implementation acceptance |
| --- | --- | --- | --- |
| Pydantic AI | CP1.1 schema ownership: contracts; cognitive gateway: sentient/model_gateway | STUDY_AND_REBUILD native typed request/response/output-mode and usage provenance contracts; no package/code reuse | Reject unsupported required schema modes, unknown fields, negative budgets and exhausted request budgets; missing usage/cost cannot become zero or PASS |
| Pydantic AI | Provider mapping: models/providers | DEFER actual SDK selection and live request proof to relevant later CP1 slice | Exact SDK rights/dependencies plus offline fixtures and separately authorized provider execution |
| OpenJarvis | CP1.1 persona/profile and provider outcome boundary | STUDY_AND_REBUILD explicit versioned profile and redacted errors | Prompt profile binding/drift fixture; mandatory credential absence rejection; nullable output/schema errors preserved |
| OpenJarvis | Mutable prompt overrides, tool-removal retry, raw provider error-body propagation, estimate as measured usage | REJECT literal reuse in CP1.1 | Exact-source/prohibition compliance mapping and negative fixtures |
| Both | Executable skills/code/packages | DEFER_CP6 / NOT_ADMITTED | Independent review, behavioral tests, rights/dependencies, authority scope, admission decision |

Source references and hashes: intake-receipt.json. Candidate proposals: skill-candidates.json. All candidate tool permissions are proposals only; activation_authority=false. No repository/runtime mutation occurred. No ALG-REG-001 edit. Partial coverage does not support full-donor qualification. Unread entrypoints, full provider adapters, arbitrary tools, durable execution and adaptive learning remain excluded from this study.
