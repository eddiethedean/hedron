---
description: The canonical Hedron 1.0 authoring model, stability boundary, migration path, and package changes.
search:
  boost: 1.8
---

# What’s new in Hedron 1.0

Hedron `v1.0.0` is a subtractive, compatibility-reviewed release candidate. It turns the proven
0.x capabilities into one canonical application model and freezes an enumerated stable surface.
The candidate and all 17 release gates are Verified in the repository; the Git tag and PyPI
publication remain maintainer-controlled. PyPI currently serves `v0.66.2`.

## One authoring model

New applications use three function roles:

| Role | Purpose | Typical result |
|---|---|---|
| `@app.page` | Complete navigable document | `Page` or a component tree |
| `@app.view` | Replaceable server-rendered region | A view handle and HTML fragment |
| `@app.action` | Typed server operation | Refresh, redirect, toast, validation, or response |

Feature composition uses `app.include(...)`. The 0.67 `screen`, `refreshable`, `fragment`,
`command`, `form_command`, and `include_feature` spellings are migration inputs, not parallel 1.0
authoring APIs.

## Stability now has a precise boundary

The 1.0 SemVer promise applies to the machine-checked stable inventory, not every importable
symbol. Public surfaces remain classified as `stable`, `beta`, `experimental`, `internal`, or
`deferred`; capability readiness remains separately classified as Supported or Experimental.

Read [Stability](../api/STABILITY.md) before depending on advanced APIs and
[What’s ready](whats-ready.md) before making production claims.

## HTMX, Alpine, and Web Components have one owner each

- The server owns routes, authorization, CSRF, validation, durable state, and response HTML.
- HTMX owns enhanced HTTP requests and placement of authoritative server HTML.
- Alpine owns disposable browser-local presentation state.
- Web Components own specialist internal DOM and typed element contracts.
- Hedron coordinates lifecycle handoff without becoming a client application runtime.

The [HTMX/Alpine boundary](../api/HTMX_ALPINE_BOUNDARY_1_0.md) is normative for 1.0.

## Package changes

- Coordinated packages, including `hedron-posit`, move to `1.0.0` and Stable maturity for their
  enumerated stable inventory.
- `fastapi-workbench` remains an independent stable package at `1.0.1`.
- `hedron-workbench` and `hedron[workbench]` were removed. Use `hedron-posit` /
  `hedron[posit]`, or use `fastapi-workbench` for a plain ASGI application.
- Charts, maps, native acceleration, MCP, Gradio, notebook, simulation, and sample-kit packages
  retain independent versions and their documented Beta/tooling boundaries.
- Edron remains an independent authoring facade and requires Hedron `>=1.0.0,<2.0`.

## Migration tooling

Audit an application without importing or executing it:

```bash
python -m hedron --app app:app check --target 1.0 --project .
python -m hedron migrate api --target 1.0 . --out migrated-app
```

The migrator writes a new output tree and leaves dynamic or ambiguous cases for review. See the
[1.0 upgrade guide](upgrade.md) for the exact mapping and rollback process.

## Operational defaults that did not change

- Polling remains the Supported production fallback; SSE and WebSocket helpers remain
  Experimental.
- Production Explorer and plugin discovery remain deny-by-default.
- Multi-worker jobs and caches require shared backends.
- Session secrets are application-owned and must be passed explicitly.
- Ordinary apps require no Node.js toolchain.
- Automated accessibility evidence does not create an unqualified WCAG or human-AT claim.

## Install status

The repository candidate is installed with `uv sync`. Until publication, public-index examples
use:

```bash
python -m pip install "hedron>=0.66.2,<0.67" "uvicorn[standard]"
```

Check [Current release and support](current-release.md) before changing an application pin.
