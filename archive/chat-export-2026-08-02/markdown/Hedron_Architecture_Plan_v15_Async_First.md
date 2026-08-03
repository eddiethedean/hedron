Hedron Architecture Plan v15

Package Integrations, DataEditor, and Async-First FastAPI Architecture

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

# Editable DataFrame and DataEditor Subsystem

Hedron should provide a first-class editable dataframe component inspired by Streamlit's editable data grid, while fitting Hedron's FastAPI, HTMX, addressable-component, security, and persistent-application architecture.

## Product Positioning

- DataEditor is a flagship Hedron component for data-heavy internal tools, administrative applications, and analytical workflows.

- The experience should feel as approachable as Streamlit while remaining compatible with ordinary FastAPI routing, dependencies, authorization, persistence, and testing.

- The browser owns spreadsheet-like interaction; Hedron owns schema, validation, transport, persistence, security, and component lifecycle.

## Beginner API

- Minimal usage: DataEditor(data).

- Saveable usage: DataEditor(data, key="users", on_save=save_users).

- Model-driven usage: DataEditor(data, row_model=UserRow, on_save=save_users).

- Hedron should infer common editors, labels, validation rules, read-only fields, and enum choices from the row model.

## Browser Architecture

- Implement the interactive grid as a Web Component rather than rerendering the table after each keystroke.

- The Web Component owns cell selection, keyboard navigation, copy and paste, local undo and redo, temporary unsaved state, and row virtualization.

- HTMX owns resource-level operations such as initial loading, dataset changes, batch saves, success and error summaries, and refreshing related components.

- FastAPI and Hedron own data loading, validation, authorization, conflict detection, persistence, and audit behavior.

## Recommended Grid Backend

- Use Tabulator as the default initial browser grid because it is MIT-licensed, framework-independent, editable, virtualized, and usable without Node.js.

- Wrap Tabulator behind Hedron's DataEditor API so application code does not depend directly on Tabulator-specific options.

- Offer AG Grid Community as an optional backend for teams already using it.

- Do not make Handsontable the default because common commercial use cases require paid licensing; support it only as a separately licensed adapter.

## Typed Row Models and Columns

- Use Hedron Model and Field metadata to infer column types and editor behavior.

- Support text, integer, decimal, boolean, date, datetime, select, enum, and read-only columns in the MVP.

- Allow explicit column overrides through TextColumn, NumberColumn, CheckboxColumn, DateColumn, SelectColumn, and related configuration objects.

- Keep browser validation advisory; server-side row and field validation remains authoritative.

## Change-Set Protocol

- Do not resend the entire dataframe on every save. The browser maintains a typed change set.

- A change set records updated cells, inserted rows, deleted row identifiers, and an optional dataset version.

- The server validates the change set against a DataChanges\[RowModel\] contract before persistence.

- Structured validation failures identify row, column, and message so the browser can preserve edits and focus the first invalid cell.

## Save Modes

- Manual batch save is the default and safest beginner mode.

- Cell commit sends one completed cell edit at a time.

- Row commit validates and saves a whole row together.

- All modes use the same typed change-set and result contracts so applications can change modes without replacing persistence logic.

## Data Sources and Scale

- Accept list\[dict\], list\[HedronModel\], Pandas, Polars, and PyArrow inputs.

- Use Narwhals in the optional data package for dataframe schema normalization without requiring conversion to Pandas.

- Introduce a DataEditorSource protocol for paged, filtered, sorted, or database-backed datasets.

- Provide adapters such as InMemorySource, PandasSource, PolarsSource, SQLAlchemySource, SQLModelSource, and DjangoQuerySetSource.

- Large datasets must use server-side pagination, filtering, sorting, and allowlisted query fields rather than full serialization to the browser.

## Concurrency and Conflicts

- Support optimistic concurrency through dataset or row version values.

- Reject stale updates instead of silently overwriting newer data.

- Return structured conflict details containing row, column, submitted value, current value, and current version.

- The grid should offer reload, retain-and-retry, compare, and cancel behaviors for conflicts.

## Security Requirements

- Saving, inserting, and deleting require CSRF protection and explicit authorization.

- Editable fields must be explicitly writable; visibility in the grid never implies permission to update.

- The server must reject changes to read-only or unauthorized columns even when a client manually alters the request.

- Apply bounded page sizes, sort and filter allowlists, safe JSON serialization, secret-field redaction, audit logging, and private caching defaults.

- Arbitrary JavaScript cell editors and formatters are disallowed by default; use registered safe editor identifiers.

## HTMX and Component Integration

- DataEditor is an addressable Hedron component with typed data and save resources.

- After successful changes, the server may emit HX-Trigger events such as employeesChanged.

- Other Hedron components can refresh when those events fire.

- Major filter or dataset changes may replace the complete editor through HTMX, while normal cell editing stays local to the Web Component.

## Component Explorer Integration

- Add a dedicated Data panel showing backend, source, row model, loaded rows, editable columns, save mode, pending changes, and conflict policy.

- Expose schema, column configuration, sample data, active filters, pending change sets, validation results, endpoint URLs, security policy, and timing.

- Explorer edits must use isolated sample data by default and must never mutate production data without an explicit authenticated configuration.

## Packaging

- Create a hedron-data package containing DataTable, DataEditor, column models, change-set models, source protocols, and normalization.

- Ship the default Tabulator integration through hedron-data-tabulator or the hedron\[data\] extra.

- Offer hedron-data-aggrid and hedron-data-handsontable as optional adapters.

- No Node.js or npm installation should be required for any official adapter.

## MVP Scope

- Tabulator-backed Web Component.

- Pandas, Polars, PyArrow, list\[dict\], and Hedron-model inputs.

- Model-derived text, number, boolean, date, datetime, and select columns.

- Read-only columns, stable row keys, manual batch save, row insertion, and deletion.

- Structured validation errors, optimistic-concurrency hooks, CSRF and authorization integration.

- Explorer integration, accessible keyboard editing, and CSV download.

## Deferred Capabilities

- Formulas, merged cells, Excel-formatting parity, collaborative real-time editing, pivot tables, and nested tree grids.

- Arbitrary JavaScript editors, automatic database persistence, spreadsheet import/export beyond CSV, and enterprise-only grid features.

## Illustrative API

**Minimal**

> DataEditor(df)

**Model-driven**

> class EmployeeRow(Model):  
> employee_id: int = Field(label="ID", read_only=True)  
> name: str = Field(min_length=1)  
> department: Literal\["Engineering", "Finance", "Operations"\]  
> salary: Decimal = Field(minimum=0, display="currency")  
> active: bool = True  
>   
> DataEditor(  
> employees,  
> row_model=EmployeeRow,  
> on_save=save_employees,  
> )

**Large-data source**

> DataEditor(  
> source=SQLAlchemySource(Employee, session_factory),  
> pagination="server",  
> row_model=EmployeeRow,  
> )

## Responsibility Boundary

| Layer | Owns | Does not own |
|----|----|----|
| Web Component | Cell editing, selection, keyboard behavior, local undo/redo, virtualization | Authorization, persistence, final validation |
| HTMX | Loading, saves, component replacement, cross-component refresh events | Per-keystroke grid state |
| Hedron | Models, schemas, change sets, endpoint wiring, diagnostics, security defaults | Database-specific business rules |
| Application | Authorization policy, persistence rules, transactions, auditing requirements | Grid rendering mechanics |

## DataEditor Design Principle

Hedron should provide Streamlit-like editable dataframe ergonomics while preserving the architecture of a normal web application: typed FastAPI endpoints, explicit persistence, reusable components, scalable server-side data sources, inspectable HTMX behavior, and security that remains authoritative on the server.

# Async-First FastAPI Integration

Hedron treats FastAPI's asynchronous request model as a first-class platform capability. Async behavior belongs at explicit component boundaries such as endpoints, actions, data sources, dependencies, lazy resources, jobs, and plugin lifecycles. HTML rendering remains deterministic, concurrency remains structured, and client cancellation propagates through all request-owned work.

## Design Principles

- Support both def and async def without forcing synchronous applications to adopt async syntax.

- Automatically await declared asynchronous factories and sources.

- Keep rendering and HTML serialization synchronous unless profiling proves an async rendering lifecycle is necessary.

- Use explicit structured concurrency rather than hidden task creation.

- Prefer lazy addressable components for deferred UI over general streamed-document rendering.

- Move long-running work into job backends instead of holding HTTP requests open.

- Propagate cancellation and timeouts through all request-owned work.

- Build on FastAPI, Starlette, AnyIO, and Python asyncio rather than creating a separate runtime.

## Async Component Endpoints and Factories

Pages, addressable components, and typed actions may be synchronous or asynchronous while returning the same Hedron component types.

> @app.page("/users/{user_id}")  
> async def user_page(  
> user_id: int,  
> service: UserService = Depends(get_user_service),  
> ) -\> UserPage:  
> user = await service.get(user_id)  
> activity = await service.get_recent_activity(user_id)  
> return UserPage(user=user, activity=activity)
>
> @addressable  
> async def UserTable(  
> team_id: int,  
> service: UserService = Depends(get_user_service),  
> ) -\> UserTableComponent:  
> users = await service.list_team_users(team_id)  
> return UserTableComponent(rows=users)

- No separate AsyncComponent base type.

- Component return annotations remain HTML contracts.

- Async actions retain CSRF, authorization, HTMX response, and validation behavior.

- Plain FastAPI integration continues to use the explicit HTML(...) response wrapper.

## Prepare Then Render

Most rendering should remain deterministic and CPU-local. If advanced components need asynchronous preparation, Hedron should separate data preparation from tree generation.

> class ReportPanel(Component):  
> async def prepare(self, context: RenderContext) -\> PreparedComponent:  
> report = await context.reports.load(self.props.report_id)  
> return PreparedComponent(state={"report": report})  
>   
> def render(self, prepared: PreparedComponent) -\> Node:  
> return ReportView(report=prepared.state\["report"\])

- prepare() performs async I/O.

- render() builds the component tree without hidden I/O.

- serialize() converts the tree into escaped HTML.

- This advanced lifecycle is deferred until endpoint factories and async sources prove insufficient.

## Structured Parallel Data Loading

Independent dashboard queries may run concurrently, but Hedron should never infer concurrency merely from the component tree.

> results = await hedron.gather(  
> revenue=revenue_service.summary(),  
> incidents=incident_service.open_items(),  
> activity=activity_service.recent(),  
> )  
>   
> return Dashboard(  
> revenue=results.revenue,  
> incidents=results.incidents,  
> activity=results.activity,  
> )

- hedron.gather() uses structured concurrency, ideally asyncio.TaskGroup or an AnyIO task group.

- A failing child task cancels sibling work unless a declared partial-failure strategy is used.

- Request cancellation cancels all request-owned child tasks.

- Detached create_task() calls during request rendering are discouraged and diagnosed.

## Async Dependencies and Lifetimes

- Preserve FastAPI Depends and Security behavior without wrapping it in a Hedron-specific container.

- Support async yield dependencies for database sessions, HTTP clients, and other scoped resources.

- Keep dependencies alive until ordinary responses finish rendering and streaming responses finish iteration.

- Compose Hedron internal startup and shutdown with the application lifespan context manager.

- Start plugins in dependency order and shut them down in reverse order.

> @asynccontextmanager  
> async def lifespan(app: Hedron):  
> app.state.http = httpx.AsyncClient()  
> app.state.jobs = await create_job_backend()  
> yield  
> await app.state.http.aclose()  
> await app.state.jobs.close()  
>   
> app = Hedron(lifespan=lifespan)

## Async Data Protocols

All data-facing protocols should permit synchronous and asynchronous implementations through the same public component APIs.

- DataEditorSource.fetch() and apply() for paginated editing and persistence.

- VisualizationSource.load() for charts, maps, and large-data renderers.

- Async option providers for selects and autocomplete controls.

- Async download sources for generated reports and exports.

- Async object adapters for Auto() and the Data Intelligence Layer.

- Async cache loaders and plugin-provided data sources.

> class UsersSource(DataEditorSource\[UserRow\]):  
> async def fetch(self, query: DataQuery) -\> DataPage\[UserRow\]: ...  
> async def apply(self, changes: DataChanges\[UserRow\]) -\> DataSaveResult\[UserRow\]: ...

## Lazy Components as the Default Async UI Pattern

Addressable components and HTMX provide a natural server-native deferred-loading model. The initial page can render quickly while independent resources load asynchronously.

> RevenueChart(  
> lazy=True,  
> period="12m",  
> fallback=RevenueSkeleton(),  
> )

- The initial document renders a placeholder with aria-busy.

- HTMX requests the component resource after page load.

- The async FastAPI endpoint loads data and returns the final component.

- Timeout, retry, error, and stale-cache behavior can be configured per resource.

- Lazy component routes preserve their own dependencies and authorization rules.

## Async Regions

A later AsyncRegion component may declare how groups of independent resources load.

- together: await all loaders and render the complete region.

- independent: render placeholders and load each addressable component separately.

- ordered: reveal resources in declared priority order.

- The MVP implements independent behavior using ordinary lazy HTMX resources.

## Timeouts, Cancellation, and Disconnects

- Do not swallow asyncio.CancelledError.

- Use try/finally for resource cleanup.

- Cancel request-owned child loaders when the client disconnects or HTMX aborts a request.

- Do not shield routine component work from cancellation.

- Ensure streaming generators yield control at await points.

- Support route- and component-level timeout policies.

> ExternalStatus(  
> timeout=3,  
> timeout_fallback=StatusUnavailable(),  
> )

- Normal endpoint timeout default: fail the request.

- Independent lazy component timeout default: render a retryable error component.

- Optional policies: error, fallback, stale-cache, or partial-region rendering.

## Background Tasks and Durable Jobs

Small post-response work should use FastAPI BackgroundTasks. Durable, retryable, distributed, or CPU-heavy work belongs in an external job system.

> return UserTable(rows=users).after_response(  
> send_welcome_email,  
> user.id,  
> )

- after_response() compiles into Starlette/FastAPI background tasks.

- Hedron does not create its own in-process executor.

- A JobBackend protocol supports Celery, Dramatiq, ARQ, Taskiq, or cloud queue integrations.

- JobStatus is an addressable polling component that can transition into success, failure, or download-ready components.

- Long-running jobs should return immediately and update through polling, SSE, or a future live-region transport.

## Streaming, SSE, and WebSockets

- General streamed HTML documents are deferred because they complicate layout validity, asset ordering, error handling, and dependency lifetimes.

- Lazy addressable components remain the default deferred-rendering mechanism.

- Focused incremental lists may later use chunked HTML.

- One-way live updates such as logs and progress may use Server-Sent Events.

- Bidirectional collaborative interactions may use WebSockets.

- SSE and WebSocket support should be optional packages built on FastAPI transports, not a new Hedron event runtime.

## Async Caching and Single-Flight

> @cache_data(ttl=60)  
> async def load_summary(team_id: int) -\> Summary:  
> ...

- Concurrent cache misses for the same key should share one in-flight load.

- A disconnected waiter should not necessarily cancel shared cache work.

- Failures are not cached unless explicitly configured.

- Authenticated data must include the relevant security context in cache keys.

- Cache entries must distinguish public, private, tenant, locale, and permission-sensitive data.

- The Explorer should report cache hits, misses, waits, and stampede prevention.

## Sync Compatibility and Blocking Work

- Synchronous def endpoints remain fully supported.

- Hedron preserves FastAPI thread-pool execution for synchronous route and dependency functions.

- Blocking I/O must not run directly on the event loop.

- hedron.run_sync() may wrap unavoidable legacy blocking calls.

- CPU-intensive work should use a process worker or external job service rather than the event-loop thread pool.

> result = await hedron.run_sync(  
> legacy_client.load_report,  
> report_id,  
> )

## Explorer Async Diagnostics

- Display dependency, loader, render, and serialization timing separately.

- Show concurrent wall time versus estimated sequential time.

- Mark sync versus async loaders, cache status, timeouts, cancellations, and row or byte counts.

- Warn about long blocking operations on the event loop.

- Warn about detached tasks that outlive the request.

- Redact security-sensitive arguments and returned values.

- Expose request cancellation and timeout outcomes for addressable resources.

## Async Testing

- Provide pytest-anyio-compatible async clients and fixtures.

- Test async component factories, actions, and data sources.

- Test timeout fallbacks and cancellation cleanup.

- Test structured concurrency failure behavior.

- Test lifespan startup and reverse-order shutdown.

- Test background-task registration without requiring execution in every unit test.

- Add future helpers for SSE and WebSocket components.

> @pytest.mark.anyio  
> async def test_user_table(async_client):  
> response = await async_client.get(  
> "/\_hedron/components/user-table"  
> )  
> assert response.status_code == 200

## Async Security Requirements

- Preserve authentication, authorization, CSRF, and dependency scopes across async component routes.

- Do not allow lazy loading to bypass parent-page authorization.

- Propagate security context into cache keys and job submissions.

- Apply timeouts to remote-service calls to reduce resource exhaustion risk.

- Bound concurrency for expensive component loaders and third-party service calls.

- Redact secrets from traces, errors, job metadata, and Explorer diagnostics.

- Treat cancellation as normal control flow rather than an application error.

## Async MVP and Roadmap

- MVP: sync and async component-returning endpoints.

- MVP: async addressable component factories and typed actions.

- MVP: async FastAPI dependencies with correct yield cleanup.

- MVP: async DataEditor and visualization source protocols.

- MVP: lazy HTMX components, cancellation safety, timeouts, and retryable fallbacks.

- MVP: lifespan integration, async plugin hooks, async testing helpers, and Explorer timing traces.

- Near term: structured hedron.gather(), async cache single-flight, JobBackend protocol, and background-task helpers.

- Later: streamed documents, SSE live regions, WebSocket components, distributed tracing, and adaptive concurrency controls.

## Async Acceptance Criteria

- The same Hedron application may mix def and async def endpoints safely.

- Async component resources preserve FastAPI dependency injection and security metadata.

- Client cancellation stops all request-owned work without leaking tasks or resources.

- Lazy components render usable fallback, error, and retry states.

- Timeout behavior is explicit, testable, and visible in the Explorer.

- No blocking synchronous I/O is silently executed on the event loop.

- Long-running work is represented as jobs rather than open requests.

- Explorer traces clearly separate I/O preparation from deterministic HTML rendering.

## Updated Async Principle

Hedron embraces asynchronous I/O at component boundaries: endpoints, actions, data sources, dependencies, and addressable resources may be async. Rendering remains deterministic, concurrency remains structured, long work becomes jobs, and client cancellation propagates through all request-owned work.
