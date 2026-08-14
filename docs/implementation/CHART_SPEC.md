# Chart grammar catalogs (phase 0.38)

**Status:** Normative under Accepted [RFC-0069](../rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md)
(D-066). `ChartSpec`, `ChartPlan`, and `hedron-chart` ship in `hedron-charts 0.2.0`.
This catalog records the accepted grammar; it is broader than some specialized behavior in the
current host. The public [runtime coverage matrix](../api/CHART.md#compiler-contract-versus-current-host-coverage)
is authoritative for observed `0.2.0` implementation coverage.

Living baseline: Published **`v0.38.0`**. Cut: Hedron **`v0.38.0`**, `hedron-charts` **`0.2.0`**.
Tracking: [#251](https://github.com/eddiethedean/hedron/issues/251).

## `ChartSpec` fields

Immutable, JSON-serializable, schema-versioned. Unknown keys fail closed.

| Field | Meaning |
|---|---|
| `schema_version` | Integer `1`. JSON schema id `hedron-chart-spec/1`. |
| `data` | Bounded inline rows plus optional name metadata and field declarations. The compiler does not resolve a remote named source. |
| `marks` | Allowlisted mark definitions (see Supported catalog in RFC-0069). |
| `encodings` | Positional, color, size, opacity, shape, stroke, detail, grouping, ordering, tooltip. |
| `scales` | Linear, log, symlog, power, time, UTC, ordinal, point, band, quantized. |
| `guides` | Axis, legend, title, and caption metadata compiled into the plan; the current lightweight host does not paint axes/legends. |
| `transforms` | Closed operator catalog only (below); dedicated `0.2.0` implementations are called out below. |
| `composition` | Open metadata mapping. `0.2.0` only bounds `composition.facet` when it is a list. |
| `annotations` | Typed text/reference-line/reference-band records validate at the schema boundary but are not copied into the current plan. |
| `interaction` | Declared inspect, focus, select, brush, zoom/pan/reset, legend-filter, crosshair, drill intent; current host subset below. |
| `theme` | Public chart token names; light/dark/forced-color/print; locale/timezone; density. |
| `export` | SVG, PNG, CSV, JSON, print policy. |
| `renderer` | Preference `svg` (default) or `canvas`. Compiler may select Canvas only under Stage 1 rules. |
| `accessibility` | Title and purpose/description are required; tabular/download alternatives compile into the plan. |

There is no executable expression channel, JavaScript callback, raw HTML tooltip, or remote
schema/data/asset loader.

## `ChartPlan` fields

Deterministic compilation result consumed by the browser host, static fallback, Explorer,
conformance fixtures, caching, and diagnostics.

| Field | Meaning |
|---|---|
| `spec_fingerprint` | Stable hash of the normalized spec. |
| `data_fingerprint` | Stable hash of transformed rows (secrets redacted). |
| `domains` | Resolved scale domains. |
| `guides` | Resolved ticks, legends, labels. |
| `marks` | Transformed mark records with counts and stable identities. |
| `renderer` | Inspectable `svg` or `canvas` decision plus reason. |
| `accessibility` | Compiled summary, encoding explanation, interaction help, bounded table/export. |
| `assets` | Fingerprinted local module/CSS list. |
| `export` | Enabled export kinds and dimension bounds. |
| `warnings` | Non-fatal diagnostics. |
| `limits` | Applied row/field/transform/facet/mark/label/payload/export floors. |

Inference is visible. Explicit author values win or fail clearly; they are not silently rewritten.

## Closed operator catalog

Calculations use this allowlist only. Unknown operators fail with a reserved `HED-CHART-*` code.

In `0.2.0`, `filter`, `aggregate`, `sort`, `sample`, `stack`, `bin`, and `fold` have dedicated
structural implementations. Numeric/string calculations have dedicated behavior for `add`,
`subtract`, `multiply`, `divide`, `negate`, `abs`, `round`, `floor`, `ceil`, `min`, `max`,
`coalesce`, `concat`, `lower`, `upper`, and `length`. Other catalog names validate but currently
preserve the first input value rather than providing distinct temporal/window semantics.

**Arithmetic / numeric:** `add`, `subtract`, `multiply`, `divide`, `negate`, `abs`, `round`,
`floor`, `ceil`, `min`, `max`, `clamp`, `coalesce`.

**Compare / logic:** `eq`, `ne`, `lt`, `le`, `gt`, `ge`, `in`, `not_in`, `is_null`, `is_not_null`,
`and`, `or`, `not`.

**String:** `concat`, `length`, `lower`, `upper`.

**Temporal:** `year`, `month`, `day`, `hour`, `minute`, `second`, `date_trunc`.

**Aggregate:** `count`, `count_distinct`, `sum`, `mean`, `median`, `min`, `max`, `stdev`, `first`,
`last`.

**Window (bounded):** `lag`, `lead`, `rank`, `dense_rank`, `row_number`, `running_sum`,
`running_mean`.

**Structural transforms:** `filter`, `aggregate`, `bin`, `stack`, `sort`, `fold`, `sample`.

## Versioned events

0.38 public event kinds (typed `CustomEvent` detail; no DOM nodes, selectors, raw HTML, callbacks,
or authorization state):

The current first-party host directly emits `inspect`, `focus`, `select`, and `reset`. The other
names are part of the accepted catalog and registered ABI but do not yet have dedicated host
operations in `0.2.0`.

| Kind | Intent |
|---|---|
| `inspect` | Structured tooltip / keyboard inspect |
| `focus` | Datum/series focus navigation |
| `select` | Point or category selection |
| `legend_filter` | Series visibility |
| `brush` | Range selection |
| `zoom` | Scale zoom |
| `pan` | Scale pan |
| `reset` | Restore default view |
| `crosshair` | Shared crosshair |
| `drill_intent` | Declared server action intent (authz/CSRF still apply) |

Async drill/actions reuse 0.37 `InteractionState`. Charts do not invent a parallel state machine.

### 0.1 `ChartEvent` mapping

Current kinds in `hedron_core.visualization` (`hover`, `click`, `click-annotation`, `box`,
`lasso`, `relayout`, `restyle`, `legend`, `extend`, `prepend`) map as follows or emit a named
remediation diagnostic:

| 0.1 kind | 0.38 kind or diagnostic |
|---|---|
| `hover` | `inspect` |
| `click` | `select` |
| `click-annotation` | `inspect` with annotation key |
| `box` | `brush` |
| `lasso` | `brush`, or `HED-CHART-0054` if lasso geometry is requested |
| `relayout` | `zoom` / `pan` |
| `restyle` / `legend` | `legend_filter` |
| `extend` / `prepend` | Fail closed `HED-CHART-0055` (streaming mutation is not in 0.38) |

## Diagnostic reservation

Existing shipped codes **stay**: `HED-CHART-0001`…`0007`, `HED-CHART-0010`…`0014`.

0.38 reserves these ownership ranges:

| Range | Owner |
|---|---|
| `HED-CHART-0020`…`0029` | Schema / version / unknown field |
| `HED-CHART-0030`…`0039` | Transform / operator / type |
| `HED-CHART-0040`…`0049` | Renderer / lifecycle / assets |
| `HED-CHART-0050`…`0059` | Interaction / events |
| `HED-CHART-0060`…`0069` | Accessibility / export |
| `HED-CHART-0070`…`0079` | Security / bounds / prototype pollution |

The `0.2.0` runtime emits `0020`–`0026`, `0030`–`0033`, `0061`–`0063`, and `0070`–`0073`;
those codes are registered in [Error codes](../guides/error-codes.md#hed-chart). Unused values in
the ranges remain reserved.

## Public chart tokens

CSS custom properties consumed by `hedron-chart` and static SVG. Private host classes are not a
Supported override surface.

| Token | Role |
|---|---|
| `--hedron-chart-color-1` … `--hedron-chart-color-8` | Categorical palette |
| `--hedron-chart-sequential` | Sequential ramp |
| `--hedron-chart-diverging` | Diverging ramp |
| `--hedron-chart-axis` | Axis line/tick |
| `--hedron-chart-grid` | Grid |
| `--hedron-chart-label` | Tick/legend/annotation type |
| `--hedron-chart-font` | Chart typography |
| `--hedron-chart-focus-ring` | Keyboard focus |
| `--hedron-chart-tooltip-bg` / `--hedron-chart-tooltip-fg` | Structured tooltip |
| `--hedron-chart-empty` / `--hedron-chart-loading` / `--hedron-chart-error` | Non-data states |
| `--hedron-chart-density-compact` / `--hedron-chart-density-ordinary` / `--hedron-chart-density-wide` | Responsive density |

Tokens must work in light, dark, high-contrast, forced-color, print, and reduced-motion modes.
Color is never the only carrier of essential meaning.

## Fallback contract

JavaScript-off, failed upgrade, and module-load failure keep a useful semantic surface:

1. **Figure** — titled container with description/alt.
2. **Summary** — compiled encoding explanation (author-reviewed; not claimed insight).
3. **Bounded table** — row-complete within `VisualizationLimits`; must not drop rows (#82).
4. **Authorized export** — Python supplies SVG/CSV/JSON/print bundle output according to policy;
   PNG remains a browser capability in `0.2.0`.

Static Matplotlib SVG/PNG remains a Supported path. First-party static SVG is also Supported for
declared families. Pixel identity with the interactive renderer is a non-goal; semantic
equivalence (data, encodings, identities, accessibility, export meaning) is required.

## Accepted D3 candidate modules

The accepted design considered this candidate set: `d3-array`, `d3-scale`, `d3-shape`, `d3-axis`,
`d3-selection`, `d3-time`, `d3-time-format`, `d3-format`, `d3-interpolate`, `d3-color`,
`d3-brush`, `d3-zoom`, optional `d3-transition` (reduced-motion gated). Not `d3-geo`,
`d3-hierarchy`, or `d3-force`. The packaged `0.2.0` first-party host is a self-contained local
module and does not expose these candidates as a consumer API or dependency contract.
