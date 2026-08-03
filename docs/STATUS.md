# Specification and implementation status

**Roadmap position:** phase 0.5 **implemented, not yet published** as `0.5.0`; phase 0.6 next  
**Date:** 2026-08-03  
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` / `hedron-sample-kit` /
`hedron-data` `0.5.0` on `main` (MIT licensed, D-033); PyPI still serves the prior train until
`v0.5.0` is tagged and published.

Phase 0.5 delivers the data application toolkit: `Auto()` and Data Intelligence,
`DataTable` / `DataEditor` with Tabulator host, data-source protocols, caching,
utility components, ColorMode UI, Explorer cache/data/Auto panels, and
`hedron-data`.

## Current conclusions

- Python is the reference implementation.
- FastAPI is the flagship integration and uses documented extension points.
- `hedron-core` remains independent of ASGI, WSGI, FastAPI, Flask, and Django.
- HTML endpoints return components; JSON endpoints return models.
- Addressability is explicit; lazy resources do not inherit parent authorization.
- HTMX is the default server-interaction layer; Web Components own persistent local UI.
- HDN is optional; built-in Python components remain the beginner path (D-010).
- Decisions D-001 through D-034 remain in force.

## Phase 0.5 evidence

- Acceptance: [DATA_EDITOR](acceptance/DATA_EDITOR.md),
  [CACHING_UTILITIES](acceptance/CACHING_UTILITIES.md).
- Inference inventory: [INFERENCE_OVERRIDES.md](INFERENCE_OVERRIDES.md).
- Release gate: `uv run python scripts/check_release_gate.py 0.5.0`.
- Cut procedure: [RELEASE.md](RELEASE.md) (`Cut v0.5.0`).

See the [roadmap](ROADMAP.md) for the phase 0.6 visualization gate.
