# CP1.1 Transformers and TensorFlow bounded study

Status: BOUNDED_STUDY_COMPLETE / PARTIAL_COVERAGE / NOT_ADMITTED. This retry supersedes the acquisition gap, preserving the earlier failed attempt. Authenticated account tjx578, repository IDs, fork parent/source and current branch heads were independently checked. Exact revisions, blobs, hashes and reviewed spans are in intake-receipt.json. Six files fetched per donor; README and pyproject retrieval is not semantic review. No donor code, tests or models executed.

## Transformers

Owner tjx578/transformers-sentient, ID 1365875233; parent/source huggingface/transformers; main at 6b07e4510e3f9667f5256656118515bcde306fc4. Six files / 276714 bytes fetched.

- generation/configuration_utils.py:133-155 distinguishes generated-token limits from prompt length and documents max_time finishing the current computation pass after the allocation expires. stopping_criteria.py:93-115 uses time.time elapsed comparison when the criterion is called. Inference: this cooperative stop is not proof of a preemptive full-request deadline or cancellation guarantee. Native host deadlines and late-response rejection remain necessary.
- configuration_utils.py:647-710 validates some configuration independently of model inputs; strict defaults false and some combinations are logged as minor issues. At821-827 output flags can be ignored without return_dict_in_generate. Native contract must reject incompatible required settings, not treat configuration parsing as runtime support.
- stopping_criteria.py:22-42 describes prediction scores before/after softmax; modeling_outputs.py:659-683 carries optional attention/logit/cache values. These are generation/model tensors, not calibrated factual confidence or authority.
- stopping_criteria.py:618-642 combines criteria and only warns on conflicting max_length. Native profile resolution must be explicit and deterministic before dispatch.

Native proposal: bind tokenizer/model revision and generation profile when a local provider is eventually selected; enforce independent request/output/context limits; classify cooperative generation stop separately from host deadline. No local model loading or claim that Transformers is the first provider.

## TensorFlow

Owner tjx578/tensorflow_sentient, ID 1365873814; parent/source tensorflow/tensorflow; master at 08f0dca20e2b3de96fac23d679f1d3945255ec44. Six files / 103963 bytes fetched.

- signature_constants.py:21-31 names serving_default; load.py:821-873 and893-913 distinguish named callable signatures and loaded object interfaces. SavedModel signature shape is a compute interface; it does not supply a Sentient evidence/authority contract.
- load.py:1029-1054 rejects mismatched tags and exposes TensorFlow version metadata. A useful native lesson is explicit artifact/signature/runtime-version binding, with adapter-specific failures normalized outside model output.
- load.py:1078-1103 continues loading when fingerprint is absent or unreadable. Native mandatory artifact identity cannot use this permissive path as provenance acceptance.
- save_options.py:133-141 permits all namespaced ops without a whitelist and can save debug stack information. These are future package/isolation/privacy review concerns; no vulnerability or executed side effect is claimed.
- types/core.py:169-208 distinguishes concrete functions from polymorphic functions that may create specializations. Future local backend contracts must bind input signatures and runtime environment, rather than equate callable presence with reproducibility.

TensorFlow remains compute/backend knowledge input, not an automatic conversational provider. Model artifacts, runtime dependencies, kernels, performance and rights require separate qualification.

## Coverage and evidence limits

Only spans listed in receipt were studied. Apache-2.0 declarations were observed; full license/NOTICE, transitive dependency, model-weight rights and security review remain NOT_EXECUTED. No executable skill source was assessed, no package installed and no model downloaded. All runtime tests, latency/cost/quality measurements and admission remain NOT_EXECUTED. Acquisition used 30-second subprocess timeouts and each donor completed below the 300-second acquisition bound; this is collector instrumentation, not provider timeout evidence.
