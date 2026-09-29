# Architecture documentation contract

## Where decisions live

- [Canonical ownership](canonical-ownership.md): current-to-target responsibility
  map, ten invariants, README policy and UX prototype boundary.
- [Current State](current-state.md): implemented behavior and historical receipts.
- [Roadmap](roadmap.md): checkpoint ordering and entry/exit gates.
- [North Star](super-intelligence-reference-architecture.md),
  [target architecture](target-architecture.md), and
  [Final Target Skeleton](final-target-skeleton.md): full product design and
  canonical target repository tree.
- [Browser Capability Plane / WebMCP](webmcp-browser-capability-plane.md):
  browser-native structured tool discovery/invocation, fallback boundary and
  checkpoint ownership.
- [Authority model](../governance/authority-model.md) and [ADRs](../adr/):
  permission boundaries and decision history.

Domain documents explain M2, M3-A, SCRS, Second Brain, Personal Assistant,
Browser Capability Plane/WebMCP, Capability Fabric/Foundry, production and learning. They do not activate those
targets. SK-01 is a catalog/governance lane, not installed skill proof.

## Maintainer contract

Architecture owns the global responsibility map; subsystem READMEs own local
interfaces and limits. Resolve ownership conflicts here and in an ADR when a
decision changes, then update affected local contracts. Do not silently choose
between duplicate target folder names by creating both implementations.

Every responsibility-changing PR includes README impact review. Verify relative
links, compare current claims with source, and keep evidence attached to exact
revisions. Historical PASS cannot qualify a new HEAD. No future empty subsystem
folders are required to make the North Star visible.

The nine CP0 local contracts cover `api`, `contracts`, `orchestration`,
`evidence`, `reasoning`, `cognition`, `agents`, this architecture directory,
and [tests](../../tests/README.md). The repository CI proves code/build checks;
it does not currently enforce this documentation policy automatically.
