# Phase 1.2 scope and support inventory

This inventory reconciles the 23-package starting set with the workspace and release order.
The machine sources are `pyproject.toml`, `packages/*/pyproject.toml`,
`release/publish-order.toml`, `release/support-matrix.toml`, and
`docs/acceptance/release-gate-1.2.toml`. `scripts/check_python_311.py` checks the workspace
membership, candidate Python range, classifiers, lockfile, CI matrices, and native selectors.
`scripts/check_release_gate.py 1.2.0` checks release package versions, changelog sections, and
the gate packet. The publish order includes every package directory and currently excludes none.

The reconciled order is:

1. `hedron-core`
2. `fastapi-workbench`
3. `hedron`
4. `hedron-docs`
5. `hedron-data`
6. `hedron-explorer`
7. `hedron-flask`
8. `hedron-django`
9. `hedron-jinja`
10. `hedron-conformance`
11. `hedron-extras`
12. `hedron-elements`
13. `hedron-posit`
14. `hedron-charts`
15. `hedron-maps`
16. `edron`
17. `hedron-native`
18. `hedron-mcp`
19. `hedron-gradio`
20. `hedron-sample-kit`
21. `hedron-notebook`
22. `hedron-sim`
23. `edron-sim`

`hedron-native` publishes through `native-wheels.yml`; the other 22 Python distributions are
built in the main release workflow. Versions come from each distribution's `pyproject.toml`.
Independently versioned satellites retain their own version lines. Existing compatibility rules
and coordinated dependency order are checked by the package and release verifiers.

## Frozen support matrix

| Area | Candidate claim | Source/check |
|---|---|---|
| Interpreter | Default-build CPython 3.11, 3.12, 3.13, 3.14; `>=3.11,<3.15` | `release/support-matrix.toml`; `scripts/check_python_311.py` |
| Static typing | BasedPyright 3.11 in `all` mode; Ruff `py311` | Root `pyproject.toml`; quality and typing CI jobs |
| Dependency bounds | Minimum and latest supported Stable dependency combinations | `release/support-matrix.toml`; dependency-bounds CI |
| Hosts | FastAPI, Flask, Django, Workbench, and in-tree Connect adapters | `scripts/ci_checks.sh`; CI and release workflows |
| Browsers | Chromium, Firefox, WebKit | CI and release browser matrices |
| Native wheels | CPython 3.11–3.14 on Linux x86_64, Linux ARM64, macOS, and Windows | `native-wheels.yml`; `packages/hedron-native/pyproject.toml` |
| Exclusions | CPython 3.15, PyPy, and free-threaded CPython | RFC-0099 and release packet |

The separately licensed live Connect Docker smoke is supplemental. In-tree Connect adapter and
contract tests remain in required CI. Workbench is the licensed required backend gate for the
release workflow.

## Reference dispositions

- Active package and scaffold metadata, check targets, native selectors, and CI matrices use the
  3.11+ contract; the phase checker rejects 3.10 package classifiers, direct `tomli` dependencies,
  and `cp310` native selectors.
- Active `typing_extensions` imports are retained for newer `override` and `TypeIs` APIs. The
  phase checker verifies a direct `typing-extensions>=4.10` dependency for each importing package.
- `uv.lock` may retain `tomli` under dependency markers for upstream tooling and `cp310-abi3` wheels
  for third-party dependencies. Those entries do not add Python 3.10 support to Hedron's own
  distributions; no Hedron native wheel selector uses `cp310`.
- Python 3.10 references in the superseded D-119, historical release metadata, archived evidence,
  and old compatibility baselines preserve prior release facts. The migration analyzer's 3.10
  source grammar is retained for inspecting older applications, not for running Hedron on 3.10.
- `check_python_310_candidate.py` automates explicit 3.10 candidate-install rejection and unpinned
  fallback to 1.1.3; its candidate-wheel digest and results are bound into the reproducibility
  ledger. The successful rehearsal is retained in `python-artifacts.json`.

## Ownership and review status

The evidence packet assigns functional owners by gate. Package `[project].authors` metadata is a
contact inventory, not proof of an accountable release maintainer, and one distribution does not
declare an author. Odos Matthews (`@eddiethedean`) reviewed and accepted this inventory on
2026-10-27. The review record, frozen source commit, reference scan, runtime, and artifact evidence
are retained in this directory; the shared full `source_commit` in both artifact ledgers identifies
the frozen candidate.
