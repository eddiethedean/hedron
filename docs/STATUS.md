# Specification and implementation status

**Roadmap position:** phase 0.2 ready to cut `v0.2.0`  
**Date:** 2026-08-03  
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` `0.2.0` on `main`; MIT licensed (D-033); release gate green; phase 0.3 (`v0.3.0`) follows publication

Phase 0.1 remains complete. Phase 0.2 implements the FastAPI flagship: `Hedron()`, `HedronRouter`/`HedronRoute`, pages, addressable components, typed actions, CSRF, HTMX page/fragment responses, OpenAPI `text/html` metadata, `SessionState`, interaction built-ins (including polling/pagination/infinite-scroll helpers), minimal CLI (`--app`), and an Explorer preview via `hedron[dev]`.

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

- Packages: `packages/hedron-core`, `packages/hedron`, `packages/hedron-explorer` at `0.2.0`.
- Gate: `uv run python scripts/check_release_gate.py 0.2.0` passes (versions, `__version__`, changelogs, LICENSE).
- Acceptance subsets for cut: SECURITY 0.2, FASTAPI MVP, HTMX 0.2, Explorer preview, COMPONENT_MODEL FastAPI parity, PACKAGING Explorer-absent-by-default.
- Suites: unit, snapshot, security, a11y, conformance, performance, FastAPI integration, HTML parity, reference CRUD.
- Reference app: authenticated team admin with CSRF (header and form field), lazy table, create/update/delete, Explorer under `explorer="development"`.
- CLI: `hedron routes|components|preview` with optional `--app module:attr`.
- PyPI: `hedron==0.2.0` **intentionally reclaims** the existing project name (same author; prior geolocation package ≤0.0.6 is superseded).

## Cut instructions

Follow [RELEASE.md](RELEASE.md) section **Cut `v0.2.0`**: green CI on `main`, then annotated tag `v0.2.0`. Do not retag. After publication, flip changelog compare URLs and mark this status published.

See the [roadmap](../ROADMAP.md) for the phase 0.3 authoring and styles gate.
