# Integrated identity migration verification — 2026-09-28

This record covers the WOLF15 Sentient namespace after the deterministic PR-2
kernel was integrated with the merged foundation. It supplements the original
[identity snapshot](sentient-identity-20260928.md), which remains bound to
commit `624d5ab` and its 27-test source and wheel results.

## Source binding

The tested source at integration commit `98cd31e` and the subsequent merge of
`main` at `064c051` have identical tracked content. The Git object IDs are:

| Object | Git ID |
| --- | --- |
| `src/` tree | `f4231582749ab961162cbf8977a3b4c66f690d51` |
| `tests/` tree | `ce967876ac24ee88623ec8443c8df496e4107923` |
| `pyproject.toml` blob | `38102fc98f5481dc781adf9d38a5f3837c2b19e0` |

Adding this report does not change those three objects. The original
source/wheel hashes in the earlier report describe the older snapshot and are
not assigned to this integrated source.

## Local results

- Source suite: **49 passed**, one Starlette TestClient dependency deprecation
  warning, on Windows Python 3.11.9.
- Ruff check: **PASS** for `src` and `tests`.
- Wheel build: **PASS** with standard isolated build dependencies. A preliminary
  `--no-build-isolation` attempt could not run because the local environment
  lacked `bdist_wheel`; the isolated build completed successfully.
- Installed-package suite from an isolated target directory: **49 passed**,
  one dependency deprecation warning.
- Isolated Python smoke: **PASS**. The imported `wolf15_sentient` module came
  from the installed target; distribution metadata, ASGI title, and health
  service identity matched `wolf15-sentient`.
- Built wheel: `wolf15_sentient-0.1.0-py3-none-any.whl`, SHA-256
  `b5b0c84ff2a12c00cb1493d6931aef5b740e1f21c630e5cfbae90c112af2b1cf`.

The wheel remains a local artifact, not an uploaded PR attachment. Remote CI
for the PR's final HEAD must be read from GitHub checks. No repository rename,
deployment, production action, learning activation, or additional runtime
authority was exercised by these checks.
