# Specification and implementation status

**Roadmap position:** phase 0.3 implemented (`v0.3.0`); phase 0.4 next  
**Date:** 2026-08-03  
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` `0.3.0`; MIT licensed (D-033)

Phase 0.3 adds HDN authoring, scoped CSS, themes, fingerprinted assets, component-folder
discovery, `inspect`/`eject`/`build`/`dev` CLI commands, and a minimal HTMX-safe Web
Component proof (`hedron-disclose`). Production consumes versioned build manifests with
no required runtime HDN/CSS compilation (`HED-BUILD-0004` when compile is attempted).
Strict CSP uses external styles only. Build promote stays on the target filesystem;
CSS `url(...)` values are rewritten to fingerprinted asset paths.

Core stays free of FastAPI/ASGI imports. The reference application includes equivalent
Python and HDN `StatusBanner` twins with scoped style symbols and theme tokens.

## Current conclusions

- Python is the reference implementation.
- FastAPI is the flagship integration and uses documented extension points.
- `hedron-core` remains independent of ASGI, WSGI, FastAPI, Flask, and Django.
- HTML endpoints return components; JSON endpoints return models.
- Addressability is explicit; lazy resources do not inherit parent authorization.
- HTMX is the default server-interaction layer; Web Components own persistent local UI.
- HDN is optional; built-in Python components remain the beginner path (D-010).
- Decisions D-001 through D-034 remain in force.

## Phase 0.3 evidence

- HDN, scoped-style, theme, asset, and build acceptance suites.
- Suites: unit (HDN/CSS/theme/assets/build), security HDN corpus, conformance Python/HDN parity,
  FastAPI integration and reference CRUD.

See the [roadmap](../ROADMAP.md) for the phase 0.4 developer platform gate.
