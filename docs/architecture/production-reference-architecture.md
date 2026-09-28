# Production reference architecture

## Status

**M1-B target design, not a deployment plan.** The inspected `main` snapshot
has a local FastAPI app, in-memory deterministic workflow, and CI. It has no
authenticated caller boundary, durable task store, production database,
container/staging receipt, or production runtime evidence. A GitHub CI pass
does not establish any of those conditions. No cloud provider, region,
availability target, or cost budget has been selected here.

## M1-C trust foundation before a runtime rollout

The repository must establish explicit ownership and policy for protected
branches, reviews, dependency locks, reproducible builds, secret scanning,
dependency audit, type checks, package build, installed-package smoke, and
security regression tests. Each is a separate hard gate with its own receipt;
one aggregate score cannot compensate for a failed gate. The current CI
executes installation, pytest, and the installed identity check on Python
3.11–3.13. The other gates remain future work.
On 2026-09-28, the canonical GitHub `main` branch API reported
`protected: false` and zero effective branch rules. M1-C must close that
governance gap before any production claim; a green CI run alone does not.

## M5 read-only service target

```text
authenticated client
  -> ingress and bounded request validation
  -> Control Kernel with explicit READ_ONLY policy
  -> durable task/run/event store and idempotency boundary
  -> policy-checked read-only adapters
  -> source-bound response and sanitized audit receipt
```

The target store should distinguish task state, event history, approval
records, source references, and personal content by access policy. A
transaction or outbox boundary must prevent a task from appearing complete
without its event receipt. Idempotency keys and replay rules are needed
before any external write is introduced. A cache or message bus may improve
delivery, but it is not canonical truth.

Secrets belong in a managed runtime secret boundary and are never included
in task prompts, logs, evidence text, or memory. Readiness must check
authenticated dependencies and migration compatibility, not merely return
the current `/health` identity response. Structured logs, traces, metrics,
and incident receipts must bind a running artifact to source and config
versions without exposing sensitive data. Staging must precede production.

## Quality scenarios and gates

| Stimulus | Required target response | Evidence needed |
| --- | --- | --- |
| Duplicate task submission | One canonical run or explicit idempotent replay | Storage/transaction tests |
| Optional learning store outage | Baseline read-only task path remains bounded; missing context is visible | Fault-injection test |
| Auth or policy denial | No adapter side effect; sanitized denial receipt | Boundary test and audit receipt |
| Source revision changes mid-task | Pinned snapshot or explicit conflict | Replay and version-pinning test |
| Stale or unavailable source | Partial/blocked result with `NOT_MEASURED` | Freshness test |
| Deployment rollback | Restore an exact prior artifact without restoring revoked authority | Staging rollback exercise |

Latency, throughput, availability, recovery time, retention, and cost
targets are **NOT_MEASURED**. They need owner requirements and representative
workloads before service-level objectives can be set. Production Grade v1
means an authenticated, durable, observable, read-only cognitive service
after these gates are demonstrated; it does not include autonomous merge,
messaging, trading, or REE activation.

Deployment, Railway changes, production database writes, and broker actions
remain outside M1-B and require separate exact-artifact authorization.
