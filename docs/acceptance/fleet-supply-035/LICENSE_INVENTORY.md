# Fleet license inventory (SUPPLY-035)

Owning gate: `SUPPLY-035`. Whole-fleet publishable channels for Hedron **0.35**.

## Supported publish channels

| Channel | Artifacts | License |
|---|---|---|
| PyPI | `hedron`, `hedron-*`, `fastapi-workbench` | MIT |
| npm | `hedron-runtime-node` | MIT |
| Maven | `io.hedron:hedron-runtime-java` | MIT |
| crates.io | `hedron-native` (optional Rust accel) | MIT |

All Supported and tooling-grade Supported packages ship `LICENSE` (MIT) with matching
`[project].license` / `license-files` metadata.

## Experimental surfaces

Experimental live SSE/WS, `experimental-ui`, Plotly/Altair, and MCP mutations remain
**Experimental** — they may ship under MIT packages but are excluded from production-grade
Supported claims in `production-grade-inventory-035.toml`.

## Pass criteria

- Every inventory `channel = "pypi"|"npm"|"maven"` row has an MIT license file in-tree
- Evidence bundle license inventory generated via `scripts/license_inventory.py`
- No proprietary redistributed runtimes required for Supported static chart paths
