# Specification and implementation status

**Roadmap position:** phase 0.4 published (`v0.4.0`); phase 0.5 next  
**Date:** 2026-08-03  
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` / `hedron-sample-kit` `0.4.0`; MIT licensed (D-033)

Phase 0.4 delivers the developer platform: full Component Explorer (HTMX panels),
CLI `new`/`check`/`graph`/`audit-components`, plugin loader with rollback, SARIF
diagnostics, public `hedron.testing` helpers, and the `hedron-sample-kit` third-party
sample package.

## Current conclusions

- Python is the reference implementation.
- FastAPI is the flagship integration and uses documented extension points.
- `hedron-core` remains independent of ASGI, WSGI, FastAPI, Flask, and Django.
- HTML endpoints return components; JSON endpoints return models.
- Addressability is explicit; lazy resources do not inherit parent authorization.
- HTMX is the default server-interaction layer; Web Components own persistent local UI.
- HDN is optional; built-in Python components remain the beginner path (D-010).
- Decisions D-001 through D-034 remain in force.

## Phase 0.4 evidence

- Acceptance: [EXPLORER](acceptance/EXPLORER.md), [CLI](acceptance/CLI.md),
  [PLUGINS](acceptance/PLUGINS.md), [TESTING](acceptance/TESTING.md).
- Inference inventory: [INFERENCE_OVERRIDES.md](INFERENCE_OVERRIDES.md).
- Published as `v0.4.0` on 2026-08-03 ([GitHub Release](https://github.com/eddiethedean/hedron/releases/tag/v0.4.0)).

See the [roadmap](../ROADMAP.md) for the phase 0.5 data application gate.
