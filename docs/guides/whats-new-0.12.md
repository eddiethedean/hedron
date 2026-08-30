# What’s new in Hedron 0.12

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and published 1.0 status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

Phase **0.12** ships data and visualization scale (D-047) with **zero Deferred** gate rows.

## Highlights

- Shared column catalog with display-versus-write policy.
- Grid and chart events, saved views, and explicit `TransformPlan` budgets.
- Advanced DataEditor: formulas, merges, pivots, tree grids, collaborative merge/recovery,
  spreadsheet import/export beyond CSV, AG Grid Community client + infinite row models.
- Dask and Snowflake bounded sources; SQLAlchemy allowlisted pushdown.
- Beginner `AreaChart` / `BarChart` / `ScatterChart`; Plotly events; annotation overlays.
- Optional adapters: Vega-Lite, PyDeck, MapLibre, Folium, GraphViz, Mermaid, Chart.js,
  Great Tables, Sigma/NetworkX, Three.js, ECharts, Datashader, Bokeh, HoloViews, Pygal,
  Plotly resampling — each with local-asset/CSP/payload/fallback contracts.
- Offline fingerprinted chart runtime pins.
- HDJ `hedron.data` / `hedron.charts` provider parity.
- Three-engine Playwright matrix for grids/charts and spatial keyboard alternatives.

## Install

```bash
pip install "hedron>=0.12.0" "uvicorn[standard]"
```

See [What’s ready](whats-ready.md) and [Upgrade](upgrade.md).
