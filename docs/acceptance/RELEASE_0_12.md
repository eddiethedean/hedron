# Hedron `v0.12` data and visualization scale acceptance

Phase 0.12 delivers advanced DataEditor capabilities, distributed/lazy data sources, a
shared column catalog, typed grid/chart events, beginner and optional visualization
adapters, offline runtime pins, and HDJ `hedron.data` / `hedron.charts` provider parity
(D-047). Evidence is indexed by [`release-gate-0.12.toml`](release-gate-0.12.toml).
**Zero Deferred:** every gate row must be Verified at cut.

## Spec packet

- [x] ROADMAP §0.12 scope accepted; D-047 recorded; optional adapters are first-party extras.
- [x] Entry gate: 0.11 evidence remains closed; 0.12 gate TOML owns Verified rows only.

## Testing contracts

- [x] `hedron.testing.data` fixtures for sources, plans, deltas, and chart/grid events.
  *(`TEST-012`)*

## Column catalog, events, views, plans

- [x] Shared typed column catalog with display-versus-write policy. *(`COL-012`)*
- [x] Typed grid and chart event contracts. *(`EVT-012`)*
- [x] Saved column/filter/sort/selection views. *(`VIEW-012`)*
- [x] Explicit `TransformPlan` with Explorer visibility. *(`PLAN-012`)*

## Sources

- [x] SQLAlchemy/Django transform-plan pushdown. *(`SRC-012`)*
- [x] Dask/distributed bounded source. *(`SRC-012-DASK`)*
- [x] Snowflake-backed bounded source. *(`SRC-012-SNOW`)*

## DataEditor / grids

- [x] Formulas, merges, Excel formatting, pivots, tree grids. *(`EDIT-012`)*
- [x] Collaborative editing auth/conflict/provenance. *(`EDIT-012-COLLAB`)*
- [x] Spreadsheet import/export beyond CSV. *(`EDIT-012-XLSX`)*
- [x] AG Grid Community client + infinite row models. *(`GRID-012-AG`)*

## Visualization

- [x] Beginner `AreaChart` / `BarChart` / `ScatterChart`. *(`CHART-012-BASIC`)*
- [x] Plotly typed events and bounded incremental updates. *(`CHART-012-EVT`)*
- [x] Annotation/overlay contract. *(`CHART-012-ANN`)*
- [x] Direct Vega-Lite + advanced Vega server transforms. *(`CHART-012-VL`)*
- [x] PyDeck, MapLibre, Folium, geospatial layers. *(`CHART-012-MAP`)*
- [x] GraphViz and Mermaid adapters. *(`CHART-012-DIAG`)*
- [x] Optional Chart.js, Great Tables, Sigma/NetworkX, Three.js, ECharts, Datashader,
  Bokeh, HoloViews/hvPlot, Pygal, Plotly resampling. *(`CHART-012-OPT`)*
- [x] Offline fingerprinted chart runtimes. *(`CHART-012-PIN`)*

## HDJ / accessibility / browser

- [x] `hedron.data` / `hedron.charts` provider parity. *(`HDJ-DEF-012`)*
- [x] Keyboard/single-pointer alternatives for spatial ops. *(`A11Y-012`)*
- [x] Three-engine Playwright matrix for grids + charts + events. *(`BROWSER-012`)*

## Exit

- [x] Full regression suite. *(`REGRESS-012`)*
- [x] Packaging rehearsal. *(`PKG-012`)*
