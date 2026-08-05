# hedron-charts

Visualization adapters and chart components for Hedron: beginner `LineChart`,
Matplotlib static SVG/PNG, Plotly interactive JSON, and Altair/Vega-Lite
specifications.

**Maturity:** Alpha on the coordinated **`0.11.0`** train — pin versions and expect
churn. Interactive Plotly/Vega **full browser runtimes** remain **experimental**:
Hedron ships host shims that fail closed when `window.Plotly` / `window.vegaEmbed`
are missing. Applications may supply pinned local runtimes; first-party offline
runtime fingerprinting is not Supported yet.

```bash
pip install "hedron-charts==0.11.0"
# Optional backends:
pip install "hedron-charts[matplotlib]"
pip install "hedron-charts[plotly]"
pip install "hedron-charts[altair]"
# Or via the flagship extra:
pip install "hedron[charts]"
```

Requires `hedron-core`. See
[charts and HTMX](https://hedron.readthedocs.io/en/latest/guides/charts-and-htmx/)
and [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).
