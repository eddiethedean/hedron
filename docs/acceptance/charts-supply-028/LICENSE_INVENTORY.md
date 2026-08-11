# Charts supply license inventory (SUPPLY-028)

Owning gate: `SUPPLY-028`. Baseline: Published `v0.28.0`.

## Supported runtime

| Component | Maturity | License | Notes |
|---|---|---|---|
| matplotlib | Supported | Matplotlib License (BSD-compatible) | Static SVG/PNG production default |
| hedron-charts hosts (static path) | Supported | MIT (Hedron) | Local assets only; no CDN |

## Experimental runtimes

| Component | Maturity | License | Notes |
|---|---|---|---|
| plotly.js | Experimental | MIT | Local pin under `assets/plotly/` |
| vega / vega-embed | Experimental | BSD-3-Clause | Local pins under `assets/vega/` |
| Chart.js | Experimental | MIT | Local pin under `assets/chartjs/` |
| Apache ECharts | Experimental | Apache-2.0 | Local pin under `assets/echarts/` |
| Mermaid | Experimental | MIT | Local pin under `assets/mermaid/` |
| MapLibre GL | Experimental | BSD-3-Clause | Local pin under `assets/maplibre/` |

Experimental adapters (Plotly/Altair Python, Vega hosts, map/diagram extras)
remain labeled **Experimental** and are excluded from production Auto defaults.

## Policy

- Supported chart workflows must not load unpinned CDN runtimes.
- License texts for vendored bundles live beside the assets / pins; this
  inventory is the release evidence index, not a substitute for full SPDX.
