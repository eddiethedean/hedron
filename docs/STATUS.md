# Specification and implementation status

**Roadmap position:** phase 0.6 **published** as `v0.6.0`; behavioral closure gate open before 0.7
**Date:** 2026-08-03  
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` / `hedron-sample-kit` /
`hedron-data` / `hedron-charts` `0.6.0` on PyPI (MIT licensed, D-033)

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

## Phase 0.6 evidence

Publication records the shipped `0.6.0` artifacts; it does not waive the new evidence policy.
Before portable 0.7 adapter contracts are implemented, the roadmap's 0.6 closure gate re-verifies
interaction/header policy, OOB and fragment regions, cache behavior, trusted chart/SVG paths, local
browser runtimes, real-browser lifecycle, and bounded SQLAlchemy queries. Open items are fixed on
the 0.6 maintenance line or explicitly reclassified as experimental.

- Acceptance: [VISUALIZATION](acceptance/VISUALIZATION.md), [HTMX](acceptance/HTMX.md).
- Packages: `hedron-charts` with Matplotlib/Plotly/Altair adapters; flagship extras
  `charts`, `markdown`, `code`, `images`, `email`, `sanitize`, `auth`.
- Reference application: chart + Markdown section and `/charts/*` interaction routes.
- Release: [GitHub `v0.6.0`](https://github.com/eddiethedean/hedron/releases/tag/v0.6.0);
  cut procedure archived in [RELEASE.md](RELEASE.md).

See the [roadmap](ROADMAP.md) for the phase 0.7 adapter/operations gate.
