---
status: beta
---

# Chart APIs


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Shipped in `0.6.0`; high-fidelity first-party line in **`0.38` / `hedron-charts` `0.2.0`**

!!! info "Phase 0.38 first-party charts"

    [RFC-0069](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md) / D-066: typed `ChartSpec` / `ChartPlan`,
    ABI-conforming `hedron-chart`, SVG/Canvas rendering, accessible fallbacks, and deterministic
    export. Beginner `LineChart` / `AreaChart` / `BarChart` / `ScatterChart` compile to the new
    grammar. `MatplotlibChart` remains Supported; Plotly/Altair stay Experimental.

## Availability

Install `hedron[charts]>=0.44.0,<0.45` (or `hedron-charts>=0.2.0,<0.3`). See
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

## Public surface

All names below are exported from `hedron_charts`; `__version__` reports the independently
versioned charts package, not the Hedron flagship version.

| Surface | Purpose | Stability |
|---|---|---|
| `Chart`, `ChartSpec`, `ChartPlan` | Advanced schema-versioned authoring and deterministic compilation result | Beta |
| `LineChart`, `AreaChart`, `BarChart`, `ScatterChart` | Beginner row-mapping components compiled to `ChartSpec` | Beta |
| `MatplotlibChart`, `MatplotlibAdapter` | Static Matplotlib SVG/PNG path | Beta / Supported capability |
| `PlotlyChart`, `PlotlyAdapter`, `AltairChart`, `AltairAdapter` | Familiar-library adapters; full browser runtimes remain opt-in | Experimental capability |
| `parse_chart_spec`, `compile_chart` | Validate a mapping and compile it to a `ChartPlan` | Beta |
| `beginner_to_spec`, `chart_from_beginner` | Convert a beginner chart call into a spec or rendered `Chart` | Beta |
| `export_svg`, `export_csv`, `export_json`, `plan_export_bundle` | Deterministic, policy-checked server-side exports | Beta |
| `compile_figure`, `apply_annotations`, `optional_adapters` | Figure compilation, annotation, and optional-adapter discovery | Beta or adapter-specific |
| `RUNTIME_PINS`, `pinned_runtime`, `verify_pin`, `ensure_pin_stubs` | Inspect and verify vendored runtime metadata; the legacy stub name now validates real assets | Beta |
| `TAG_NAME` | The first-party custom-element tag (`hedron-chart`) | Beta ABI |
| `__version__` | Installed `hedron-charts` distribution version | Beta |

Core signatures:

```python
Chart(spec: ChartSpec | Mapping[str, Any] | None = None, *, class_: str | None = None)
parse_chart_spec(value: Mapping[str, Any] | ChartSpec) -> ChartSpec
compile_chart(spec: ChartSpec | Mapping[str, Any]) -> ChartPlan
beginner_to_spec(*, kind, data, x, y, title, description, color=None) -> ChartSpec
export_svg(plan: ChartPlan, *, authorized: bool = True, width: int | None = None) -> str
export_csv(plan: ChartPlan, *, authorized: bool = True) -> str
export_json(plan: ChartPlan, *, authorized: bool = True) -> str
plan_export_bundle(plan: ChartPlan, *, authorized: bool = True) -> dict[str, Any]
```

### Advanced `Chart(spec=...)`

```python
from hedron_charts import Chart, ChartSpec

spec = {
    "schema_version": 1,
    "data": {"rows": [{"x": 1, "y": 2}, {"x": 2, "y": 5}]},
    "marks": [{"type": "line", "encodings": {"x": {"field": "x"}, "y": {"field": "y"}}}],
    "accessibility": {"title": "Trend", "description": "Demo line"},
}
page_chart = Chart(spec)
```

`ChartSpec` is immutable and rejects unknown fields. Its public top-level fields are:

| Field | Type / default | Contract |
|---|---|---|
| `schema_version` | integer, `1` | Unknown versions fail closed (`HED-CHART-0020`) |
| `data` | inline rows plus optional name/field declarations | The compiler consumes `rows`; `name` is metadata and is not a remote loader |
| `marks` | one or more mark definitions | Accepts `line`, `area`, `bar`, `point`, `rect`, `rule`, `box`, `arc`, `ohlc`, or `candlestick`; paint coverage is narrower (below) |
| `scales`, `guides`, `transforms` | tuples, empty by default | The compiler resolves domains/guides and applies the implemented transform subset; unknown values fail closed |
| `composition`, `annotations` | mappings / tuples | Only a list in `composition.facet` is currently bounded; annotations validate at the schema boundary but are not copied into `ChartPlan` in `0.2.0` |
| `interaction` | typed interaction flags | Flags are recorded in the plan; the current host directly implements a subset (below) |
| `theme` | light, dark, forced-colors, or print | Density, locale, timezone, and tokens are carried in the plan; host styling uses public `--hedron-chart-*` CSS variables |
| `export` | SVG/PNG/CSV/JSON/print enabled by default | Each server export still requires an authorized caller |
| `renderer` | `svg` (or `canvas`) | The compiler can choose Canvas for dense marks and records the reason |
| `accessibility` | required title and description | Builds summary, interaction help, and optional tabular fallback |

Call `parse_chart_spec(mapping)` when only validation is needed. Call
`compile_chart(spec_or_mapping)` to obtain the deterministic `ChartPlan`, including
fingerprints, transformed rows, resolved domains/guides, renderer decision, accessibility
plan, assets, limits, warnings, layout, theme, interaction, and export policy. `Chart()` with
no spec raises `ValueError` when compiled or rendered.

### Nested mapping shapes

The main nested mappings reject unknown fields just like the top-level model:

| Mapping | Fields |
|---|---|
| `data` | `name`, `rows`, `fields` |
| `fields[]` | `name`, `type`, `key` |
| `marks[]` | `type`, `encodings`, `tooltip`, `filled`, `stroke_width`, `opacity`, `identity` |
| `encodings.<channel>` | `field`, `type`, `scale`, `title`, `aggregate`, `stack`, `bin`, `sort`, `value` |
| `scales[]` | `name`, `type`, `domain`, `range`, `nice`, `zero`, `clamp`, `padding` |
| `guides[]` | `kind`, `scale`, `title`, `orient`, `format`, `ticks` |
| `transforms[]` | `op`, `field`, `as`, `params` |
| `annotations[]` | `kind`, `text`, `x`, `y`, `x2`, `y2` |

Field and encoding types are `number`, `string`, `boolean`, `temporal`, or `geo`. Supported
encoding channel names are `x`, `y`, `x2`, `y2`, `color`, `size`, `opacity`, `shape`, `stroke`,
`detail`, `group`, `order`, `tooltip`, `text`, `open`, `high`, `low`, and `close`.

### Compiler contract versus current host coverage

`ChartSpec` acceptance is broader than the specialized painting implemented by the `0.2.0`
browser host. Use this matrix when deciding whether the first-party host is sufficient:

| Feature | Compiler / plan | Current `hedron-chart` host |
|---|---|---|
| `line`, `area`, `bar`, `point` | Validated and compiled | Dedicated SVG behavior; these back the four beginner components |
| `rect`, `rule`, `box`, `arc`, `ohlc`, `candlestick` | Validated and compiled | No family-specific painter yet; do not infer fidelity from schema acceptance |
| Scales and guides | Domains/guides are inferred or preserved | Axes and legends are not painted by the lightweight host in `0.2.0` |
| Annotations | Schema validation only | Not represented in the current plan or painted |
| SVG | Default below 2,500 marks | Family-specific behavior for line/area/bar/point |
| Canvas | Selected at 2,500 marks or by request | Dense-series painter plus an HTML navigation list; verify non-series output |
| Interaction | All typed flags are preserved | Directly emits `inspect`, `focus`, `select`, and `reset`; other event names are registered for forward compatibility |

Use `MatplotlibChart` for a reviewed static figure when an advanced family needs painting that the
first-party host does not yet implement. Plotly and Altair are available as Experimental explicit
opt-ins.

### Implemented transforms

The compiler has dedicated implementations for `filter`, `aggregate`, `sort`, `sample`, `stack`,
`bin`, and `fold`, plus numeric/string calculation behavior for `add`, `subtract`, `multiply`,
`divide`, `negate`, `abs`, `round`, `floor`, `ceil`, `min`, `max`, `coalesce`, `concat`, `lower`,
`upper`, and `length`. Other names in the closed operator catalog validate but currently preserve
the first input value rather than providing distinct window/temporal semantics. Test transformed
rows in `ChartPlan.transformed_rows` before relying on an advanced operator.

## Beginner `LineChart`

```python
from hedron import Hedron, Page
from hedron_charts import LineChart

app = Hedron(title="Demo", security="standard", session_secret="replace-me")

data = [
    {"month": "Jan", "revenue": 10},
    {"month": "Feb", "revenue": 14},
    {"month": "Mar", "revenue": 18},
]


@app.page("/")
def home() -> Page:
    return Page(
        LineChart(
            data,
            x="month",
            y="revenue",
            title="Monthly revenue",
            description="Revenue increased during the period.",
        ),
        title="Revenue",
    )
```

## Familiar-library adapters

```python
from hedron_charts import AltairChart, MatplotlibChart, PlotlyChart

PlotlyChart(figure, description="Revenue by region")
MatplotlibChart(figure, alt="Revenue by month")
AltairChart(chart, description="Declarative Vega-Lite figure")
```

Every chart declares title, description or alt text, output mode, data policy, and optional
tabular fallback. Interactive adapters register host shims and serialize specifications as
non-executable data. Plotly, Altair, and optional adapters reject callback-shaped content and
unapproved remote assets. The first-party `ChartSpec` compiler does not execute strings in
open metadata mappings; only documented fields affect its plan.

!!! note "Plotly / Vega runtimes (Experimental)"

    Interactive Plotly.js and Vega/vega-embed runtimes ship as **vendored,
    fingerprinted Experimental** assets under `hedron-charts` (`RUNTIME_PINS`).
    Host scripts fail closed when `window.Plotly` / `vegaEmbed` are missing.
    They are **not** production Auto defaults (`INTERACTIVE-028`); opt in with
    `Auto(..., as_="plotly")` / explicit `PlotlyChart` / `AltairChart`.
    Supported production charts remain the first-party beginner/`ChartSpec` path and
    Matplotlib.

## Export and failure behavior

Compile a plan once, authorize in application code, then export only the enabled formats:

```python
from hedron_charts import compile_chart, export_csv, export_svg

plan = compile_chart(spec)
svg = export_svg(plan, authorized=user_can_export)
csv_text = export_csv(plan, authorized=user_can_export)
```

`export_json` emits fingerprints, theme metadata, and transformed rows.
`plan_export_bundle` returns the enabled server-generated SVG, CSV, JSON, and print outputs. The
`ExportPolicy.png` flag is a browser capability; it does not add PNG to the Python bundle, and
there is no root-level `export_png` function in `0.2.0`. The deterministic Python SVG export is a
semantic series representation, not a family-specific renderer for every accepted mark.

Export functions default to `authorized=True` for already-authorized internal calls. Route
handlers should always pass an explicit authorization decision. Export calls fail with
`HED-CHART-0061` when `authorized=False`, `HED-CHART-0062` when the format is disabled,
and `HED-CHART-0063` when SVG dimensions exceed `max_px`. Remote URLs in export payloads
can be checked with `hedron_charts.export.assert_no_remote_urls`, which fails closed with
`HED-CHART-0073`.

Parsing/compilation failures use `HED-CHART-0020`–`HED-CHART-0033` for unsupported schema
versions, unknown fields/operators/marks/scales, invalid encodings, and transform failures.
Row and payload bounds use `HED-CHART-0002` / `HED-CHART-0003`; adapter callback, remote-URL,
and active-SVG guards use `HED-CHART-0004`–`HED-CHART-0006`. Prototype-pollution keys use
`HED-CHART-0070`, while field/transform/facet/mark/label bounds use `HED-CHART-0071` /
`HED-CHART-0072`. Missing optional backends include a bounded PyPI install command. Payload
limits and server-transform policies are visible in Explorer.

## Bounds and enforcement

| Limit | Default | Enforcement in `0.2.0` |
|---|---:|---|
| Rows | 10,000 | Compiler, beginner components, and adapters |
| Serialized payload | 1,000,000 bytes | Beginner components and plotting-library adapters; recorded but not separately measured by `compile_chart()` |
| Declared fields | 64 | Compiler |
| Transforms | 32 | Compiler |
| Facets | 16 | Compiler when `composition.facet` is a list |
| Compiled marks | 10,000 | Compiler |
| Labels | 500 | Recorded in `ChartPlan.limits`; no separate label counter yet |
| Export width/height | 4,096 px | Python SVG export |

The compiler redacts output fields whose names contain `secret` or `password`. That narrow helper
does not replace application-level data minimization: remove confidential rows and fields before
building a chart.

## Testing

```python
from hedron import RenderMode, render

result = render(page_chart, mode=RenderMode.FRAGMENT)
assert "<hedron-chart" in result.html
assert "data-hedron-payload=" in result.html
assert "hedron-chart-fallback" in result.html

plan_again = compile_chart(spec)
assert plan.spec_fingerprint == plan_again.spec_fingerprint
```

Browser tests can wait for `hedron-chart[data-hedron-chart-mounted='1']`; no-JavaScript tests
should assert that the figure, summary, and table remain useful before enhancement.

## See also

- [Charts and HTMX](../guides/charts-and-htmx.md)
- [`hedron-charts` package guide](../packages/hedron-charts.md)
- [Chart components](../components/charts.md)
- [Error codes](../guides/error-codes.md#hed-chart)
- [Streamlit migration](../guides/streamlit-migration.md)
