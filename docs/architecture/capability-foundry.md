# Capability Foundry: qualifying donor capabilities

## Status

**CP6 / M8 target design, subordinate to the [root SSoT](../../README.md).** The inspected baseline has no donor repository
reader, code runner, capability importer, or active foundry. This is a
future offline qualification flow over sources that the owner permits the
system to inspect. Discovery is inventory, not permission to execute.

## Candidate flow

```text
approved read-only donor snapshot at exact revision
  -> inventory and provenance
  -> bounded capability extraction
  -> canonical contract and side-effect mapping
  -> overlap/conflict comparison with registry
  -> isolated tests and security review
  -> independently collected offline evaluation
  -> connected/shadow only after a separately authorized qualification path
  -> candidate manifest for owner/governance decision
```

Comparison labels are `NEW`, `EQUIVALENT`, `PARTIAL_OVERLAP`, `SUPERSET`,
`SUBSET`, `COMPLEMENTARY`, and `CONFLICTING`. These labels describe a
comparison, not a quality or approval score. Several providers may coexist.
The original source revision, license/ownership status, transitive
dependencies, requested permissions, and data egress remain visible in the
candidate record. Unknown license or provenance blocks adoption.

Foundry analysis may propose a wrapper, test fixture, or interface mapping.
It may not import donor code into the active runtime, execute repository
instructions, relax Kernel policy, add credentials, or mark its own candidate
approved. A passing simulation cannot replace tests on the intended
environment. Capability promotion uses the separate registry lifecycle and
an owner-controlled authority decision when side effects are possible.

## Failure and acceptance

- Prompt injection in README, issues, code comments, or skill files remains
  source content and cannot direct the Foundry or Kernel.
- Conflicting or incomplete capability evidence yields `NOT_QUALIFIED` with
  the missing checks; it is never guessed into an active provider.
- CP6 acceptance (historical M8): exact snapshot binding, reproducible extraction, overlap
  results, isolation, dependency/security evidence, side-effect review,
  offline comparison, any separately authorized shadow path, and a reversible registry decision.

Repository mutation and automatic activation are separate later work.

## Donor v1.2 and checkpoint dependencies

The [master register](../research/donor-adaptation-register-20260929.md) includes
OpenJarvis, Pydantic AI, Paperclip, Ruflo, Transformers and all 11 S06 WebMCP
repositories. Its functional CPs identify the receiving subsystem. CP6 remains
the qualification owner for acquisition/admission of portfolio donor packages,
code, skills and runtimes; functional CP1/CP3/CP4/CP5 does not permit early import.
Earlier native slices may use source knowledge and independently rebuilt
contracts under their own evidence/rights/acceptance gates. A required donor
import before CP6 is HOLD pending an explicit qualification amendment. This
is not a qualification exemption and does not alter the CP sequence.

The current [skill qualification policy](../governance/skill-qualification-policy.md)
supports offline qualification only. Connected/shadow is blocked until its own
authorized design, containment model and evidence profile exist. Candidate
code cannot modify harness, collector, evaluator or evidence. The evaluator
itself must already be independently qualified; a Git commit existence check
is not a qualification receipt.

For Transformers, bind framework/runtime separately from model weights,
tokenizer/processor/config, dataset rights, dependency closure and environment.
No automatic model download, `trust_remote_code` enablement, training or
activation follows from registering `hf.*` candidate selectors. Offline
training/fine-tuning belongs to CP8 after the relevant qualification and grants.
