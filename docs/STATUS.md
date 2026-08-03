# Specification and implementation status

**Roadmap position:** phase 0.2 published (`v0.2.0`); phase 0.3 next  
**Date:** 2026-08-03  
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` `0.2.0` published to PyPI; MIT licensed (D-033); next is phase 0.3 (`v0.3.0`)

Phase 0.1 remains complete. Phase 0.2 ships the FastAPI flagship: `Hedron()`, `HedronRouter`/`HedronRoute`, pages, addressable components, typed actions, CSRF, HTMX page/fragment responses, OpenAPI `text/html` metadata, `SessionState`, interaction built-ins (including polling/pagination/infinite-scroll helpers), minimal CLI (`--app`), and an Explorer preview via `hedron[dev]`.

Core stays free of FastAPI/ASGI imports. The authenticated CRUD reference application works in both `Hedron()` and plain FastAPI + `HedronRouter` modes. CI covers Python 3.11–3.14.

## Current conclusions

- Python is the reference implementation.
- FastAPI is the flagship integration and uses documented extension points.
- `hedron-core` remains independent of ASGI, WSGI, FastAPI, Flask, and Django.
- HTML endpoints return components; JSON endpoints return models.
- Addressability is explicit; lazy resources do not inherit parent authorization.
- HTMX is the default server-interaction layer.
- Decisions D-001 through D-034 remain in force (D-023 Python range superseded by D-034; D-030 superseded by D-033 MIT).

## Phase 0.2 evidence

- Release: [v0.2.0](https://github.com/eddiethedean/hedron/releases/tag/v0.2.0)
- PyPI: [`hedron`](https://pypi.org/project/hedron/0.2.0/), [`hedron-core`](https://pypi.org/project/hedron-core/0.2.0/), [`hedron-explorer`](https://pypi.org/project/hedron-explorer/0.2.0/)
- `hedron==0.2.0` intentionally reclaims the existing PyPI project name (same author; prior geolocation package superseded).
- Acceptance subsets: SECURITY 0.2, FASTAPI MVP, HTMX 0.2, Explorer preview, COMPONENT_MODEL FastAPI parity.
- Suites: unit, snapshot, security, a11y, conformance, performance, FastAPI integration, HTML parity, reference CRUD.

See the [roadmap](../ROADMAP.md) for the phase 0.3 authoring and styles gate.
