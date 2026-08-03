# RFC-0011: Visualization

**Status:** Accepted

## Architecture

Hedron exposes stable chart components and a `VisualizationAdapter` protocol. Established libraries own graphical expression; Hedron owns lifecycle, data limits, transport, browser assets, caching, accessibility, security, HTMX refresh, and Explorer metadata.

An adapter compiles a supported value into JSON, SVG, an image asset, or a controlled trusted fragment. JSON is serialized as data, never constructed inside executable strings. Browser runtimes are pinned, fingerprinted, and served locally by default.

## Initial adapters

1. Matplotlib for static SVG or PNG.
2. Plotly for interactive figure JSON.
3. Altair/Vega-Lite for declarative specifications.

Narwhals may normalize dataframe inputs. ECharts, Datashader, maps, Bokeh, and HoloViz interoperability are deferred.

Every visualization requires a title and description or an explicit documented waiver. Static images require alt text. Simple charts should offer tabular fallbacks. Raw JavaScript callbacks and unapproved remote URLs are rejected.

## Acceptance criteria

- Large data and payload limits fail predictably or invoke an explicit server transform.
- Explorer reports backend, rows, payload, assets, timing, accessibility, and security policy.
- Secret fields are excluded from samples and output.
- Optional libraries are lazily imported and missing extras produce exact installation guidance.

