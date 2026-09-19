---
type: operations
title: Quality, testing, and release contracts
description: Hedron's local verification is organized by change area and shared CI suites, with strict typing, documentation checks, package contracts, and a deliberately small stable API surface.
tags: [testing, quality, release, tooling]
sources:
  - id: openwiki-source-000a7add03cfbd0ac1794f3a
    resource: repo://docs/CONTRIBUTING.md
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-db8a384d21376a4f9d3a47a1
    resource: repo://release/stable-api.toml
  - id: openwiki-source-76f1c5b345f97c02d0989b38
    resource: repo://scripts/check_openwiki_freshness.py
  - id: openwiki-source-2faef51cd0bcbe4bb5eaae2d
    resource: repo://scripts/ci_checks.sh
  - id: openwiki-source-4c56c4085c56a3ab75df5178
    resource: repo://scripts/README.md
generated: { by: "codex", at: "2026-09-19T16:47:17.741Z" }
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T17:40:19.225Z
---

# Quality, testing, and release contracts

Use the narrowest check that covers a change, then widen verification when the change crosses package or public-contract boundaries. The [monorepo architecture](/openwiki/architecture/monorepo.md) identifies package ownership; this page identifies the evidence expected before a change is handed off.

## Fast local loop

The repository supports CPython 3.10–3.14 and `uv`. After `uv sync`, the standard contributor loop is:

```bash
uv run ruff format --check packages tests examples
uv run ruff check packages tests examples
uv run pyright
uv run pytest -q
```

Choose a focused test lane first: `tests/unit` for a single package, `tests/integration` for FastAPI behavior, `tests/adapters` for host adapters, `tests/security` for the security corpus, `tests/conformance` for conformance behavior, and `examples` for runnable examples. The default pytest configuration uses xdist; browser tests are opt-in with `HEDRON_BROWSER=1` and run serially with `-n 0`.

For a docs-only change, sync the docs group and run `uv run --group docs mkdocs build --strict` plus the documentation SSOT, ownership, inventory, API-coverage, package-link, recipe-sync, and generated-content checks listed in [Contributing](https://github.com/eddiethedean/hedron/blob/main/docs/CONTRIBUTING.md). Playwright and the full pytest suite are not required for a markdown-only typo change.

## Shared suites and their boundaries

`scripts/ci_checks.sh` is the single command source for the repository's test, coverage, workbench, docs, typing, quality, browser, evidence, packaging, and local OpenWiki suites. The test suite runs strict pytest configuration and markers; coverage runs branch-aware tests and checks independent floors of 73% for `hedron` and 83% for `hedron-core`; quality runs Ruff formatting/linting, workspace and package Pyright, release-contract checks, docs checks, package verification, and optionally wheel smoke; the docs suite runs generated-content and documentation checks before strict MkDocs. GitHub Actions calls the workflow suites but does not call the local OpenWiki suite.

The OpenWiki suite is a deterministic, read-only documentation gate. It compares
the current model-visible source fingerprint with the generated page manifest,
checks the current Git HEAD checkpoint, verifies every factual page's Markdown
and Claims sidecar, and requires verified non-empty Claims. Run it directly with:

```bash
bash scripts/ci_checks.sh openwiki --python 3.12
```

If it fails, refresh the wiki through the local Codex OpenWiki integration and
rerun the gate. OpenWiki is intentionally local-only; there is no GitHub Actions
workflow for it.

The full local parity command is intentionally explicit and can skip browser work when needed:

```bash
bash scripts/ci_checks.sh all --python 3.12 --skip-browser
```

`all` runs the OpenWiki freshness gate first, before tests and the more expensive
quality, browser, evidence, and packaging work.

For a runtime-package change, the smallest high-signal sequence is the relevant focused pytest target, Ruff, and the warning-fatal strict typing lane:

```bash
bash scripts/ci_checks.sh typing --python 3.12
```

The root Pyright configuration analyzes the workspace at the Python 3.10 floor in strict mode. It includes each shipped package and treats a broad set of unknown-type, unused, deprecated, and incompatible-override findings as warnings; the quality script additionally runs package typing inventory checks and a warning-enabled package pass.

## Public API and release metadata

`release/stable-api.toml` defines the deliberately small 1.0 SemVer surface. Listed exports are compatibility-protected, listed callable/class signatures are locked when present, and unlisted exports are not stable. The stable `hedron` surface includes the application/router, core page and form components, CSRF/security policies, interaction helpers, and common controls; `hedron-core` separately protects `Component`, `Page`, `Text`, `render`, render contracts, trust markers, secrets, fragment regions, and interaction results.

Use `release/support-matrix.toml` for package maturity and supported dependency ranges, and treat package packet scripts and release-contract checks as evidence rather than as substitutes for focused behavioral tests. Public API, security-default, and supported-claim changes require the RFC/decision workflow described in [Contributing](https://github.com/eddiethedean/hedron/blob/main/docs/CONTRIBUTING.md); ordinary fixes and focused test/doc changes do not.

For runtime security checks, continue to [security and request boundaries](/openwiki/security/request-boundaries.md). For the documentation lifecycle, see [OpenWiki and Local Documentation](/openwiki/operations/openwiki-and-local-documentation.md). For a concise task-routing map, see the [Hedron agent quickstart](/openwiki/quickstart.md).
