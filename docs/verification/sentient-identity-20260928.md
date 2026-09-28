# Identity migration verification - 2026-09-28

## Verdict

**PASS_LOCAL** for the WOLF15 Sentient identity and namespace migration on PR-2.
Remote delivery remains unverified. The change is in the isolated managed
worktree on `codex/sentient-identity`, based on
`df43c93e12b2ff68ce4fe1c2d3778a6052886413`.

## Checks

| Check | Result |
| --- | --- |
| Source suite: `python -m pytest -q --junitxml=.pytest_cache/identity-source.xml` | 27 passed, 1 warning; 23.42 seconds |
| Wheel: `python -m pip wheel --no-deps --no-cache-dir --disable-pip-version-check --wheel-dir .pytest_cache/wheels .` | PASS using declared isolated build dependencies |
| Install wheel: `python -m pip install --no-deps --no-index --no-cache-dir --target .pytest_cache/installed <wheel>` | PASS |
| Installed suite: `python -m pytest -q -o pythonpath=.pytest_cache/installed --junitxml=.pytest_cache/identity-installed.xml` | 27 passed, 1 warning; 6.01 seconds |
| Installed package smoke: `python -I .pytest_cache/verify_identity.py` | PASS |
| `python -m ruff check src tests` | PASS after wrapping one longer import |
| `python -m compileall -q src tests` | PASS |
| `git diff --check` using repository line-ending configuration | PASS |
| Original PR-3 checkout preservation | All 38 inventoried file hashes, branch, HEAD, and status unchanged |

The installed smoke verifies distribution metadata, the origin of every imported
product module, absence of loaded legacy namespace modules, Uvicorn entrypoint
resolution, app factory identity, health output, task completion, and rejection
of WRITE authority. Wheel contents include the new namespace and exclude the
legacy package. Runtime AST comparison matches the renamed PR-2 baseline,
except the separately reviewed task-contract compatibility docstring.
The full suite retains transition, revision/exhaustion, correlation, and
side-effect containment checks and adds two identity contract tests.

## Source and environment binding

See [structured evidence](sentient-identity-20260928.json) for hashes, JUnit
counts, and dependency versions. Source inventory covers all Python files in
`src` and `tests`, package metadata, and the CI workflow. Its digest is SHA-256
of UTF-8 lines `relative/path + space + SHA256(raw file bytes) + newline`, sorted
lexicographically by forward-slash relative path. Documentation is excluded.

- Source manifest SHA-256: `e0d09e5eabde234ec6d493f97192483eb6f7928fc783390317e8d10f58b1a859`.
- Wheel SHA-256: `27868b4472362203ed422e8559082a7c8d492263da79883cf117bd9633cf1b89`.
- Python: 3.11.9 on Windows.
- Runtime/test dependencies reused the existing PR-3 virtual environment.
- The wheel was installed into this worktree's cache only; the existing
  environment was not reinstalled or upgraded.
- Build dependencies were resolved in pip's isolated temporary environment.

This proves installation against the observed dependencies, not a fresh runtime
dependency resolution or the Python 3.12/3.13 CI matrix. Test duration is not a
latency benchmark. JUnit durations and pytest console durations cover different
intervals; both are retained in their respective evidence.

## Observed failures and limitations

The first build attempt with `--no-build-isolation` failed because the existing
build environment lacked `bdist_wheel`. Normal isolated build then passed.
An installed import probe issued before installation was available failed;
it was rerun successfully after installation. The Starlette TestClient/httpx
deprecation warning remains visible in both final suites. No dependency warning
was suppressed and no test or validator was weakened.

The CI definition now uses a regular package installation and verifies the
installed identity with `python -I`. Remote CI for this migration is
**NOT_EXECUTED**. GitHub rename, push, PR creation, merge, and deployment were
not performed. Current remote repository/PR/billing status is **NOT_VERIFIED**.
Live-provider connectivity, model quality, latency, cost, and production state
are **NOT_MEASURED**. A fresh security scanner run was **NOT_EXECUTED**; review
here covers the rename diff and retention of the existing authority boundary.

The original PR-3 worktree remains separate with its previously verified
59-test adapter implementation. This migration contains the 25-test PR-2
baseline plus two identity tests. Porting PR-3, reorganizing subsystems, and
specifying the full specialist roster require later increments.

## Delivery snapshot binding

The tested working-tree source and wheel hashes were rechecked before commit.
Git normalizes some Windows CRLF line endings to LF. Every staged source blob
was compared with the tested bytes and differs only by that normalization.
The structured record contains the raw and Git source inventories separately.
The Draft PR description records the migration commit SHA and links to this
report and its structured evidence at that exact SHA. This avoids embedding a
self-referential commit hash in the commit itself.

Git source manifest SHA-256: `db52d21cd6f47bf762ed149e855c3c2742514904c85767a19594b3a79349a160`.

The status and non-execution statements above describe the local verification
checkpoint. Subsequent commit, push, PR, and CI observations are recorded in the
Draft PR description against its exact HEAD; they do not replace local evidence.
