# Project and package layout

**Status:** Accepted; kept current with the **0.50.x** published train (tip `v0.50.2`)

Hedron uses a Python monorepo with independently publishable distributions. Distribution
names use hyphens; import packages use underscores. The flagship `hedron` package
re-exports the beginner-facing FastAPI API.

```text
hedron/
├── README.md
├── STATUS.md                  # generated mirror of docs/STATUS.md
├── CONTRIBUTING.md            # stub → docs/CONTRIBUTING.md
├── pyproject.toml
├── uv.lock
├── packages/
│   ├── hedron-core/
│   │   └── src/hedron_core/
│   ├── hedron/
│   │   └── src/hedron/
│   ├── hedron-explorer/
│   │   └── src/hedron_explorer/
│   ├── hedron-sample-kit/
│   │   └── src/hedron_sample_kit/
│   ├── hedron-data/
│   │   └── src/hedron_data/
│   ├── hedron-charts/
│   │   └── src/hedron_charts/
│   ├── hedron-jinja/              # Optional .hdj format and Jinja/HTML/HTMX integration
│   │   └── src/hedron_jinja/
│   ├── hedron-flask/              # Flask adapter (Supported capability; Beta package)
│   │   └── src/hedron_flask/
│   ├── hedron-django/             # Django adapter (Supported; Django >=5.2,<6)
│   │   └── src/hedron_django/
│   ├── hedron-conformance/        # Language-neutral conformance kit (0.14)
│   │   └── src/hedron_conformance/
│   ├── hedron-extras/               # Curated extras / workbenches (0.16)
│   ├── hedron-notebook/             # Beta tooling-grade localhost notebook preview (RFC-0042)
│   │   └── src/hedron_notebook/
│   ├── hedron-mcp/                  # Beta deny-by-default MCP projection (RFC-0043 / RFC-0065)
│   │   └── src/hedron_mcp/
│   ├── hedron-gradio/               # Beta allowlisted Gradio client interop (RFC-0049 / RFC-0067)
│   │   └── src/hedron_gradio/
│   ├── hedron-sim/                  # Beta tooling-grade offline HTMX docs/demo simulator
│   │   └── src/hedron_sim/
│   ├── hedron-workbench/            # Posit Workbench compatibility adapter (0.33)
│   │   └── src/hedron_workbench/
│   ├── hedron-posit/                # Unified Posit Workbench / Connect adapter (0.33)
│   │   └── src/hedron_posit/
│   ├── hedron-native/             # Optional Rust acceleration (Beta 0.1.x)
│   │   └── src/hedron_native/
│   ├── hedron-elements/           # Alpha 0.36 Web Component ABI (D-064)
│   ├── hedron-runtime-node/       # Beta tooling-grade Node evaluator (outside uv workspace)
│   └── hedron-runtime-java/       # Beta tooling-grade Java evaluator (outside uv workspace)
├── tests/
│   ├── adapters/
│   ├── conformance/
│   ├── integration/
│   ├── browser/
│   ├── security/
│   └── performance/
├── examples/
│   ├── reference-app/             # FastAPI reference
│   ├── dashboard-0.17/            # Reactive dashboard / agent interface demo (0.17)
│   ├── model-demo-0.18/           # Model demo / inference workflow demo (0.18)
│   ├── live-interaction/          # Poll / stream / SSE sample (0.10)
│   ├── flask-reference/
│   ├── django-reference/
│   └── hdj-progressive/           # Optional HDJ progressive samples
├── scripts/                       # release gates, component docs, STATUS sync, mkdocs
└── docs/                          # canonical MkDocs sources
```

## Distribution boundaries

| Distribution | Import | Required dependencies | First release |
|---|---|---|---:|
| `hedron-core` | `hedron_core` | Pydantic and small framework-neutral utilities | `v0.1.0` |
| `hedron` | `hedron` | `hedron-core`, FastAPI; Starlette through FastAPI | `v0.2.0` (current train `0.50.x`) |
| `hedron-explorer` | `hedron_explorer` | `hedron`, development UI dependencies | `v0.2.0` preview; full platform at `v0.4.0` |
| `hedron-sample-kit` | `hedron_sample_kit` | `hedron-core`; sample plugin entry point | `v0.4.0` |
| `hedron-data` | `hedron_data` | `hedron-core`; dataframe/grid dependencies remain extras; also `hedron[data]` | `v0.5.0` |
| `hedron-charts` | `hedron_charts` | `hedron-core`; chart backends remain extras; also `hedron[charts]` | Beta line `0.2.x`, tip `0.2.0` (Published with Hedron `v0.38.0`) |
| `hedron-flask` | `hedron_flask` | `hedron-core`, Flask | `v0.7.0` (Supported capability; Beta package) |
| `hedron-django` | `hedron_django` | `hedron-core`, Django `>=5.2,<6` | `v0.7.0` (Supported; Beta package) |
| `hedron-jinja` | `hedron_jinja` | `hedron-core`, Jinja; also `hedron[jinja]` | `v0.9.0` / train with `0.25.x` |
| `hedron-conformance` | `hedron_conformance` | Fixture schema + runner (stdlib + pydantic) | `v0.16.0` |
| `hedron-extras` | `hedron_extras` | Optional curated extras / workbenches; also `hedron[extras]` | `v0.16.0` |
| `hedron-notebook` | `hedron_notebook` | Beta tooling-grade localhost preview; also `hedron[notebook]` | `v0.1.0` |
| `hedron-mcp` | `hedron_mcp` | Optional MCP projection (Beta Supported inventory; deny-by-default); also `hedron[mcp]` | `v0.2.1` |
| `hedron-gradio` | `hedron_gradio` | Beta allowlisted Gradio client interop; also `hedron[gradio]` | `v0.2.0` |
| `hedron-sim` | `hedron_sim` | Offline HTMX docs/demo simulator (Beta tooling) | `v0.1.0` |
| `hedron-native` | `hedron_native` | Optional PyO3 extension; pure-Python fallback | `0.1.x` (Beta; independent of train version) |
| `hedron-elements` | `hedron_elements` | Beta Web Component ABI (Supported inventory only); also `hedron[elements]` | `v0.50.2` |
| `hedron-workbench` | `hedron_workbench` | `hedron-posit`; Posit Workbench compatibility; also `hedron[workbench]` | `v0.50.2` |
| `hedron-posit` | `hedron_posit` | `hedron`, `fastapi-workbench`; unified Posit facade; also `hedron[posit]` | `v0.50.2` |
| `fastapi-workbench` | `fastapi_workbench` | Starlette, Uvicorn; independent plain-FastAPI/ASGI Workbench adapter | `v1.0.0` |

`hedron` does not require Explorer or Jinja in production. `hedron[dev]` installs
`hedron-explorer` for development diagnostics; `hedron[jinja]` installs the separate integration.
The flagship package contains the registry and trace hooks needed by
Explorer but not the Explorer frontend.

**Publish note:** the coordinated in-tree train tip is **`v0.50.2`** (latest on PyPI **`v0.50.1`**) — see
[STATUS](STATUS.md).
Experimental Java/Node runtimes live under
`packages/hedron-runtime-*` outside the uv workspace.

## Dependency rules

- Packages depend only toward `hedron-core`; optional subsystems do not become core dependencies.
- `hedron-core` imports no FastAPI, Starlette, ASGI, WSGI, Flask, or Django types.
- Flask and Django packages do not depend on `hedron` or install FastAPI.
- Adapter-neutral request/interaction values, reverse-URL and asset/build protocols, lifecycle
  descriptions, and sanitized registry/diagnostic views live in `hedron-core`; raw host-framework
  objects never cross that boundary.
- Explorer's shared services consume core-owned sanitized views. Framework-specific Explorer
  mounting uses optional bridges and does not create a required adapter-to-`hedron` dependency.
- `hedron-data` and `hedron-charts` share protocols but neither depends on a concrete dataframe or visualization backend by default.
- Browser assets are package resources with manifests; application users require no Node.js installation.
- Reference applications import packages exactly as an external application would.

## Repository tooling

The root is a `uv` workspace with one lockfile for development and compatibility testing.
Each distribution owns its own `pyproject.toml`, metadata, dependencies, typing marker,
package assets, changelog, and tests. Hatchling is the PEP 517 build backend. Published
artifacts remain installable with ordinary `pip` and are not coupled to `uv`.

Edit canonical **STATUS** under `docs/STATUS.md`, then run
`scripts/sync_status_roadmap.py` so root `STATUS.md` stays aligned.
The roadmap is only `docs/ROADMAP.md` (no generated copies).

## Release numbering

First-party distributions use a coordinated release train. The Git tag and release name
include `v`—for example `v0.10.0`—while Python package metadata uses the normalized version
without the prefix, such as `0.10.0`. Patch releases such as `v0.10.1` fix the owning phase
without creating another roadmap phase.
