# hedron-charts

Visualization adapters and chart components for Hedron: beginner `LineChart`,
Matplotlib static SVG/PNG, Plotly interactive JSON, and Altair/Vega-Lite
specifications.

Interactive Plotly/Vega **full browser runtimes** are **experimental**: Hedron ships
host shims that fail closed when `window.Plotly` / `window.vegaEmbed` are missing.
Applications may supply pinned local runtimes; first-party offline runtime
fingerprinting remains deferred on the 0.6 maintenance line.

```bash
pip install hedron-charts
# Optional backends:
pip install "hedron-charts[matplotlib]"
pip install "hedron-charts[plotly]"
pip install "hedron-charts[altair]"
# Or via the flagship extra:
pip install "hedron[charts]"
```

Requires `hedron-core`. Coordinated train: **`0.10.1`** (first released at `0.6.0`).
Interactive Plotly/Altair full browser runtimes remain **experimental**.
