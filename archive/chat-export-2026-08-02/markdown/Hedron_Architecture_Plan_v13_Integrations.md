**Hedron Architecture Plan v13**

*Package Integrations, Visualization Ecosystem, and Dependency Strategy*

Status: Working Architecture and Adoption Plan • August 2026

Hedron is a Python-first, FastAPI-first, security-first component framework for HTML and HTMX applications. This revision consolidates the package integration strategy and defines how third-party Python visualization, data, authentication, content, testing, and developer-tooling packages fit into Hedron without bloating the core framework.

# 1. Product Direction

- Hedron should be the glue between proven Python libraries rather than a replacement for them.

- The required dependency set must remain intentionally small.

- Optional integrations should be isolated behind extras or separate packages.

- Hedron owns component lifecycle, transport, security, accessibility, discovery, and HTMX behavior.

- Integrated libraries retain ownership of their domain-specific functionality, such as chart construction, authentication protocols, image processing, or Markdown parsing.

- Every optional integration must degrade cleanly when the dependency is absent.

# 2. Packaging Model

> hedron \# batteries-included FastAPI distribution  
> hedron-core \# framework-neutral component engine  
> hedron-flask \# Flask adapter; does not install FastAPI  
> hedron-django \# Django adapter; does not install FastAPI  
> hedron-explorer \# optional development explorer  
> hedron-charts \# shared visualization protocols and components

The PyPI distribution named hedron remains the recommended starting point and installs FastAPI. Flask and Django users install dedicated distributions that depend on hedron-core and re-export the shared component API.

# 3. Required Dependencies

| **Distribution** | **Required dependency** | **Purpose** |
|----|----|----|
| hedron-core | Pydantic | Internal implementation of Hedron Model, Props, FormModel, Field, validation, and schema extraction. |
| hedron | hedron-core | Shared rendering, models, HDN, HTMX metadata, security, scoped styles, and component registry. |
| hedron | FastAPI | Flagship routing, dependency injection, OpenAPI, request validation, and ASGI integration. |
| hedron | Starlette | Indirect FastAPI runtime foundation and response primitives. |
| Browser assets | HTMX | Bundled or locally served browser interaction layer; no Node.js installation required. |

No visualization, database, authentication, Markdown, image, or data-science package belongs in Hedron core.

# 4. Optional Dependency Policy

- Integrations should use extras for small, closely related adapters and separate distributions for large subsystems.

- Imports must be lazy so importing hedron never imports Plotly, Pandas, SQLAlchemy, Pillow, or similar packages unless used.

- Missing extras should produce actionable errors with exact installation commands.

- Adapters must be independently testable and version-gated against supported upstream releases.

- Integrations must use public upstream APIs rather than relying on undocumented internals.

- Every adapter must document security, browser assets, payload size, and accessibility implications.

# 5. Development and Authoring Integrations

| **Package** | **Recommended role** | **Packaging** | **Priority** |
|----|----|----|----|
| watchfiles | Development file watching for Python, HDN, scoped CSS, and examples. | hedron\[dev\] | MVP |
| Rich | Readable CLI diagnostics, tables, trace summaries, and security reports. | hedron\[dev\] | MVP |
| Typer | Hedron CLI commands such as new, inspect, check, build, and routes. | hedron\[cli\] or bundled CLI | MVP |
| Pygments | Server-side syntax highlighting for docs, code blocks, Explorer source views. | hedron\[code\] | Early |
| markdown-it-py | CommonMark-compatible Markdown parser with configurable plugins. | hedron\[markdown\] | Early |
| Faker | Generate safe sample props in the Component Explorer. | hedron\[explorer\] | Early |
| Factory Boy | Optional test fixture integration for component examples. | hedron\[test\] | Later |
| Syrupy | Snapshot testing for rendered component output. | hedron\[test\] | Early |
| pytest | First-class testing helpers and plugin fixtures. | hedron\[test\] | MVP |

# 6. Content and Media Integrations

| **Integration** | **Recommended use** | **Security notes** |
|----|----|----|
| markdown-it-py | Markdown component and documentation content. | Raw HTML disabled by default; output must pass through Hedron trust/sanitization policy. |
| Pygments | Code highlighting. | Generated HTML is trusted only from the registered formatter; user code remains escaped. |
| Pillow | Image resizing, optimization, thumbnails, responsive variants, and fingerprints. | Enforce file-size, pixel-count, format, and decompression-bomb limits. |
| email-validator | Email field validation through Hedron Field types. | Optional extra; never expose the underlying Pydantic dependency model. |
| Icon packs / SVG registries | Lucide, Heroicons, or organization icon sets. | Inline SVG must come from trusted registered assets; arbitrary SVG input is prohibited. |
| HTML sanitizer adapter | Sanitize user-authored rich text before creating TrustedHtml. | Hedron should integrate a maintained sanitizer rather than maintain its own sanitizer or rely on deprecated packages. |

# 7. Authentication and Authorization Integrations

- Hedron must keep authentication framework-native and must not create a competing identity system.

- FastAPI Depends and Security remain authoritative for addressable components and typed actions.

- Django authentication, permissions, sessions, and CSRF middleware remain authoritative in hedron-django.

- Flask extension and session conventions remain authoritative in hedron-flask.

| **Package / system** | **Recommended role** | **Status** |
|----|----|----|
| Authlib | OAuth 1/2, OpenID Connect clients, providers, JOSE, and framework integrations. | Primary official OAuth/OIDC adapter candidate |
| FastAPI security utilities | Bearer, OAuth2, OpenID Connect metadata, and security scopes. | Native flagship path |
| FastAPI Users | Optional prebuilt user-management integration if its API and maintenance status meet release criteria. | Evaluate; do not hard-depend |
| Django auth | Authentication and authorization for hedron-django. | Native adapter behavior |
| Flask-Login / ecosystem equivalents | Session-oriented Flask authentication. | Optional adapter integrations |

# 8. Database and Data Integrations

| **Package** | **Hedron integration** | **Boundary** |
|----|----|----|
| SQLAlchemy | AutoTable, AutoForm, filters, relationship-aware labels, pagination helpers, Explorer query panel. | Hedron must not become an ORM. |
| SQLModel | Convenience adapter for users combining Pydantic-style models and SQLAlchemy. | Optional; no core dependency. |
| Django ORM | ModelForm-like component generation and QuerySet-aware tables in hedron-django. | Django adapter only. |
| Pandas | Accepted DataTable and Chart data source. | Never required by core. |
| Polars | First-class DataTable and Chart data source with efficient columnar paths. | Official data adapter candidate. |
| PyArrow | Portable tabular interchange and efficient chart serialization. | Optional data subsystem dependency. |
| Narwhals | Compatibility layer across Pandas, Polars, PyArrow, cuDF, Modin, and related DataFrame APIs. | Recommended normalization layer in hedron-data or hedron-charts. |
| Dask / lazy frames | Large or deferred datasets. | Adapter must avoid accidental collection and enforce browser payload limits. |

# 9. Data Visualization Architecture

Hedron should expose a stable chart resource model while allowing established visualization libraries to own graphical expression.

> Chart / PlotlyChart / AltairChart / MatplotlibChart  
> ↓  
> VisualizationAdapter  
> ↓  
> CompiledVisualization  
> ↓  
> JSON spec, SVG, image, or trusted fragment  
> ↓  
> Hedron component + HTMX resource + browser runtime

## 10. Visualization Adapter Protocol

> class VisualizationAdapter(Protocol):  
> name: str  
>   
> def supports(self, value: object) -\> bool: ...  
>   
> def compile(  
> self,  
> value: object,  
> \*,  
> context: ChartContext,  
> ) -\> CompiledVisualization: ...

- Hedron owns lifecycle, transport, caching, assets, CSP, accessibility contracts, Explorer metadata, and HTMX refresh behavior.

- Adapters own conversion from library objects to browser specifications or static outputs.

- No adapter may inject arbitrary inline JavaScript callbacks by default.

- All JSON must be emitted with a real serializer rather than concatenated into script blocks.

- Each chart must provide a title and accessible description or an explicit waiver.

# 11. Recommended Visualization Integrations

| **Library** | **Best fit** | **Output strategy** | **Priority** |
|----|----|----|----|
| Matplotlib | Static scientific, analytical, report, and publication charts. | SVG or PNG asset endpoint. | 1 - MVP |
| Plotly | Broad interactive dashboards and recognized business/scientific charting. | Figure JSON + one registered Plotly browser runtime. | 2 - Early |
| Vega-Altair | Declarative statistical charts, inspectable specifications, and strong Explorer support. | Vega-Lite JSON + Vega runtime; optional static fallback. | 3 - Early |
| Narwhals | DataFrame normalization for chart and table adapters. | Schema and column access without eager Pandas conversion. | 4 - Early |
| ECharts / pyecharts | Enterprise dashboards, gauges, Sankey, graphs, trees, and specialized charts. | Validated ECharts option JSON. | 5 - Later |
| Datashader | Millions of points, dense geographic or time-series rendering. | Server-rendered image/tile resource with viewport parameters. | 6 - Later |
| Folium | Compatibility with existing Leaflet-centric Python geospatial workflows. | Extracted/isolated map component; avoid full standalone page injection. | 7 - Later |
| Bokeh | Standalone interactive plots and advanced scientific visualization. | Standalone JSON/model embedding only at first. | 8 - Interop |
| HoloViews / hvPlot | Data-science interoperability across Bokeh, Matplotlib, Plotly, Datashader, and varied DataFrames. | Convert through supported backends; do not absorb Panel app lifecycle. | 9 - Interop |
| Pygal | Lightweight Python-native SVG charts and restricted environments. | SVG asset or trusted compiled output. | 10 - Optional |

# 12. Beginner Chart API

> LineChart(  
> data,  
> x="month",  
> y="revenue",  
> title="Monthly revenue",  
> description="Revenue increased steadily across the six-month period.",  
> )

The configured default backend may implement the beginner chart. The public component contract must remain stable even if the default backend changes.

# 13. Familiar-Library APIs

> PlotlyChart(plotly_figure)  
> AltairChart(altair_chart)  
> MatplotlibChart(matplotlib_figure, alt="...")  
> EChart(option=echarts_option)

# 14. Large-Data and Payload Policy

- Browser-bound row counts and JSON payload sizes must be capped by default.

- The Explorer must show rows received, rows emitted, specification size, asset size, and server transform mode.

- Altair integrations may use VegaFusion and vl-convert-python for server-side transforms and static fallback generation.

- Plotly integrations may later support plotly-resampler for zoom-aware high-frequency time series.

- Datashader should be used for aggregation/rasterization rather than shipping millions of rows to the browser.

- Lazy and distributed frames must never be collected implicitly without an explicit policy.

# 15. Geospatial Visualization

- Folium is an interoperability path for existing Python map code.

- A direct MapLibre Web Component should be considered for Hedron-native interactive mapping because it offers clearer lifecycle and asset control.

- GeoViews and HoloViews can be supported through interoperability adapters.

- All remote tile providers, tokens, and URLs must be allowlisted and visible in Explorer security diagnostics.

- Sensitive coordinates and user-specific geospatial layers must use private caching defaults.

# 16. Chart Accessibility

- Interactive charts require a title and meaningful textual description.

- Simple charts should optionally generate an accessible tabular fallback.

- Static charts require alt text; Hedron must not claim to understand arbitrary scientific meaning automatically.

- Color must not be the only encoding for critical distinctions.

- Keyboard and screen-reader behavior belongs in the chart Web Component contract.

- The Explorer should identify missing descriptions, missing fallback data, inaccessible interactions, and overlarge payloads.

# 17. Chart Security

- Browser runtimes must be pinned, fingerprinted, and served locally by default.

- Raw JavaScript callbacks in Plotly, Vega, ECharts, or Bokeh specifications are rejected by default.

- External URLs, image references, map tiles, and remote assets require URL-policy validation.

- Specifications must be serialized outside executable script contexts whenever possible.

- Chart data shown in the Explorer must redact Secret fields and respect component authorization.

- User-specific chart resources default to private, no-store caching.

- SVG output is treated as active content and is served through a controlled asset path or sanitizer/trust boundary.

# 18. Component Explorer Integration

| **Explorer panel** | **Information** |
|----|----|
| Visualization | Backend, output mode, runtime, rows, payload size, fallback, and render timing. |
| Specification | JSON specification or static-render settings. |
| Data schema | Columns, types, nullability, secret/redacted columns, and sample policy. |
| Accessibility | Title, description, alt text, fallback table, keyboard support. |
| Security | Remote assets, raw HTML/JS, CSP compatibility, caching, sensitive data. |
| Assets | Runtime JS, CSS, fonts, images, and fingerprints. |
| HTMX | Addressable endpoint, refresh behavior, lazy loading, targets, and swap policy. |

# 19. Testing Integrations

| **Package / method** | **Use** |
|----|----|
| pytest | Core test runner, client fixtures, component route tests, adapter conformance. |
| Syrupy | Snapshot rendered HTML, normalized manifests, and chart specs. |
| httpx / FastAPI TestClient | Addressable component and action endpoint tests. |
| Playwright - optional | Browser-level HTMX, Web Component, chart, and accessibility tests. |
| axe-core through browser tooling - optional | Deep accessibility verification beyond server-side static checks. |
| visual regression tooling - optional | Chart and component screenshot regression testing. |

# 20. Official Package and Extra Roadmap

| **Package / extra** | **Contents** | **Release phase** |
|----|----|----|
| hedron\[dev\] | watchfiles, Rich, development reload and diagnostics. | MVP |
| hedron\[cli\] | Typer-based CLI. | MVP |
| hedron\[test\] | pytest plugin, Syrupy helpers, test clients. | MVP |
| hedron\[markdown\] | markdown-it-py and secure Markdown component. | Early |
| hedron\[code\] | Pygments integration. | Early |
| hedron\[images\] | Pillow-based image pipeline. | Early |
| hedron\[email\] | email-validator-backed Hedron email fields. | Early |
| hedron-explorer | Component Explorer and previews. | Early |
| hedron-charts | Chart protocol, base components, data limits, accessibility and security policy. | Early |
| hedron-charts\[matplotlib\] | Matplotlib adapter. | First chart release |
| hedron-charts\[plotly\] | Plotly adapter. | Second chart release |
| hedron-charts\[altair\] | Altair/Vega-Lite adapter. | Third chart release |
| hedron-data | Narwhals-based tabular normalization and DataTable adapters. | Early |
| hedron-auth | Authlib and framework-native security conveniences, not an identity system. | Later |
| hedron-lsp | HDN language server and editor tooling. | Later |

# 21. Integrations Hedron Should Avoid Owning

- Do not create a proprietary ORM.

- Do not create a proprietary authentication protocol implementation.

- Do not build a chart grammar before proving that established libraries cannot meet the need.

- Do not maintain an HTML sanitizer or cryptographic primitives internally.

- Do not require Jinja solely because it is familiar; HDN and the component renderer remain the primary rendering model.

- Do not round-trip component trees through BeautifulSoup or lxml for ordinary rendering.

- Do not integrate complete competing application frameworks such as Panel as internal Hedron runtimes.

# 22. Integration Acceptance Criteria

- Installing base Hedron does not import or install optional heavy packages.

- Every missing integration produces a concise install command.

- All integration browser assets support local serving and strict CSP configurations.

- All adapters expose security and accessibility metadata to the Component Explorer.

- All chart adapters obey payload limits and secret-field redaction.

- All adapters include contract tests and compatibility ranges.

- Optional integrations do not change core rendering semantics.

- Applications can disable any automatic integration discovery.

# 23. Updated Implementation Sequence

1\. Core component rendering, models, FastAPI responses, security defaults, and HTMX behavior.

2\. Development tooling: watchfiles, Rich diagnostics, CLI, pytest integration, and snapshots.

3\. Component Explorer foundation and shared registry.

4\. Markdown, code highlighting, image pipeline, and email field extras.

5\. hedron-data with Narwhals and DataTable normalization.

6\. hedron-charts base protocol and Matplotlib adapter.

7\. Plotly and Altair adapters with Explorer, security, and accessibility support.

8\. SQLAlchemy, Authlib, and framework-specific ecosystem adapters.

9\. ECharts, Datashader, geospatial, and HoloViz interoperability.

10\. Optional native acceleration only after profiling identifies a concrete bottleneck.

# 24. Guiding Principle

**Hedron owns integration mechanics, not domain reinvention.** It should make proven Python libraries feel native inside typed, addressable, secure components while preserving their strengths, keeping the core small, and making every automatic behavior visible in the Component Explorer.

# 25. Reference Notes

This integration plan was reviewed against current official documentation and project materials for markdown-it-py, Pygments, Pillow, Authlib, Vega-Altair, HoloViews, hvPlot, Datashader, and related Python ecosystem projects in August 2026. Exact minimum versions should be selected and tested when each adapter enters implementation; the architecture intentionally avoids pinning speculative minimums in the plan.
