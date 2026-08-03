# RFC-0018: Packaging

**Status:** Proposed

## Distributions

- `hedron-core`: models, components, rendering, registry protocols, HDN, HTMX metadata, scoped-style contracts, and security primitives.
- `hedron`: flagship FastAPI integration and re-exported beginner API.
- `hedron-flask` and `hedron-django`: dedicated adapters without FastAPI.
- `hedron-explorer`, `hedron-data`, and `hedron-charts`: substantial optional subsystems.

Small integrations may use extras such as `hedron[dev]`, `[test]`, `[markdown]`, `[code]`, `[images]`, and `[email]`. Heavy libraries are never required by the core. Imports are lazy, version-gated, and based on public upstream APIs.

## Compatibility

Packages declare supported Python, Hedron, and upstream version ranges. Optional native wheels, if introduced, cannot remove the pure-Python path or change output semantics.

## Acceptance criteria

- A clean `hedron-core` installation has no FastAPI import.
- Flask and Django packages do not install FastAPI.
- Missing extras yield an exact install command.
- Wheel and source-distribution tests verify package data, assets, typing markers, and offline operation.

