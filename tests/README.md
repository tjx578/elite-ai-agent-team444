# Verification contract

## Ownership and coverage

Tests provide reproducible offline evidence for the current source. They do not
grant authority or certify a live provider, deployment, statistical calibration
or skill qualification.

| Suite | Responsibility |
| --- | --- |
| `integration/test_api.py` | In-process FastAPI identity, strict input, routing and workflow responses |
| `unit/test_workflow_invariants.py` | Kernel transitions, role failures, bounded revisions, correlation and authority |
| `unit/test_evidence_runtime.py` | M2 digest/scope/revision/freshness/conflict and missing evidence |
| `unit/test_reasoning.py` | M3-A routing, evidence bridge, binding, schema/reference rejection and adapter failure |
| `unit/test_cognitive_reflex.py` | SCRS equations, finite numbers, full-profile binding and event lifecycle |
| `unit/test_learning_contracts.py` | Learning data invariants, required evaluation/approval references and authority escalation denial |

## Reproduction

Run from the repository root with the committed lockfile:

```powershell
uv sync --locked --extra dev
uv run --locked --extra dev python -m pytest
uv run --locked --extra dev ruff check .
uv run --locked --extra dev pyright src tests scripts
```

Use `python -m pytest` rather than executing individual files. Pytest config
selects `src` and `tests`. Focused runs select one file; full acceptance uses the
whole suite. Fixtures, adapters and profiles are synthetic/offline. For a
read-only source review use `-B` and `-p no:cacheprovider` with an existing locked
environment, recording interpreter and exact source paths.

## CI and evidence

[CI](../.github/workflows/ci.yml) runs pytest on Python 3.11/3.12/3.13, Ruff,
Pyright, sdist/wheel build, isolated installed-package identity, dependency
audit and secret scan. [CodeQL](../.github/workflows/codeql.yml) separately
analyzes Actions and Python for main-targeted PRs and main pushes. Each required
job must actually execute. Local results, PR results and resulting-main results
are separate receipts tied to their exact SHA. A neutral aggregate is not a
substitute for required successful jobs.

Changing a responsibility requires reviewing the owning README and adding or
adjusting meaningful behavior tests. Do not weaken validation to make CI green.
Source gates cannot establish production authentication, live transport,
durability or model quality; those require later checkpoint evidence.

[Canonical ownership](../docs/architecture/canonical-ownership.md) decides
global ownership; this README describes the verification boundary.
