# Capability Foundry: qualifying donor capabilities

## Status

**M1-B target design.** The inspected baseline has no donor repository
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
  -> offline or shadow evaluation
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
- M8 acceptance: exact snapshot binding, reproducible extraction, overlap
  results, isolation, dependency/security evidence, side-effect review,
  offline/shadow comparison, and a reversible registry decision.

Repository mutation and automatic activation are separate later work.
