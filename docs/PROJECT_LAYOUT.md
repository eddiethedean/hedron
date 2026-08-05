# Project and package layout

**Status:** Accepted; kept current with the **0.13.0** train (published) on `main`

Hedron uses a Python monorepo with independently publishable distributions. Distribution
names use hyphens; import packages use underscores. The flagship `hedron` package
re-exports the beginner-facing FastAPI API.

```text
hedron/
├── README.md
├── ROADMAP.md                 # generated mirror of docs/ROADMAP.md
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
│   ├── hedron-flask/              # Beta Supported adapter
│   │   └── src/hedron_flask/
│   └── hedron-django/             # Beta Supported adapter (Django >=5.2,<6)
│       └── src/hedron_django/
├── tests/
│   ├── adapters/
│   ├── conformance/
│   ├── integration/
│   ├── browser/
│   ├── security/
│   └── performance/
├── examples/
│   ├── reference-app/             # FastAPI reference
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
| `hedron` | `hedron` | `hedron-core`, FastAPI; Starlette through FastAPI | `v0.2.0` (current train `0.13.0`) |
| `hedron-explorer` | `hedron_explorer` | `hedron`, development UI dependencies | `v0.2.0` preview; full platform at `v0.4.0` |
| `hedron-sample-kit` | `hedron_sample_kit` | `hedron-core`; sample plugin entry point | `v0.4.0` |
| `hedron-data` | `hedron_data` | `hedron-core`; dataframe/grid dependencies remain extras; also `hedron[data]` | `v0.5.0` |
| `hedron-charts` | `hedron_charts` | `hedron-core`; chart backends remain extras; also `hedron[charts]` | `v0.6.0` |
| `hedron-flask` | `hedron_flask` | `hedron-core`, Flask | `v0.7.0` (Beta Supported) |
| `hedron-django` | `hedron_django` | `hedron-core`, Django `>=5.2,<6` | `v0.7.0` (Beta Supported) |
| `hedron-jinja` | `hedron_jinja` | `hedron-core`, Jinja; also `hedron[jinja]` | `v0.9.0` / train with `0.13.0` |

`hedron` does not require Explorer or Jinja in production. `hedron[dev]` installs
`hedron-explorer` for development diagnostics; `hedron[jinja]` installs the separate integration.
The flagship package contains the registry and trace hooks needed by
Explorer but not the Explorer frontend.

**Publish note:** the coordinated train is **`0.13.0`** (`v0.13.0`, published) for advanced
async and observability — see [STATUS](STATUS.md).

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

Edit canonical **STATUS** and **ROADMAP** under `docs/`, then run
`scripts/sync_status_roadmap.py` so the root mirrors stay aligned.

## Release numbering

First-party distributions use a coordinated release train. The Git tag and release name
include `v`—for example `v0.10.0`—while Python package metadata uses the normalized version
without the prefix, such as `0.10.0`. Patch releases such as `v0.10.1` fix the owning phase
without creating another roadmap phase.
