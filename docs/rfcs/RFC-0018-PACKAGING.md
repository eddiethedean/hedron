# RFC-0018: Packaging

**Status:** Accepted

**Revision:** 2026-08-03 — D-035 assigned portable adapter contracts to `hedron-core` and requires
an acyclic Explorer/adapter dependency graph before phase 0.7 implementation.

## Distributions

- `hedron-core`: models, components, rendering, registry protocols, experimental legacy HDN,
  HTMX metadata, scoped-style contracts, and security primitives. D-040 moves and removes HDN
  through the RFC-0031 migration because current placement is not a replacement constraint.
- `hedron`: flagship FastAPI integration and re-exported beginner API.
- `hedron-flask` and `hedron-django`: dedicated adapters without FastAPI.
- `hedron-explorer`, `hedron-data`, and `hedron-charts`: substantial optional subsystems.

Small integrations may use extras such as `hedron[dev]`, `[test]`, `[markdown]`, `[code]`, `[images]`, and `[email]`. Heavy libraries are never required by the core. Imports are lazy, version-gated, and based on public upstream APIs.

`hedron-core` owns adapter-neutral request/interaction values, URL and asset/build-manifest
protocols, lifecycle/resource descriptions, and sanitized diagnostic/registry views. Concrete raw
request, response, session, dependency, middleware, and router objects remain in `hedron`,
`hedron-flask`, or `hedron-django`.

Explorer services consume core-owned sanitized views. Framework-specific mounting is supplied by an
optional adapter bridge; neither Flask nor Django packages acquire FastAPI through a required
Explorer dependency. The phase 0.7 entry gate must record the final acyclic dependency graph before
package scaffolding begins.

The repository is a `uv` workspace built with Hatchling. Distribution names use hyphens and their Python import packages use underscores. Component Explorer ships as the `hedron-explorer` distribution and is installed for application development through `hedron[dev]`; it is not a production dependency of `hedron`. The authoritative source tree and release sequence are defined in [Project layout](../PROJECT_LAYOUT.md).

## Compatibility

Packages declare supported Python, Hedron, and upstream version ranges. Optional native wheels, if introduced, cannot remove the pure-Python path or change output semantics.

## Acceptance criteria

- A clean `hedron-core` installation has no FastAPI import.
- Flask and Django packages do not install FastAPI.
- Installing an adapter's supported development/Explorer integration does not silently change its
  runtime framework or route semantics.
- Missing extras yield an exact install command.
- Wheel and source-distribution tests verify package data, assets, typing markers, and offline operation.
