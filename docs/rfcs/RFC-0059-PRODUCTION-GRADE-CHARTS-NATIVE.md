# RFC-0059: Production-grade visualization and native acceleration

**Status:** Accepted
**Phase:** 0.28 (`v0.28.0`)
**Stability:** `beta` (process / package-graduation contract)
**Evidence:** [RELEASE_0_28.md](../acceptance/RELEASE_0_28.md) ·
[release-gate-0.28.toml](../acceptance/release-gate-0.28.toml) ·
[production-grade-inventory-028.toml](../acceptance/production-grade-inventory-028.toml)
**Related:** D-038, D-047, D-048, D-053, D-055, D-056; [RFC-0056](RFC-0056-PRODUCTION-QUALITY.md);
[RFC-0058](RFC-0058-PRODUCTION-GRADE-SATELLITES.md); [ROADMAP §0.28](../ROADMAP.md);
[STABILITY.md](../api/STABILITY.md); [COMPATIBILITY.md](../COMPATIBILITY.md)

## Summary

Apply the ROADMAP **production-grade package contract (0.26+)** to
`hedron-charts` and `hedron-native` for explicitly bounded Supported workflows.
Baseline train is Published **`v0.28.0`**. Alpha maturity today is not the
production-grade label; 0.28 is the graduation that earns that label for the
**declared inventory only**. Independent package version lines may remain
`0.1.x` until cut; classifiers leave Alpha only when every 0.28-owned gate is
Verified.

## Motivation

Phase 0.27 (D-055 / RFC-0058) graduated the remaining Python satellite train
except charts and native acceleration. Adopters already treat Matplotlib/static
beginner charts as the conservative Supported visualization path on an Alpha
package, and optional native escape acceleration as a non-required speedup with
Python fallback. 0.28 closes the honesty gap: machine-readable Supported versus
Experimental inventories, release-gate evidence for static charts and native
wheels/fallback, supply-chain pins for Supported assets, and explicit
non-graduation of interactive/optional adapters.

## Design

### Packages in scope

| Package | Production-grade scope |
|---|---|
| `hedron-charts` | Matplotlib static SVG/PNG; beginner `LineChart` / `BarChart` / `AreaChart` / `ScatterChart` on the static/Matplotlib path; accessible tabular/text alternatives; CSP-safe local assets; bounded payloads; lifecycle cleanup; browser/print/export evidence |
| `hedron-native` | Optional Rust `escape_text` / `escape_attr` only; published wheels for the Supported CPython × OS matrix (cibuildwheel: manylinux x86_64 + aarch64, macOS arm64, Windows amd64); reproducible source builds; fuzz and sanitizer evidence; Python-reference parity; measured serialize-stage benefit; absence / import failure / unsupported platform / runtime disable all fall back without semantic drift |

### Interactive and optional adapters

Plotly, Altair/Vega interactive hosts, and every name in
`hedron_charts.optional_adapters` remain **Experimental**. `INTERACTIVE-028`
passes by proving they are machine-labeled Experimental and **absent from
production defaults** (plugin/Auto must not register them as default Supported
renderers). This phase does **not** graduate interactive backends even when
vendored browser bundles exist in-tree.

### Gate IDs

`CHARTS-028`, `INTERACTIVE-028`, `NATIVE-028`, `SUPPLY-028`, `REGRESS-028`,
`PKG-028`.

Inventory agreement with public docs and package metadata is required for
`PKG-028` (machine-readable
[production-grade-inventory-028.toml](../acceptance/production-grade-inventory-028.toml)).

### Trust-boundary evidence bar

Chart and native trust boundaries are owned by the gates above plus a structured
maintainer-led review under
[security-review-028/](../acceptance/security-review-028/). Verified at cut means
gate-owned adversarial suites are green and a redacted report plus disposition
ledger attaches for SVG/HTML host injection, asset pins, payload budgets, and
native malformed-input handling — same honesty bar as REVIEW-026/027. Commercial
third-party re-review remains optional follow-up.

### Upgrade fixtures

See [upgrade-fixtures-028.md](../acceptance/upgrade-fixtures-028.md): goldens
from `v0.28.0` charts/native public contracts under `tests/upgrade/`.

### Non-goals

- Declaring all visualization backends Supported as a group
- Making native acceleration required for correctness or availability
- Loading chart runtimes from unpinned public CDNs in the Supported configuration
- Claiming performance improvement from microbenchmarks without material
  application impact
- Graduating MCP, Gradio, or conformance tooling (later phases)
- Claiming full human AT / compensated screen-reader evidence for charts
- Desktop-shell / `pywebview` recipes as part of `hedron-native` graduation
- Scheduling `1.0`, SLA, or certification claims

## Acceptance

- Every 0.28-owned gate row Verified with zero Deferred
- Production-grade label used only for declared Supported inventory
- `python scripts/verify_pkg_28.py` passes without `--allow-planned` at cut
