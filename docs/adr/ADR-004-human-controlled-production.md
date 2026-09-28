# ADR-004: Human-Controlled Production

- **Status:** Accepted
- **Date:** 2026-08-24
- **Implementation status:** Normative safety boundary

## Context

Repository changes, merges, deployments, production data mutations, and operations on high-criticality systems can cause irreversible harm. A successful analysis or test run is not sufficient authority for those actions.

## Decision

Agents cannot merge to a protected/default branch or perform production actions without explicit, action-specific owner authority enforced outside model reasoning.

Authority is least-privilege, task-scoped, target-scoped, time-bounded where practical, and checked again at the execution boundary. It is never inferred from project mode, model output, a readiness label, access to credentials, or an earlier approval for a different action.

Default operation is non-mutating. The intended delivery ceiling before a separate owner decision is an isolated change, tested feature branch, or draft pull request.

Production actions include deployment, secret or environment mutation, production database writes, destructive infrastructure operations, and domain-specific real-world actions such as submitting broker orders.

## Consequences

### Positive

- owner intent remains the final decision boundary;
- compromise or hallucination has a smaller blast radius;
- audit records can connect an approval to the exact attempted action;
- readiness assessment remains separate from execution authority.

### Costs

- workflows can pause for approval;
- approval and resume need durable, replay-resistant design;
- production automation requires an additional controlled system.

## Guardrails

- No direct push to the default branch.
- No autonomous merge.
- No production deployment or mutation from a generic task prompt.
- No destructive command without explicit, scoped confirmation.
- Credentials do not confer permission.
- Approval must identify target, action, artifact/version, and relevant environment.
- Material changes after approval invalidate that approval.
- Every attempted external or production action, including one denied at its
  execution boundary, emits a sanitized trace event when that adapter exists.
  HTTP request validation failures in the current foundation return 422; the
  foundation has no external execution adapter or durable audit store.

## Alternatives rejected

- **Model decides when production is ready and deploys:** conflates assessment with authority.
- **One broad standing approval:** cannot preserve task or artifact scope.
- **Credential possession as authorization:** makes secret exposure equivalent to owner consent.

## Verification

Policy tests must prove denied-by-default behavior, scope mismatch rejection, expired or replayed approval rejection, artifact-change invalidation, default-branch protection, and sanitized audit evidence.
