# Specification status

**Roadmap position:** phase 0.0 — specification and project foundation  
**Date:** 2026-08-02  
**Implementation:** ready to begin phase 0.1, targeting `v0.1.0`

The phase 0.0 specification and project-foundation gate is complete; it publishes no package. The accepted documents describe the cumulative phase 0.0–1.0 path, distinguish planned contracts from implemented behavior, and provide enough detail to start the phase 0.1 typed rendering core for `v0.1.0` without inventing foundational policy.

## Current conclusions

- Python is the reference implementation.
- FastAPI is the flagship integration and its documented extension points are authoritative.
- `hedron-core` remains independent of ASGI, WSGI, FastAPI, Flask, and Django.
- HTML endpoints return components; JSON endpoints return models.
- Addressability is explicit and preserves framework-native security dependencies.
- HTMX is the default server-interaction layer; Web Components own durable browser-local behavior.
- HDN, scoped styles, Explorer, DataEditor, integrations, and async boundaries have defined architectures.
- Rust and cross-language runtimes are deferred until Python semantics stabilize and profiling supplies evidence.
- All 29 baseline RFCs and all indexed public API contracts are Accepted as planned designs; none is represented as implemented.
- Decisions D-001 through D-032 are resolved, and the compatibility, project-layout, configuration, identifier, diagnostic, built-in, release-version, and toolchain baselines are explicit.

## Readiness evidence

- RFC and API statuses agree with their indexes.
- The 0.1–1.0 roadmap assigns every accepted RFC and every planned feature family to a phase.
- Local Markdown links, heading structure, code fences, indexes, and feature coverage pass the final documentation audit.
- The remaining license choice is deliberately a publication gate, not a local implementation blocker; no license has been inferred on the owner's behalf.

See the [readiness report](READINESS_REPORT.md) for the audit record and the [roadmap](../ROADMAP.md) for the next implementation gate.
