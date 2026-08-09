# Compatibility policy

**Status:** Accepted for the **0.25.0** train (**Published** as `v0.25.0`; last published
PyPI/git = `v0.25.0`)
**Reviewed:** 2026-08-09

## Current train (read this first)

| Dependency | Supported matrix (tested) | Declared range | Notes |
|---|---|---|---|
| Python | CPython 3.11–3.14 | `>=3.11,<3.15` | |
| FastAPI | `>=0.141.1,<0.142` | `>=0.141.1,<0.150` (`hedron`) | Not required by `hedron-core` |
| Pydantic | `>=2.13.4,<2.14` | `>=2.13.4,<2.15` | Required by `hedron-core` / `hedron` |
| HTMX | Bundled 2.0.10; contract `>=2.0,<3.0` | same | Injected on PAGE responses |
| Flask | `>=3.0,<4` via `hedron-flask` | same | Waitress `>=3,<4` reference WSGI |
| Django | `>=5.2,<6` via `hedron-django` | same | WSGI + ASGI |
| Jinja (optional HDJ) | `>=3.1,<4` via `hedron[jinja]` | same | Not a default install |

The **Supported matrix** is the CI-tested range. Package metadata may declare a **wider**
compatible range; versions outside the Supported column are installable but unsupported
until evidence is green. Beta packages (`hedron`, `hedron-core`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`, `hedron-explorer`, `hedron-conformance`,
`hedron-extras`)
stay on the `0.25.x` train (Published as `0.25.0`; last published
`v0.25.0`). Alpha packages `hedron-charts`, `hedron-gradio`,
`hedron-sample-kit`, `hedron-native`, `hedron-notebook`, and `hedron-mcp`
version independently.

### Current 0.25 packaging limitation: charts and sample kit

!!! danger "Do not install these distributions from PyPI with Hedron 0.25"

    **Do not install `hedron[charts]`, `hedron-charts`, or `hedron-sample-kit` from
    PyPI with Hedron 0.25.** The newest matching `0.1.x` releases on PyPI require
    `hedron-core<0.20`; the registry-default `0.11.0` releases require
    `hedron-core==0.11.0`. Neither line is compatible with `hedron-core 0.25.x`.

    The repository contains 0.25-compatible source and tests, but a compatible wheel has
    not been published. Treat charts and the sample kit as **source-only / Deferred for
    adopters** until a new distribution version is published and this notice is removed.
    Other Alpha packages listed above have compatible published `0.1.x` wheels.

Pure-Python behavior remains the conformance reference when optional `hedron-native`
acceleration is present or absent (D-001 / D-048).

Live transports (SSE, focused streaming, page/session WebSocket, preload) are
**experimental** on the FastAPI flagship (`hedron.experimental`); polling remains the
Supported fallback on every host. Chat/Dialog are beta. Full ops/backpressure evidence
for live transports is still incomplete — see [What's ready](guides/whats-ready.md).
Flask/Django ship Blueprint/`init_app`, AppConfig, forms bridge, and bounded QuerySet
DataSource (Supported) with capability-labeled live helpers (**experimental**; prefer
polling).

Historical phase baselines (0.7–0.10) and deprecation rules are below. Prefer this section
when evaluating a new install. Maturity Supported vs Experimental claims:
[What’s ready](guides/whats-ready.md) — not the historical tables.

!!! tip "Historical sections"

    Phase 0.7–0.10 baselines below describe what each phase **introduced**. They are not
    the current maturity snapshot. Live transports introduced in 0.10 are **experimental**
    on the 0.25 train (Accepted disposition `polling_only`).

## Dependency pin conflicts

Hedron declares wider FastAPI/Pydantic ranges than the Supported matrix CI proves:

| Package | Supported (tested) | Declared |
|---|---|---|
| FastAPI | `>=0.141.1,<0.142` | `>=0.141.1,<0.150` |
| Pydantic | `>=2.13.4,<2.14` | `>=2.13.4,<2.15` |

**First app:** use a clean virtualenv so an older shared pin does not block install.

**Existing app:** if your lockfile cannot move into the Supported ranges:

1. Create an isolated env for Hedron evaluation, **or**
2. Install within the declared range at your own risk — versions outside Supported are
   **unsupported** (may work; no CI claim; upgrade risk is yours).
3. Do not report out-of-range resolver failures as Hedron defects until you reproduce on
   a clean env within the Supported ranges.

See [Installation](getting-started/installation.md) and
[Troubleshooting](guides/troubleshooting.md#fastapi-version-conflict-on-install).

## Initial runtime ranges

| Dependency | `v0.13.0` compatibility baseline | Policy |
|---|---|---|
| Python | CPython 3.11, 3.12, 3.13, and 3.14 | `requires-python = ">=3.11,<3.15"`; 3.15 prereleases are not supported. |
| FastAPI | Supported `>=0.141.1,<0.142`; declared `>=0.141.1,<0.150` | Required by `hedron`, not `hedron-core`; expand Supported only after adapter conformance. |
| Pydantic | Supported `>=2.13.4,<2.14`; declared `>=2.13.4,<2.15` | Required by `hedron-core`; Hedron shields public contracts from Pydantic internals. |
| Starlette | FastAPI-managed compatible version | No independent direct pin unless implementation use requires one; test the resolved FastAPI set. |
| HTMX | Bundled 2.0.10; compatible contract `>=2.0,<3.0` | Official assets pin an exact reviewed version per Hedron release; PAGE responses inject `/hedron-static/htmx.min.js`. |
| Matplotlib | `>=3.8,<4` in the in-repo `hedron-charts` workspace package | Source-only on 0.25 until a compatible chart wheel is published. |
| Plotly | `>=5.18,<7` in the in-repo `hedron-charts` workspace package | Source-only; local host asset, no CDN callbacks. |
| Altair | `>=6.0,<7` in the in-repo `hedron-charts` workspace package | Source-only; Python 3.14 requires Altair 6+ (TypedDict fix). |
| nh3 | `>=0.2` via `hedron[sanitize]` / `[markdown]` | TrustedHtml.nh3 named constructor. |
| Pygments | `>=2.17` via `hedron[code]` | Optional syntax highlighting for CodeViewer. |
| Pillow | `>=10.0` via `hedron[images]` | Optional image processing. |
| email-validator | `>=2.0` via `hedron[email]` | Optional email validation helpers. |
| SQLAlchemy | `>=2.0,<3` via `hedron-data[sqlalchemy]` | Explicit adapters; app owns sessions. |
| SQLModel | `>=0.0.22` via `hedron-data[sqlmodel]` | Optional on top of SQLAlchemy. |
| Authlib | `>=1.3` via `hedron[auth]` | Convenience helpers only; no identity ownership. |
| Jinja | `>=3.1,<4` via `hedron[jinja]` / `hedron-jinja` | Optional trusted-template integration; not imported by `hedron-core`. |

## Phase 0.11 compatibility baseline

Phase 0.11 adds native Flask/Django depth on top of the 0.10 live-transport surfaces and
dependency floors above.

| Capability | Supported declaration |
|---|---|
| Flask | Blueprint / `init_app`, CSRF/session helpers, capability-labeled live helpers; polling Supported fallback behind buffering proxies |
| Django | AppConfig, forms bridge, bounded QuerySet DataSource (`hedron-data`), capability-labeled live helpers; polling Supported fallback |
| Portable adapter harness | `hedron.testing.adapters` |
| HDJ | Dynamic manifests / foreign namespaces / SecurityPolicy–CSP reconciliation |
| Jobs | Optional Celery / RQ `JobBackend` bridges |

## Phase 0.10 compatibility baseline (historical)

!!! warning "Historical — not current maturity snapshot"

    Phase 0.10 **introduced** official SSE, focused streaming, page/session WebSocket,
    Dialog/Chat, media chunk contracts, and navigation preload APIs. As of the **0.13**
    train those live-transport APIs are classified **experimental**
    (`hedron.experimental`); polling and ordinary HTTP remain the Supported production
    path. Use [What’s ready](guides/whats-ready.md) for current claims — not this section.

Phase 0.10 kept the numeric dependency floors above, kept optional HDJ authoring, and added
the live-transport APIs listed below. Polling and ordinary HTTP remain Supported fallbacks.

| Capability | Historical declaration (0.10 introduction) |
|---|---|
| HDJ / Jinja | Optional `hedron-jinja` / `hedron[jinja]` with Jinja2 `>=3.1,<4` and MarkupSafe as resolved by Jinja. Not imported by `hedron-core` or a default `hedron` install. |
| HDJ source format | UTF-8 `.hdj` with a mandatory format-v1 TOML prologue; ordinary `.html`/`.jinja` stay outside the HDJ loader. |
| HDN | Removed. Version 0.8 is the final HDN-capable line; no converter or compatibility runtime ships. |
| Native adapter depth (as of 0.10) | FastAPI remained the flagship depth; Flask/Django kept their 0.7/0.8 routing slices until 0.11. |
| Live HTMX / streaming | Phase 0.10 introduced official SSE and focused streaming APIs (RFC-0032). **Current train:** those APIs are **experimental**; polling remains the required Supported fallback. PAGE responses inject pinned `htmx-ext-sse` and `htmx-ext-head-support`. |

## Phase 0.9 compatibility baseline (historical)

Phase 0.9 introduced the optional HDJ authoring package and removed HDN.

## Phase 0.7 compatibility entry gate

Concrete reviewed ranges for adapter and operations work. A version in dependency metadata is not
supported until its native conformance slice is green.

| Capability | Supported declaration |
|---|---|
| Flask | Flask `>=3.0,<4`; Werkzeug `>=3.0,<4`; reference WSGI server **Waitress** `>=3.0,<4`. Sessions use Flask signed cookies (`SECRET_KEY`); CSRF uses the double-submit cookie pattern via `hedron-flask` (same token semantics as FastAPI adapter). |
| Django | Django `>=5.2,<6` (5.2 LTS line); asgiref `>=3.8,<4`. Supported modes: **WSGI** (gunicorn sync workers) and **ASGI** (uvicorn/`Django` ASGI). Sessions and CSRF use Django middleware; first-party forms bridge and bounded QuerySet DataSource are Supported (D-046). Unsupported Django 5.0/5.1 are outside the Supported floor. |
| FastAPI operations | Uvicorn `>=0.30,<1` with `--workers` ≥ 2; proxy-forwarding via explicit `ProxyHeadersMiddleware` / trusted hosts only (fail closed when misconfigured). `root_path` and `X-Forwarded-Prefix` must match the reverse-proxy mount. |
| External cache | **Redis** `>=7.0` server; client `redis` `>=5,<6`. Serialization: JSON UTF-8 with key version prefix `h1:`; failures raise and surface via readiness without caching poisoned values. Conformance uses `fakeredis` in unit CI and Redis in ops topology. |
| Durable jobs | `JobBackend` protocol with **in-memory** test double and **Redis** conformance backend. Polling status retention default 24h; `Retry-After` from backend capability. BackgroundTasks remain non-durable. |
| Browsers (0.8 baseline) | Chromium, Firefox, and WebKit (Playwright pinned channels) for release-blocking HTMX/history/focus/OOB/CSP/reduced-motion evidence. |

### Framework capability matrix (portable vs host)

| Guarantee | Class |
|---|---|
| Safe HTML render, fragment/page selection, OOB, approved HTMX headers, cache Vary | Portable |
| Request-aware URL reverse under mounts / `root_path` / `SCRIPT_NAME` | Portable (via host reverse) |
| Disconnect cancellation, cooperative deadlines | ASGI |
| Sync-only endpoints, limited lifespan hooks | WSGI |
| FastAPI Depends / lifespan / BackgroundTasks | Framework-specific (FastAPI) |
| Flask `url_for`, cookie sessions, WSGI middleware | Framework-specific (Flask) |
| Django URLconf, middleware CSRF/sessions, forms | Framework-specific (Django) |

The framework capability matrix labels each guarantee as portable, ASGI, WSGI, or
framework-specific. A version appearing in dependency metadata is not considered supported until
its native conformance slice is green.

Python 3.11 and 3.12 remain supported by upstream security fixes through 2027 and 2028 respectively; 3.13 and 3.14 are in bugfix support. Python 3.15 is prerelease as of this review. FastAPI 0.141.1 and Pydantic 2.13.4 are the latest stable releases reviewed for the baseline. HTMX’s official repository documents 2.0.10, while later major-line work is not used for the initial contract.

The exact lockfile records full transitive versions. Patch releases enter through dependency-update pull requests and must pass the complete compatibility suite before the supported range or bundled asset changes.

Hedron uses documented public upstream APIs. Compatibility shims are isolated by adapter and removed according to the deprecation policy.

## Public stability

Authoritative classifications live in [api/STABILITY.md](api/STABILITY.md)
(`stable` | `beta` | `experimental` | `internal` | `deferred`).

- Hedron intentionally remains on capability-driven `0.x` releases; no 1.0 freeze is scheduled.
- `stable` contracts are compatibility-protected regardless of the distribution's `0.x` version.
  An incompatible change requires an accepted RFC/decision, migration tooling or guidance, a
  deprecation diagnostic when feasible, and at least one intervening minor phase before removal.
- `beta` contracts may change at a minor phase boundary with the same changelog, migration, and
  evidence obligations; patch releases remain backward compatible except for an urgent security or
  correctness fix with explicit disclosure.
- `experimental` contracts may change or be removed in a minor phase but must remain visibly
  classified. `internal` and `deferred` behavior is not a Supported public promise.
- Release changes are classified as:
  - **MINOR PHASE** — additive APIs, new optional extras/capabilities, promoted stability, or an
    approved beta/experimental revision with migration evidence;
  - **PATCH** — compatible bug/security fixes, dependency changes within the declared range, and
    documentation;
  - **FUTURE MAJOR** — reserved for a separately accepted RFC demonstrating a real ecosystem-wide
    compatibility boundary, never created merely because the roadmap reached a certain size.
- Bundled browser-asset pin changes (exact HTMX version/digest) are at least a **MINOR** and require
  the three-engine browser suite plus asset audit evidence.
- Build-manifest format bumps that reject older artifacts require a new minor phase,
  accepted migration design, upgrade diagnostics, compatibility fixtures, and retained migration
  evidence.
- Deprecations include a diagnostic code (when feasible), replacement guidance, and a numeric
  support window of **at least one intervening minor phase** before removal.
- D-041 is the explicit exception for experimental HDN: 0.9 removes it without a deprecation
  window, compatibility runtime, or converter; 0.8 is the final capable line.
- Rendered markup, registry metadata, Jinja template inventories, CSS symbol manifests, and plugin
  protocols each declare whether they are public, versioned artifacts or private details
  ([STABILITY.md](api/STABILITY.md)).

## Phase 0.8 compatibility baseline

| Dimension | 0.8 baseline |
|---|---|
| Python | CPython 3.11–3.14 |
| FastAPI flagship | FastAPI `>=0.141.1,<0.142` + Uvicorn workers |
| Flask adapter | Flask/Werkzeug `>=3,<4`; Waitress `>=3,<4` |
| Django adapter | Django `>=5.2,<6`; asgiref `>=3.8,<4`; WSGI + ASGI |
| Browsers | Chromium, Firefox, WebKit (Playwright) |
| HTMX | Bundled 2.0.10; contract `>=2.0,<3.0` |
| Deferred (0.8 historical) | SSE live transport (promoted in 0.10); Django QuerySet DataSource (promoted in 0.11 / D-046) |

Changing a Supported row in a later capability phase requires an accepted compatibility update,
migration analysis, and a complete rerun of affected baseline plus owning-phase evidence.

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

Compatibility claims for the **0.25.0** train require clean-install, package, FastAPI
adapter, OpenAPI, security corpus, reference-application, and owning-phase live-transport
suites. Changing a Supported row requires compatibility evidence and an updated decision
or RFC.

For 0.7 and later, compatibility evidence includes the framework/server capability matrix,
native adapter slices, offline browser assets, multi-worker deployment, and external
cache/job degradation. From 0.8 onward, a phase may revise the matrix only through its
accepted capability scope, migration analysis, and a complete rerun of affected evidence.
Dependency metadata alone never creates a Supported claim.

## Primary sources reviewed

- [Python version status](https://devguide.python.org/versions/)
- [FastAPI package metadata and releases](https://pypi.org/project/fastapi/)
- [Pydantic package metadata and releases](https://pypi.org/project/pydantic/)
- [HTMX official repository](https://github.com/bigskysoftware/htmx)
