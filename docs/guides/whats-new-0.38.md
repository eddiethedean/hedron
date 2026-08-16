# What's new in Hedron 0.38

**Published** as `v0.38.0` on 2026-08-14. Historical pin: `hedron>=0.38.0,<0.39` and `hedron-charts>=0.2.0,<0.3`.
For new apps, use `hedron>=0.44.0,<0.45`; see [What’s new in 0.40](whats-new-0.41.md).

Phase **0.38** ships Hedron's first-party high-fidelity chart system
([RFC-0069](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md) / D-066).

## Highlights

- Typed, schema-versioned **`ChartSpec`** compiles to a deterministic **`ChartPlan`**
- ABI-conforming **`hedron-chart`** Web Component with SVG default and Canvas for dense marks
- Beginner **`LineChart` / `AreaChart` / `BarChart` / `ScatterChart`** keep their call shapes and compile to the new grammar
- **`MatplotlibChart`** remains Supported; Plotly/Altair stay explicit Experimental adapters
- Public chart tokens, typed keyboard/pointer interactions, accessible summary/table fallbacks, and deterministic SVG/CSV/JSON/print export

## Pins

```bash
pip install "hedron>=0.38.0,<0.39" "hedron[charts]>=0.38.0,<0.39"
# independent charts line:
pip install "hedron-charts>=0.2.0,<0.3"
```

## See also

- [Chart API](../api/CHART.md)
- [hedron-charts package](../packages/hedron-charts.md)
- [Upgrade](upgrade.md)
- [RELEASE_0_38](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_38.md)
