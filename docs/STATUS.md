# Specification and implementation status

**Roadmap position:** phase 0.2 — secure FastAPI application MVP  
**Date:** 2026-08-03  
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` `0.2.0` complete; MIT licensed (D-033); phase 0.3 (`v0.3.0`) is next

Phase 0.1 remains complete. Phase 0.2 ships the FastAPI flagship: `Hedron()`, `HedronRouter`/`HedronRoute`, pages, addressable components, typed actions, CSRF, HTMX page/fragment responses, OpenAPI `text/html` metadata, `SessionState`, interaction built-ins, minimal CLI, and an Explorer preview via `hedron[dev]`.

Core stays free of FastAPI/ASGI imports. The authenticated CRUD reference application works in both `Hedron()` and plain FastAPI + `HedronRouter` modes. CI covers Python 3.11–3.14.

## Current conclusions

- Python is the reference implementation.
- FastAPI is the flagship integration and uses documented extension points.
- `hedron-core` remains independent of ASGI, WSGI, FastAPI, Flask, and Django.
- HTML endpoints return components; JSON endpoints return models.
- Addressability is explicit; lazy resources do not inherit parent authorization.
- HTMX is the default server-interaction layer.
- Decisions D-001 through D-033 remain in force (D-030 superseded by D-033 MIT).

## Phase 0.2 evidence

- Packages: `packages/hedron-core`, `packages/hedron`, `packages/hedron-explorer` at `0.2.0`.
- Suites: unit, snapshot, security, a11y, conformance, performance, FastAPI integration, reference CRUD.
- Reference app: authenticated team admin with CSRF, lazy table, create/update/delete.
- CLI: `hedron routes`, `hedron components`, `hedron preview`.
- Explorer preview mounts only under development/secured explorer modes.

See the [roadmap](../ROADMAP.md) for the phase 0.3 authoring and styles gate.
