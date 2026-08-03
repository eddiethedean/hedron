# Compatibility policy

**Status:** Accepted for the phase 0.0 baseline  
**Reviewed:** 2026-08-03

## Initial runtime ranges

| Dependency | `v0.6.0` baseline | Policy |
|---|---|---|
| Python | CPython 3.11, 3.12, 3.13, and 3.14 | `requires-python = ">=3.11,<3.15"`; 3.15 prereleases are not supported. |
| FastAPI | `>=0.141.1,<0.142` | Required by `hedron`, not `hedron-core`; expand only after adapter conformance. |
| Pydantic | `>=2.13.4,<2.14` | Required by `hedron-core`; Hedron shields public contracts from Pydantic internals. |
| Starlette | FastAPI-managed compatible version | No independent direct pin unless implementation use requires one; test the resolved FastAPI set. |
| HTMX | Bundled 2.0.10; compatible contract `>=2.0,<3.0` | Official assets pin an exact reviewed version per Hedron release; PAGE responses inject `/hedron-static/htmx.min.js`. |
| Matplotlib | `>=3.8,<4` via `hedron-charts[matplotlib]` | Lazy optional; exact missing-extra guidance. |
| Plotly | `>=5.18,<7` via `hedron-charts[plotly]` | Lazy optional; local host asset, no CDN callbacks. |
| Altair | `>=5.2,<6` via `hedron-charts[altair]` | Lazy optional; Vega-Lite JSON as data. |
| nh3 | `>=0.2` via `hedron[sanitize]` / `[markdown]` | TrustedHtml.nh3 named constructor. |
| Pygments | `>=2.17` via `hedron[code]` | Optional syntax highlighting for CodeViewer. |
| Pillow | `>=10.0` via `hedron[images]` | Optional image processing. |
| email-validator | `>=2.0` via `hedron[email]` | Optional email validation helpers. |
| SQLAlchemy | `>=2.0,<3` via `hedron-data[sqlalchemy]` | Explicit adapters; app owns sessions. |
| SQLModel | `>=0.0.22` via `hedron-data[sqlmodel]` | Optional on top of SQLAlchemy. |
| Authlib | `>=1.3` via `hedron[auth]` | Convenience helpers only; no identity ownership. |

## Phase 0.7 compatibility entry gate

The following matrix must contain concrete reviewed ranges before phase 0.7 adapter implementation
begins. `TBD` is a blocker, not an implied claim.

| Capability | Required declaration before 0.7 code |
|---|---|
| Flask | Supported Flask and Werkzeug ranges; reference WSGI server; session and CSRF integration policy |
| Django | Supported Django and asgiref ranges; supported ASGI/WSGI modes; forms, sessions, and CSRF policy |
| FastAPI operations | Reference ASGI server/version and proxy-forwarding policy |
| External cache | At least one executable conformance implementation, serialization/version policy, and failure semantics |
| Durable jobs | At least one executable conformance implementation and polling/status retention policy |
| Browsers | Chromium, Firefox, and WebKit versions/channels used for 0.7 evidence and 0.8 release hardening |

The framework capability matrix labels each guarantee as portable, ASGI, WSGI, or
framework-specific. A version appearing in dependency metadata is not considered supported until
its native conformance slice is green.

Python 3.11 and 3.12 remain supported by upstream security fixes through 2027 and 2028 respectively; 3.13 and 3.14 are in bugfix support. Python 3.15 is prerelease as of this review. FastAPI 0.141.1 and Pydantic 2.13.4 are the latest stable releases reviewed for the baseline. HTMX’s official repository documents 2.0.10, while later major-line work is not used for the initial contract.

The exact lockfile records full transitive versions. Patch releases enter through dependency-update pull requests and must pass the complete compatibility suite before the supported range or bundled asset changes.

Hedron uses documented public upstream APIs. Compatibility shims are isolated by adapter and removed according to the deprecation policy.

## Public stability

- Pre-1.0 APIs may change through accepted RFC revisions and release notes.
- 1.0 public contracts follow semantic versioning.
- Deprecations include diagnostics, replacement guidance, and at least the documented support window.
- Rendered markup, registry metadata, HDN compiled formats, CSS symbol manifests, and plugin protocols each declare whether they are public, versioned artifacts or private details.

## Cross-package compatibility

Every optional package declares compatible Hedron and upstream ranges. The plugin loader rejects incompatible major versions at startup. Pure-Python behavior remains the conformance reference if native acceleration is introduced.

## Browser compatibility

The baseline targets browsers with native ES modules, Custom Elements, CSS custom properties,
`fetch`, `AbortController`, and the selected HTMX version. Phase 0.6 closure activates at least one
real-browser job for shipped interaction and visualization assets. Phase 0.7 records the supported
browser evidence matrix, and phase 0.8 runs the release-blocking Chromium, Firefox, and WebKit
suite. Internet Explorer is unsupported. Enhanced widgets document additional capabilities and
accessible fallbacks.

CPython default builds are normative. Free-threaded CPython and PyPy are informational until separately promoted through the compatibility matrix.

## Release evidence

Compatibility claims for the 0.2.0 train require clean-install, package, FastAPI adapter, OpenAPI, security corpus, and reference-application tests. Browser and compiled-artifact evidence arrive with later phases. The matrix above is the initial tested baseline; changing it requires compatibility evidence and an updated decision or RFC.

For 0.7 and later, compatibility evidence includes the framework/server capability matrix, native
adapter slices, offline browser assets, multi-worker deployment, and external cache/job degradation.
For 0.8 and `1.0.0rcN`, the matrix is immutable except for an approved compatibility fix with
migration analysis and a complete rerun of affected evidence.

## Primary sources reviewed

- [Python version status](https://devguide.python.org/versions/)
- [FastAPI package metadata and releases](https://pypi.org/project/fastapi/)
- [Pydantic package metadata and releases](https://pypi.org/project/pydantic/)
- [HTMX official repository](https://github.com/bigskysoftware/htmx)
