# Source Provenance — Algorithm Donor Assessments

## Report provenance

The ARCH-ALG assessments were produced from source-level reviews of legacy Python donor files and recorded in the project conversation/document lineage named `Rancangan Otak WILF15 Sentient.txt`.

Current known report grouping:

- **ARCH-ALG-01** — Cognitive / Constitutional Algorithms.
- **ARCH-ALG-02** — Neural Orchestration / Capability Algorithms.
- **ARCH-ALG-03** — Reflective / Pipeline / Evaluation Algorithms.
- **ARCH-ALG-04** — Cognitive Lifecycle / Contracts / Tools / Runtime Tests.
- **ARCH-ALG-05** — Reasoning Graph / Policy Guard / Temporal Evaluation / Explainable Fusion.

## Important evidence note

The batch reports are **design assessments**, not runtime qualification receipts. Source review may establish that a pattern is useful or defective; it does not establish that a donor package is safe, compatible, licensed, tested, or qualified for WOLF15 runtime.

## Local donor source

The owner reported the donor source corpus is available under `D:\Python`. This documentation package does not copy that donor corpus and does not assert that every local donor file has been content-hashed into the repository yet.

## Canonicalization rule

When this package is adopted into the repository, each donor source used for an implementation should gain an immutable provenance record:

```text
source_file
source_sha256
source_repository (if any)
source_revision (if any)
assessment_batch
algorithm_ids
```

Duplicate source bytes should map to one donor family, not multiple algorithm providers.


## Verified package receipt

Full ZIP SHA-256: fadc573aaf91e31a3dca81787ff6a9a99c3a0c8ffa8897251caabbdd1d600425

Seven-document ZIP SHA-256: fb3f24397747eed272a0c7c1da4561f15022ed7a29534f7138406875148f9b96

All seven shared members are byte-identical. All six earlier individual files
match their package members. Hashes below bind original input bytes; repository
copies may include reconciliation notes and whitespace normalization.

| Input member | SHA-256 |
| --- | --- |
| PACKAGE_MANIFEST.md | 443e07ca5e08fd97cf01fe95d8f65f2bbf9ef54022627d26846d4695522166f1 |
| docs/architecture/algorithm-adoption-canon.md | e1bc33d9a1e1a203b0b6964654a7dbfb49fb297f3d1c0d9375e95c13cbdf3546 |
| docs/research/algorithm-donors/README.md | a422ba2745de00745d1fa6dde88e0e2d65813ef05fa7130f5d3a86341a97b67e |
| docs/research/algorithm-donors/adoption-registry.yaml | 77841140b4a1718d894a389469b88a030bdf3c30739e43c4643a1cc4beab7fbc |
| docs/research/algorithm-donors/anti-pattern-registry.md | 21b00be56b0fd7e581eb7caf3098f56a7aa135965d1664c472885e9082bc2e96 |
| docs/research/algorithm-donors/batch-01-cognitive-constitutional.md | 563a258946b0946ee311b4940f5d6ea8eb1783b95642f3008dbbf10348445b30 |
| docs/research/algorithm-donors/batch-02-neural-capability.md | 59810f7856488f2a6645d2d76d82a9392577bba2ebdcb333fc59b4306a13c1d5 |
| docs/research/algorithm-donors/batch-03-reflective-evaluation.md | 3771f5d322c42efb7c11c7fb9acd80e4369d5134bc3732d86d1bae398221aa4b |
| docs/research/algorithm-donors/batch-04-cognitive-contract-runtime.md | 8d3b0688de77e9687e8829d2e19ac6b7467605070baa197e840239035f2212bb |
| docs/research/algorithm-donors/batch-05-reasoning-policy-evaluation.md | 5fd2b8be874ed01a69aaa4b98e02bf85f02bd62a930972b14ba25c31919c9c57 |
| docs/research/algorithm-donors/checkpoint-adoption-matrix.md | f2089151f96da339a436135b2325d15e1ae11a8ded08504f6caaa10991f7a4c7 |
| docs/research/algorithm-donors/codex-desktop-implementation-contract.md | b3510b8fdcd1b63978e5a785973f3d588527f9e6353250610d2543856d2960bd |
| docs/research/algorithm-donors/source-provenance.md | 1d65da1db5f67fd69bc1dce2990401ac56bb6862762cca8531c632653259af8e |

## Reconciled provenance

The owner designated these package documents as canonical for this task;
older chat snapshots are no longer required for documentation reconciliation.
Precedence is batch document, source-provenance, package YAML, then local
inference. All 31 original records remain unchanged under source_proposal.
origin and batch_provenance identify design attribution and recovered records.

The four additional original-scope records are RECONCILED_DESIGN. The two new
telemetry records are BATCH_DOCUMENT_SUPPORTED by the explicit batch-02 list.
None of these labels establishes donor qualification.

### Resolved differences

- Converter design spans batch 02 toolpack, batch 03 ingestion and batch 04
  typed tools. technical_data_processor in the prior batch-04 inventory is
  supplementary historical evidence; examples are not assigned to every batch.
- Named ContractSurfaceValidator/ImportPreflight provenance is batch 05.
  Batch 03 supports generic compatibility qualification. Its original YAML
  label remains preserved as a source claim, not named-validator provenance.
- TelemetryPersistenceAnalyzer is explicit in batch 05. The prior pattern_reporter
  mapping from batch 03 remains a related local inference.
- ProcedureSelector's batch-04 attribution relies on the supplied registry and
  the historical inventory; the short package summary gives the lifecycle
  family rather than naming that class.
- Batch-02 early REE/evaluation references support the family of bounded/replay
  candidates; batch 01 explicitly names the extracted optimizer/replay methods.
- CP1 bounded model-adapter placement and CP6 overlap detector are reconciled
  designs from the owner brief, not additional original package YAML records.

Exact uploaded-source identity remains separate. The prior 59 historical
references, 67 unique local digests and one exact-byte alias are preserved.
Original-upload equivalence and usage rights remain NOT_VERIFIED/NOT_MEASURED.
These are implementation/admission prerequisites, not missing package documents.

See [local observations](local-source-observations.md) for supplementary static
findings. Complete package receipt does not prove donor runtime readiness.
