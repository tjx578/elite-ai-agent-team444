# Architecture documentation contract

## Where decisions live

The [root README on main](../../README.md) is the system SSoT. Architecture
documents expand that design; donor registers own source identity and routing
details without defining an independent checkpoint sequence.

- [Canonical ownership](canonical-ownership.md): current-to-target responsibility
  map, ten invariants, README policy and UX prototype boundary.
- [Current State](current-state.md): implemented behavior and historical receipts.
- [Roadmap](roadmap.md): derived CP0–CP9/substep view, donor routing and entry/exit gates.
- [Repository donor register](../research/donor-adaptation-register-20260929.md):
  owner-supplied v1.2 portfolio and qualification dependencies.
- [WebMCP matrix](../research/webmcp-donors/donor-cp-matrix.csv): 11 source routing records.
- [North Star](super-intelligence-reference-architecture.md) and
  [target architecture](target-architecture.md): full product design.
- [Authority model](../governance/authority-model.md) and [ADRs](../adr/):
  permission boundaries and decision history.

Domain documents explain M2, M3-A, SCRS, Second Brain, Personal Assistant,
Capability Fabric/Foundry, production and learning. They do not activate those
targets. SK-01 is a catalog/governance lane, not installed skill proof.

## Maintainer contract

The root README owns system direction and global responsibility decisions.
This directory maintains the detailed responsibility map; subsystem READMEs
own local interfaces and limits. Resolve ownership conflicts in the root SSoT
and affected architecture/ADR records, then update local contracts. Do not silently choose
between duplicate target folder names by creating both implementations.

Every responsibility-changing PR includes README impact review. Verify relative
links, compare current claims with source, and keep evidence attached to exact
revisions. Historical PASS cannot qualify a new HEAD. No future empty subsystem
folders are required to make the North Star visible.

The nine CP0 local contracts cover `api`, `contracts`, `orchestration`,
`evidence`, `reasoning`, `cognition`, `agents`, this architecture directory,
and [tests](../../tests/README.md). The repository CI proves code/build checks;
it does not currently enforce this documentation policy automatically.
