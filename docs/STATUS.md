# Specification and implementation status

**Roadmap position:** phase 0.1 — typed rendering core  
**Date:** 2026-08-03  
**Implementation:** `hedron-core` `0.1.0` complete (including harden pass); release-ready except D-030 license; phase 0.2 (`v0.2.0`) is next

Phase 0.0 (specification and project foundation) remains complete. Phase 0.1 ships the framework-neutral `hedron-core` package: models, security boundary types, components, private HTML serializer, sealable registry, 0.1 built-ins, and `render(...) -> RenderResult`. A harden pass closed residual XSS, Secret-redaction, FormField a11y, registry sealing, and model-guardrail defects while remaining on `0.1.0`.

Core tests run without FastAPI, Flask, Django, or Node.js tooling. The reference application’s static team-admin tree renders offline. CI is green on Python 3.12–3.14. The PyPI name `hedron-core` is available. Cutting `v0.1.0` is blocked only by license selection (D-030); see [Release](RELEASE.md).

## Current conclusions

- Python is the reference implementation.
- FastAPI is the flagship integration and its documented extension points are authoritative; they are not yet implemented (phase 0.2).
- `hedron-core` remains independent of ASGI, WSGI, FastAPI, Flask, and Django.
- HTML endpoints will return components; JSON endpoints return models (HTTP adapters in 0.2).
- Addressability is explicit and preserves framework-native security dependencies (0.2).
- HTMX is the default server-interaction layer; Web Components own durable browser-local behavior (0.2+).
- All 29 baseline RFCs and indexed public API contracts remain Accepted as designs; the 0.1 surface is implemented in `hedron-core`.
- Decisions D-001 through D-032 remain in force.
- No open-source license has been selected (D-030); the release workflow refuses public PyPI publication until `LICENSE` and package license metadata exist.

## Phase 0.1 evidence

- Package: `packages/hedron-core` version `0.1.0`, import `hedron_core`.
- Tooling: uv workspace, Hatchling, Ruff, Pyright, pytest, Syrupy snapshots, GitHub Actions CI with clean-install smoke.
- Suites: unit, snapshot, security corpus, a11y core, conformance, performance foundations, environment isolation, package metadata.
- Reference app: `examples/reference-app` static PAGE and FRAGMENT renders.
- Acceptance: 0.1 subsets marked in `docs/acceptance/{COMPONENT_MODEL,SECURITY,ACCESSIBILITY,PACKAGING_DEPLOYMENT}.md`.
- Release: changelog, PyPI metadata, tag/version gate, and publish workflow documented in [RELEASE.md](RELEASE.md).

See the [roadmap](../ROADMAP.md) for the phase 0.2 secure FastAPI application MVP gate.
