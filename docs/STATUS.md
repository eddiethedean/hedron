# Specification and implementation status

**Roadmap position:** phase 0.1 — typed rendering core  
**Date:** 2026-08-02  
**Implementation:** `hedron-core` `0.1.0` complete; phase 0.2 (`v0.2.0`) is next

Phase 0.0 (specification and project foundation) remains complete. Phase 0.1 ships the framework-neutral `hedron-core` package: models, security boundary types, components, private HTML serializer, sealable registry, 0.1 built-ins, and `render(...) -> RenderResult`. Core tests run without FastAPI, Flask, Django, or Node.js. The reference application’s static team-admin tree renders offline.

## Current conclusions

- Python is the reference implementation.
- FastAPI is the flagship integration and its documented extension points are authoritative; they are not yet implemented (phase 0.2).
- `hedron-core` remains independent of ASGI, WSGI, FastAPI, Flask, and Django.
- HTML endpoints will return components; JSON endpoints return models (HTTP adapters in 0.2).
- Addressability is explicit and preserves framework-native security dependencies (0.2).
- HTMX is the default server-interaction layer; Web Components own durable browser-local behavior (0.2+).
- All 29 baseline RFCs and indexed public API contracts remain Accepted as designs; the 0.1 surface is also implemented in `hedron-core`.
- Decisions D-001 through D-032 remain in force.
- No open-source license has been selected (D-030); local packaging is allowed.

## Phase 0.1 evidence

- Package: `packages/hedron-core` version `0.1.0`, import `hedron_core`.
- Tooling: uv workspace, Hatchling, Ruff, Pyright, pytest, Syrupy snapshots, GitHub Actions CI.
- Suites: unit, snapshot, security corpus, a11y core, conformance, performance foundations, environment isolation.
- Reference app: `examples/reference-app` static PAGE and FRAGMENT renders.

See the [roadmap](../ROADMAP.md) for the phase 0.2 secure FastAPI application MVP gate.
