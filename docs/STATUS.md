# Specification and implementation status

**Roadmap position:** phase 0.6 **cut-ready** as `0.6.0` (tag `v0.6.0` when cut); behavioral
closure gate **green** (with Plotly/Vega full offline runtime pin Deferred as `VIS-C06-002`)  
**Date:** 2026-08-03  
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` / `hedron-sample-kit` /
`hedron-data` / `hedron-charts` `0.6.0` (MIT licensed, D-033)

Phase 0.6 delivers visualization adapters (`hedron-charts`), content/auth extras,
SQLAlchemy and AG Grid adapter boundaries, typed HTMX interaction envelopes,
semantic status responses, fragment regions, cache `Vary`, and Explorer chart /
interaction simulation panels.

## Current conclusions

- Python is the reference implementation.
- FastAPI is the flagship integration and uses documented extension points.
- `hedron-core` remains independent of ASGI, WSGI, FastAPI, Flask, and Django.
- HTML endpoints return components; JSON endpoints return models.
- Addressability is explicit; lazy resources do not inherit parent authorization.
- HTMX is the default server-interaction layer; Web Components own persistent local UI.
- HDN is optional; built-in Python components remain the beginner path (D-010).
- Decisions D-001 through D-035 remain in force.
- Optional HTMX extensions remain deferred; default fragment asset policy is
  predeclared page-shell assets ([HTMX_2_EXTENSIONS.md](HTMX_2_EXTENSIONS.md)).
- Phase 0.6 closure evidence is indexed in
  [release-gate-0.6.toml](acceptance/release-gate-0.6.toml) (`Verified` or owned `Deferred`).

## Phase 0.6 evidence

- Acceptance: [VISUALIZATION](acceptance/VISUALIZATION.md), [HTMX](acceptance/HTMX.md),
  [SECURITY](acceptance/SECURITY.md), [EVIDENCE](acceptance/EVIDENCE.md).
- Closure commands: interaction header/region suites, chart/SVG adversarial corpus,
  bounded SQLAlchemy paging (`DATA-C06-001`), Chromium Playwright smoke (`HTMX-C06-003`).
- Deferred: interactive Plotly/Vega first-party offline runtime pin/fingerprint/serve
  (`VIS-C06-002`); host shims fail closed when globals are missing.
- Packages: `hedron-charts` with Matplotlib/Plotly/Altair adapters; flagship extras
  `charts`, `markdown`, `code`, `images`, `email`, `sanitize`, `auth`.
- Reference application: chart + Markdown section and `/charts/*` interaction routes.
- Cut procedure: [RELEASE.md](RELEASE.md) (`## Cut v0.6.0`). PyPI / GitHub release appear
  after `git push origin v0.6.0` triggers the release workflow.

See the [roadmap](ROADMAP.md) for the phase 0.7 adapter/operations entry gate.
