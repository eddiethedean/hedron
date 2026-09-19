---
type: reference
title: Test Topology
description: How Hedron maps focused tests and full local check suites to package, security, browser, release, and documentation contracts.
tags:
  - testing
  - verification
  - operations
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T17:40:19.225Z
sources:
  - id: openwiki-source-000a7add03cfbd0ac1794f3a
    resource: repo://docs/CONTRIBUTING.md
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-2faef51cd0bcbe4bb5eaae2d
    resource: repo://scripts/ci_checks.sh
  - id: openwiki-source-7f83bf935479aabc34d5f6d2
    resource: repo://tests/a11y/test_charts_038_a11y.py
  - id: openwiki-source-2b238cbb7442b3a63995e502
    resource: repo://tests/browser/test_charts_038_render.py
  - id: openwiki-source-741bbab04f6ee71f3e5410f8
    resource: repo://tests/ops/test_release_gate_evidence.py
  - id: openwiki-source-0926487af97d5a24d272aa4e
    resource: repo://tests/performance/test_w025_dataeditor.py
  - id: openwiki-source-dc057e8bd8ebd387c0b7da91
    resource: repo://tests/scripts/test_check_realwb_029.py
  - id: openwiki-source-4c93d59f8c5ef77256a1be62
    resource: repo://tests/upgrade/phase_1_0/negative/invalid_interaction.py
generated: { by: "codex", at: "2026-09-19T16:47:17.741Z" }
---

# Test Topology

Hedron's tests are organized around the kind of contract being protected, not
only around the package that owns the implementation. Start with the narrowest
directory or test file that covers a change, then widen to the shared suite when
the change crosses a public, security, adapter, or packaging boundary.

## Focused lanes

The default pytest discovery includes `tests`, `examples`, and the
`hedron-docs` test package. Pytest uses importlib mode and xdist's load-file
distribution by default. The shared test command adds strict configuration and
strict-marker validation, so an unknown marker or malformed pytest setting is a
failure rather than a warning.

Use the following lanes as the first signal for a change:

| Change or contract | Focused lane |
| --- | --- |
| Core/runtime behavior | `tests/unit` or the specific unit test file |
| FastAPI/application integration | `tests/integration` |
| Flask, Django, Jinja, Posit, Workbench, or other hosts | `tests/adapters` |
| Auth, CSRF, headers, URI, and tenant behavior | `tests/security` |
| Portable package and cross-surface guarantees | `tests/conformance` |
| Accessible output and keyboard/fallback behavior | `tests/a11y` |
| Browser lifecycle and rendered interaction evidence | `tests/browser` |
| Performance budgets and non-blocking workloads | `tests/performance` |
| Migration and compatibility behavior | `tests/upgrade` |
| Script and release-contract behavior | `tests/scripts`, `tests/ops`, or the relevant `scripts/verify_pkg_*.py` |

The browser lane is opt-in because it needs Playwright and serial execution:
install Chromium, set `HEDRON_BROWSER=1`, and run `pytest -m browser -n 0`.
Security, accessibility, performance, browser, Redis, and historical tests are
also represented by explicit markers in the root pytest configuration.

## Shared local suites

`scripts/ci_checks.sh` is the single orchestration layer used by local checks
and by the CI/release workflows. Its suites have distinct responsibilities:

- `test` runs the strict full pytest configuration; `coverage` runs a serial,
  branch-aware test pass and checks independent floors for the main packages.
- `typing` runs the warning-fatal Pyright path; `quality` combines formatting,
  linting, workspace/package typing, release-contract checks, docs checks,
  package verification, and optional wheel smoke.
- `docs` builds strict MkDocs and the documentation ownership, inventory,
  recipes, generated-content, links, and API-coverage checks.
- `workbench` exercises minimum/latest dependency bounds for the Workbench
  adapter; `browser` runs Playwright evidence; `realwb` and `realconnect` are
  credential-gated Docker smoke paths.
- `evidence` verifies release packets, dependency/audit evidence, and the
  historical package cuts; `packaging` rehearses artifacts and verifies the
  package cut used for release.
- `openwiki` checks the generated documentation checkpoint locally before the
  `all` suite proceeds to expensive work.

Independent checks inside a suite can overlap, but wheel building and package
verification remain sequenced so they cannot race the shared virtual
environment. Suite order in `all` is sequential for the same reason. Pass
`--python 3.12` for one local interpreter; omit it to run the configured test
matrix.

## Choosing breadth

For a documentation-only edit, use the docs lane and the OpenWiki gate when the
source-visible tree or generated wiki changed. For a runtime or public API
change, combine the focused test, Ruff, and warning-fatal typing lanes before
running broader quality or package checks. For security-sensitive changes,
include the corresponding security corpus even if the implementation lives in
another package. For release or package metadata changes, run the relevant
quality, evidence, and packaging paths rather than relying on a unit test alone.

The full local parity command is:

```bash
bash scripts/ci_checks.sh all --python 3.12 --skip-browser
```

It begins with the local OpenWiki freshness gate, then runs tests, dependency
bounds, quality, optional backend/browser work, evidence, and packaging. See
[Quality and Release Workflow](quality-and-release.md) for gate details and
[Quickstart](../quickstart.md) for task routing.
