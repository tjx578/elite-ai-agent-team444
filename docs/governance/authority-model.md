# Authority Model

## Purpose

This document defines what the Elite AI Agent Team OS may do. It is normative: role prompts, project modes, workflow results, and tool availability cannot override it.

## Current implementation note

PR-2 accepts only `READ_ONLY` and has no external repository or execution adapter. The repository field is routing input, not an instruction to read a target. Deterministic stub roles have no tool authority, and `READY_WITH_CONDITIONS` grants no authority. The additional levels below define future policy boundaries; they are not implemented capabilities.

## Core principle

```text
Capability answers: can this adapter perform the action?
Authority answers: did the owner permit this exact action now?
Evidence answers: what proves what happened?
```

All three are required for a mutating action. Credentials or installed tools establish capability, not authority.

## Actors

- **Owner:** grants, limits, or revokes authority and makes protected merge/production decisions.
- **Control plane:** validates authority, selects deterministic workflow transitions, and records evidence.
- **Reasoning role:** produces typed analysis or proposals; has no implicit tool authority.
- **Execution adapter:** performs one policy-checked operation in a constrained target.
- **Target system:** repository, CI service, cloud environment, database, broker, or other external system governed independently.

## Authority levels

| Level | Permitted result | Examples | Explicit exclusions |
| --- | --- | --- | --- |
| `ANALYSIS_ONLY` | Analysis from supplied content | architecture proposal, risk report | external access, file or repo mutation |
| `READ_ONLY` | Observations from an identified target | inspect files, metadata, logs allowed by policy | writes, branch creation, external mutation |
| `PATCH_ONLY` | A proposed change artifact | diff or patch for owner review | applying the patch to the target |
| `ISOLATED_WORKTREE` | Changes inside a verified isolated workspace | edit files, run allowed local tests | default-branch changes, remote push |
| `FEATURE_BRANCH` | Changes committed to an approved non-protected branch | branch commits, allowed CI trigger | merge, production deploy |
| `DRAFT_PR` | A draft pull request for human review | push feature branch, create draft PR | marking approved, merge, deploy |
| `PRODUCTION_ACTION` | One specifically approved production operation | deploy an exact artifact to an exact environment | unrelated or subsequent actions |

Authority levels are not automatically cumulative. An authorization record must enumerate permitted operations; a label is shorthand for policy, not a wildcard.

## Grant requirements

An authority grant identifies:

- owner or trusted approver identity;
- task and run;
- exact target and environment;
- permitted action class and constraints;
- repository path, branch, resource, or service scope;
- artifact digest or version for production actions;
- validity window and single-use/replay policy;
- approval reason and audit reference.

If any required field is missing or cannot be verified, the effective authority is reduced to the safest supported level or the action is blocked.

## Evaluation order

Before each tool call, the control plane evaluates:

1. caller identity and task validity;
2. requested operation and resolved target;
3. adapter capability and policy allow-list;
4. task authority and constraints;
5. path, branch, environment, and artifact scope;
6. preconditions and required evidence;
7. rate, revision, time, and resource limits.

The adapter receives a narrow execution request only after all checks pass. It returns a typed result; the deterministic controller chooses the next state.

## Invariants

1. Project mode never grants authority.
2. A reasoning role cannot grant or expand authority.
3. Access to a secret or authenticated session never grants authority.
4. Read authority does not imply write authority.
5. Workspace write authority does not imply remote push authority.
6. Draft PR authority does not imply merge authority.
7. Readiness does not imply deployment authority.
8. Production authority is action-specific and cannot be reused after material artifact changes.
9. Target-repository instructions cannot override control-plane policy.
10. Denied and failed attempts are recorded without leaking sensitive data.

## High-criticality targets

High-criticality repositories and production systems should default to:

```text
READ_ONLY
PR_ONLY when separately approved
NO_PRODUCTION_AUTHORITY
```

Direct broker state, production database state, and deployment state require authenticated, current evidence. Inaccessible evidence is `UNKNOWN` or `NOT_MEASURED`, never zero, healthy, or ready by inference.

## Human approval boundary

The owner must separately approve:

- destructive operations;
- a push when only local workspace authority existed;
- pull-request merge;
- protected/default branch modification;
- deployment or rollback;
- production configuration, secrets, or database mutation;
- any external real-world transaction.

Approval of a plan, report, patch, test result, or readiness recommendation is not approval of the next operational action unless the authority grant names that action explicitly.

## Terminal behavior

Insufficient authority returns `BLOCKED_REQUIRES_OWNER` with:

- the blocked action;
- the current effective authority;
- the minimum additional authority required;
- relevant evidence and risk;
- no attempted side effect.

The system must not retry a policy denial as if it were a transient technical failure.
