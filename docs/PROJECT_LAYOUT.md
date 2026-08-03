# Project and package layout

**Status:** Accepted for the phase 0.0 baseline

Hedron uses a Python monorepo with independently publishable distributions. Distribution names use hyphens; import packages use underscores. The flagship `hedron` package re-exports the beginner-facing core API.

```text
hedron/
├── README.md
├── ROADMAP.md
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
│   ├── hedron-flask/              # planned; phase 0.7C gate
│   │   └── src/hedron_flask/
│   └── hedron-django/             # planned; phase 0.7D gate
│       └── src/hedron_django/
├── tests/
│   ├── conformance/
│   ├── integration/
│   ├── browser/
│   ├── security/
│   └── performance/
├── examples/
│   └── reference-app/
└── docs/
```

## Distribution boundaries

| Distribution | Import | Required dependencies | First release |
|---|---|---|---:|
| `hedron-core` | `hedron_core` | Pydantic and small framework-neutral utilities | `v0.1.0` |
| `hedron` | `hedron` | `hedron-core`, FastAPI; Starlette through FastAPI | `v0.2.0` (train at `0.6.0`) |
| `hedron-explorer` | `hedron_explorer` | `hedron`, development UI dependencies | `v0.2.0` preview; full platform at `v0.4.0` |
| `hedron-sample-kit` | `hedron_sample_kit` | `hedron-core`; sample plugin entry point | `v0.4.0` |
| `hedron-data` | `hedron_data` | `hedron-core`; dataframe/grid dependencies remain extras; also `hedron[data]` | `v0.5.0` |
| `hedron-charts` | `hedron_charts` | `hedron-core`; chart backends remain extras; also `hedron[charts]` | `v0.6.0` |
| `hedron-flask` *(planned)* | `hedron_flask` | `hedron-core`, Flask | Target `v0.7.0`; publish/stability gated by 0.7C evidence |
| `hedron-django` *(planned)* | `hedron_django` | `hedron-core`, Django | Target `v0.7.0`; publish/stability gated by 0.7D evidence |

`hedron` does not require Explorer in production. Beginning with the `v0.2.0` preview, `hedron[dev]` installs `hedron-explorer` for development diagnostics; the full Explorer surface ships in `v0.4.0`. The flagship package contains the registry and trace hooks needed by Explorer but not the Explorer frontend.

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
- The reference application imports packages exactly as an external application would.

## Repository tooling

The root is a `uv` workspace with one lockfile for development and compatibility testing. Each distribution owns its own `pyproject.toml`, metadata, dependencies, typing marker, package assets, changelog fragment, and tests. Hatchling is the initial PEP 517 build backend. Published artifacts remain installable with ordinary `pip` and are not coupled to `uv`.

The phase 0.7A package-boundary review must prove this graph is acyclic before Flask or Django
package scaffolding is accepted. Planned directories in this document describe target layout, not
currently shipped distributions.

## Release numbering

First-party distributions use a coordinated release train. The Git tag and release name include `v`—for example `v0.1.0`—while Python package metadata uses the normalized version without the prefix, such as `0.1.0`. Every first-party distribution already introduced by a phase uses that release-train version; a distribution introduced later begins at the current train version shown in the table above. Patch releases such as `v0.1.1` fix the owning phase without creating another roadmap phase. Phase 0.0 creates neither a release tag nor a package artifact.
