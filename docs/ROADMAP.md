# Roadmap to 1.0

Hedron advances through cumulative product phases from 0.0 to 1.0. Phase 0.0 is the documentation and foundation baseline and publishes no package. Each implementation phase from 0.1 onward produces an initial release whose tag adds a patch component: phase 0.1 produces `v0.1.0`, phase 0.2 produces `v0.2.0`, and so on through phase 0.8 producing `v0.8.0`; phase 1.0 produces `v1.0.0`. Python package metadata omits the tag prefix (`0.1.0`, `0.2.0`, …, `1.0.0`).

Phase numbers describe capability maturity, not calendar commitments. Patch releases such as `v0.1.1` remain maintenance releases within their owning phase and do not create new roadmap phases. Scope may move to a later phase, but an initial release may not claim phase completion with a partially implemented public contract.

## Release-wide definition of done

Every implementation phase from 0.1 onward—and its corresponding initial release—requires:

- accepted owning RFCs and updated architectural decisions;
- documented and typed public APIs;
- implementation specifications and automated acceptance coverage;
- secure defaults, threat scenarios, and secret redaction;
- applicable accessibility contracts and keyboard behavior;
- performance and payload measurements for new critical paths;
- CLI or Component Explorer visibility for new inference;
- migration notes, examples, and compatibility evidence;
- a working increment of the reference application using packaged-style imports.

## 0.0 — Specification and project foundation (documentation baseline; no package release)

**Outcome:** Hedron has an agreed product definition and an implementation-ready engineering baseline.

### Scope

- Accept the vision, philosophy, design principles, and non-goals.
- Adopt the RFC and architectural decision process.
- Resolve supported Python, FastAPI, Starlette, Pydantic, HTMX, and browser ranges in the compatibility contract.
- Decide the repository, package, namespace, configuration, identifier, and diagnostic-code layouts.
- Accept the RFCs and public contracts required by phases 0.1 and 0.2.
- Define CI, typing, formatting, release, and compatibility policies, and record the pre-publication license decision.
- Establish the canonical specification as the self-contained authority for implementation.

### Exit gate

- All 29 baseline RFCs and their referenced public contracts are Accepted as planned designs; roadmap phases still control availability.
- Decisions D-001 through D-032 are resolved, with no open decision that can materially change the phase 0.1 core architecture.
- Compatibility, project layout, configuration, identifiers, diagnostics, built-ins, and engineering checks are explicit enough to create the package skeleton without inventing public behavior.
- The canonical specification is self-contained and requires no historical source corpus.

## 0.1 — Typed rendering core (`v0.1.0`)

**Outcome:** `hedron-core` can define, validate, compose, and safely render components without FastAPI installed.

### Scope

- Hedron `Model`, `Props`, `FormModel`, `EventPayload`, `Field`, `Secret`, `TrustedHtml`, `SafeUrl`, and `UrlPurpose` types.
- Component protocol, native node algebra, children, slots, fragments, page metadata, and deterministic identity.
- Context-aware HTML serializer with deterministic attribute behavior.
- Framework-neutral render context, `RenderResult`, component registry, diagnostics, and trace stages.
- Initial built-ins sufficient to express semantic pages, forms, layouts, and navigation.
- Unit, snapshot, adversarial escaping, typing, and benchmark foundations.

### Exit gate

- Core tests run with no FastAPI, Flask, Django, or Node.js installation.
- Representative pages and fragments render deterministically and pass the component, security, and accessibility core suites.
- The reference application’s static component tree renders outside an HTTP request.

## 0.2 — Secure FastAPI application MVP (`v0.2.0`)

**Outcome:** Developers can build and test a secure component-oriented FastAPI CRUD application with HTML and HTMX.

### Scope

- `HedronRoute`, `HedronRouter`, thin `Hedron()` application, response classes, and plain-FastAPI `HTML(...)` integration.
- Pages, explicit addressable components, component references, typed actions, automatic forms, and validation fragments.
- Stable and self-targeting component identities, refresh controls, lazy resources, polling, pagination, and infinite-scroll helpers.
- Full-page versus HTMX fragment behavior, safe targets, loading/error/retry states, redirects, out-of-band swaps, `HX-Trigger` events, history policy, and approved HTMX headers.
- FastAPI dependency injection, security, lifespan, middleware, `BackgroundTasks`, `StaticFiles`, dependency overrides, and exception compatibility.
- Typed `SessionState` framework adapter, explicit URL/form state, and documented boundaries between request, session, cache, and browser-local state.
- Contextual security controls, CSRF integration, safe redirects, private authenticated caching defaults, security headers, and route-exposure diagnostics.
- Accurate `text/html` OpenAPI responses, deterministic operation IDs, and `x-hedron-*` metadata.
- Minimal CLI inspection and registry-backed Explorer for routes, components, previews, HTMX inference, and security findings.

### Exit gate

- The authenticated CRUD portion of the reference application works in both `Hedron()` and plain FastAPI router modes.
- FastAPI conformance, security, HTMX, OpenAPI, sync/async endpoint, and dependency-cleanup suites pass.
- A new user reaches a secure working page in under five minutes using published instructions.

## 0.3 — Authoring, styles, assets, and themes (`v0.3.0`)

**Outcome:** Developers can move from built-in Python composition to complete markup and presentation control without adding Node.js.

### Scope

- HDN grammar, parser, portable expression engine, type checking, render-program compilation, formatter, diagnostics, and source maps.
- `inspect` and `eject` workflows for built-in component templates.
- Scoped CSS AST compiler, typed style symbols, keyframe scoping, explicit globals, variants, cascade layers, and token contracts.
- Theme registration, light/dark modes, accessible tokens, and application override layers.
- Fingerprinted asset pipeline, component-relative assets, external CSP-compatible bundles, and offline production manifests.
- Component-folder discovery for templates, styles, examples, tests, documentation, and registered browser modules.
- Web Component registration, typed custom-event contracts, light-versus-Shadow-DOM policy, and lifecycle-safe behavior across HTMX swaps.
- Incremental development watching and atomic registry/build replacement.

### Exit gate

- The reference application contains equivalent representative Python and HDN components.
- Clean builds are deterministic, production requires no runtime HDN/CSS compilation, and strict CSP passes.
- HDN, scoped-style, theme, asset, and build acceptance suites pass.

## 0.4 — Developer platform and ecosystem contracts (`v0.4.0`)

**Outcome:** Hedron is inspectable, extensible, and practical for contributors and component-package authors.

### Scope

- Full Component Explorer navigation, component graph and inverse consumers, request simulator, render/HTMX/style/asset traces, examples, and dependency overrides.
- Explorer panels for source, HDN, styles, assets, accessibility, security, performance, async timing, caches, packages, settings, and inference explanations.
- CLI `new`, `dev`, `build`, `check`, `inspect`, `eject`, `components`, `routes`, `graph`, `preview`, and component audit commands.
- Stable text, JSON, and SARIF diagnostics with remediation and suppression policy.
- Pytest helpers, async clients, Syrupy-style snapshots, Playwright browser hooks, axe-style accessibility checks, visual-regression hooks, named examples, and adapter-conformance framework.
- Plugin metadata, deterministic discovery, capability audit, lifecycle, compatibility gates, rollback, and Explorer extension contracts.
- Production build manifests, package component conventions, project scaffolding, and author documentation.

### Exit gate

- Every framework inference introduced through 0.4 has an Explorer or CLI explanation and override.
- A third-party sample package contributes a component, example, style, asset, diagnostic, and Explorer metadata using public contracts.
- Explorer, CLI, plugin, build, testing, accessibility, and production-exposure acceptance suites pass.

## 0.5 — Data application toolkit (`v0.5.0`)

**Outcome:** Hedron can build Streamlit-approachable data tools while retaining normal web application architecture.

### Scope

- Deterministic `Auto()` renderer registry and bounded Data Intelligence inspection.
- `DataTable`, `DataEditor`, typed columns, typed change sets, validation results, and optimistic-concurrency conflicts.
- In-memory and paged sync/async data-source protocols; Narwhals-based optional dataframe normalization.
- `list[dict]`, Hedron-model, Pandas, Polars, and PyArrow inputs without mandatory dataframe dependencies.
- Tabulator-backed Web Component with keyboard editing, virtualization, local pending state, manual batch, row, and cell save modes, insert/delete, and CSV export.
- Structured row/field validation and conflict UX for reload, retain-and-retry, compare, and cancel behaviors.
- Server-authoritative writable-field policy, CSRF, authorization, audit hooks, bounded queries, and private caching.
- `cache_data`, `cache_component`, explicit invalidation tags/versioning, single-flight behavior, scope metadata, and Explorer cache traces.
- `Metric`, `FileUpload`, `DownloadButton`, `CodeViewer`, `JSONViewer`, `Progress`, `Status`, `Toast`, `Expander`, `Tabs`, `Sidebar`, and explicit `Grid` components.

### Exit gate

- The reference application securely edits a paged async dataset, handles validation and stale-update conflicts, and demonstrates intelligent rendering and utility components.
- Forged writes, cache-scope leaks, unsafe uploads/downloads, inaccessible grid behavior, and implicit large-data collection are covered by acceptance tests.

## 0.6 — Visualization and first-party integrations (`v0.6.0`)

**Outcome:** Hedron supports production-quality dashboards and common Python content workflows without bloating the core.

### Scope

- Stable visualization adapter and source contracts.
- Matplotlib static output, Plotly interactive figures, and Altair/Vega-Lite specifications.
- Accessible descriptions, alt text, tabular fallbacks, data/payload limits, local browser runtimes, and strict CSP.
- Markdown, syntax highlighting, image processing, email validation, and trusted sanitizer integration paths.
- Trusted icon and SVG registries with explicit active-content policy.
- SQLAlchemy/SQLModel data adapters and Authlib/FastAPI security conveniences without owning persistence or identity.
- AG Grid Community interoperability and a stable adapter boundary for separately licensed DataEditor backends.
- Explorer visualization, data schema, payload, assets, accessibility, cache, and security panels.
- Compatibility ranges, lazy imports, precise missing-extra guidance, and upstream contract tests.

### Exit gate

- The complete data-and-chart reference workflow runs offline with locally served assets and no secret-field leakage.
- Initial visualization and content adapters pass security, accessibility, payload, browser-lifecycle, and optional-dependency tests.

## 0.7 — Framework adapters and production operations (`v0.7.0`)

**Outcome:** Hedron has a credible multi-framework core and documented production operating model.

### Scope

- `hedron-flask` and `hedron-django` distributions that preserve framework-native routing, security, CSRF, sessions, forms, lifecycle, and URL reversing.
- Shared cross-adapter component, rendering, HTMX, security, and testing conformance suites.
- Container, multi-worker, reverse-proxy/root-path, external static-host, and offline deployment guides.
- Structured async diagnostics, cancellation and timeout traces, bounded concurrency, single-flight backend contracts, and graceful shutdown.
- Structured `hedron.gather()`, `hedron.run_sync()` legacy blocking-call bridge, async cache backends, and lifecycle-ordered plugin resources.
- FastAPI `BackgroundTasks` helpers and pluggable durable `JobBackend` contracts with addressable status resources.
- Logging, tracing, health/readiness, cache/job failure, component-package audit, and supply-chain operating guidance.

### Exit gate

- Advertised FastAPI, Flask, and Django packages pass their declared compatibility and conformance matrices.
- The reference application deploys behind a prefixed reverse proxy with multiple workers, external cache/job test doubles, and externally hosted static assets.

## 0.8 — Release candidate and hardening (`v0.8.0`)

**Outcome:** Hedron’s `v1.0.0` public surface is frozen and supported by release-quality evidence.

### Scope

- Public API, HDN, registry metadata, plugin protocol, compiled artifact, and rendered-markup stability classifications.
- Compatibility matrix, semantic-versioning rules, deprecation window, upgrade tooling, changelog, and migration guides.
- Complete security threat-model review, dependency and browser-asset audit, accessibility audit, and performance budgets.
- Packaging tests for wheels and source distributions across supported platforms and Python versions.
- Documentation usability testing, error-message review, example verification, and no-Node/offline test path.
- Release-candidate stabilization: only fixes, documentation, compatibility work, and explicitly approved scope changes.

### Exit gate

- All `v1.0.0` acceptance documents pass using published release-candidate artifacts.
- No unresolved critical/high security issue, release-blocking accessibility defect, undocumented breaking change, or unowned compatibility failure remains.
- The full reference application is deployed and tested from a clean installation.

## 1.0 — Stable Hedron (`v1.0.0`)

**Outcome:** Hedron is a stable, documented, secure, and supportable framework for typed FastAPI component applications.

### Release commitments

- Stable documented public APIs governed by semantic versioning and the compatibility policy.
- FastAPI flagship experience, framework-neutral core, and accurately stated Flask/Django support.
- Secure components, addressable resources, HTMX interaction, HDN, scoped styles, themes, Explorer, data tools, charts, plugins, and production tooling at their documented stability levels.
- Published reference application, tutorials, API reference, architecture/RFC history, deployment guides, and migration support.
- Reproducible release artifacts, provenance, vulnerability response process, and maintained acceptance baselines.

### 1.0 gate

The [`v1.0.0` release acceptance specification](acceptance/RELEASE_1_0.md) is complete and signed off. Features that do not meet the gate are clearly marked experimental or removed from the 1.0 promise rather than shipped as silently incomplete stable APIs.

## Complete feature-to-release ledger

This ledger is the coverage check for planned `v1.0.0` capabilities. The detailed phase sections above remain normative; the ledger prevents a subsystem or cross-cutting requirement from disappearing between plans.

### Foundation and server architecture

| Planned capability | Target phase | Notes |
|---|---:|---|
| Vision, principles, non-goals, decisions, RFC process | 0.0 | Architecture must be accepted before implementation. |
| Runtime and browser compatibility ranges | 0.0 | Selected from current supported upstream releases. |
| Package/repository/configuration/diagnostic layout | 0.0 | Includes CI, licensing, typing, formatting, and release policy. |
| `hedron-core`, `hedron`, and optional-package dependency graph | 0.0 | Prevents framework and heavy-integration leakage into core. |
| Hedron models, props, forms, events, fields, `Secret`, `TrustedHtml`, `SafeUrl`, `UrlPurpose` | 0.1 | Pydantic-backed but Hedron-owned public contract. |
| Component nodes, props, children, slots, fragments, identity | 0.1 | Framework-neutral and deterministic. |
| HTML serializer and contextual escaping | 0.1 | Text, attribute, URL, CSS, JSON, SVG/trusted boundaries. |
| Page metadata, semantic built-ins, render results, registry | 0.1 | Provides the non-HTTP rendering proof. |
| `HedronRoute`, `HedronRouter`, thin `Hedron()` | 0.2 | Uses documented FastAPI extension points. |
| Plain FastAPI `HTML(...)` and response helpers | 0.2 | Incremental adoption without subclassing. |
| Addressable components and component references | 0.2 | Exposure remains explicit; dependencies remain authoritative. |
| Typed `Action`, `AutoForm`, automatic controls, validation fragments | 0.2 | Business validation and authorization stay explicit. |
| Stable/self-targeting identities, `RefreshButton`, lazy loading, polling, pagination, infinite scroll | 0.2 | Registry-backed resource URLs and safe targets. |
| Page/fragment detection, redirects, OOB swaps, triggers, history policy | 0.2 | HTMX mechanics remain visible and overrideable. |
| OpenAPI HTML responses, operation IDs, `x-hedron-*`, hidden internal routes | 0.2 | Swagger documents HTTP; Explorer documents components. |
| Sync/async endpoints, dependencies, actions, timeouts, cancellation | 0.2 | Deterministic rendering remains synchronous. |
| `SessionState` adapter and explicit state-scope guidance | 0.2 | No global rerun-style state. |

### Authoring, browser, and presentation

| Planned capability | Target phase | Notes |
|---|---:|---|
| HDN tags, expressions, conditions, loops, slots, trusted HTML | 0.3 | JSX-familiar without arbitrary host-language execution. |
| HDN formatter, diagnostics, source maps, compiled render programs | 0.3 | No Node.js requirement. |
| `inspect` and `eject` customization workflow | 0.3 | Progressive control over built-ins. |
| Scoped classes, keyframes, globals, variants, layers | 0.3 | AST-based deterministic CSS rewriting. |
| Tokens, themes, light/dark modes, override layers | 0.3 | Accessible CSS-custom-property architecture. |
| Fingerprinted assets, CSS URL rewriting, CSP/offline manifests | 0.3 | Production performs no required runtime compilation. |
| Component folders with code, HDN, CSS, examples, tests, docs, browser modules | 0.3 | Colocated ownership with explicit discovery. |
| Web Component registration, typed events, light/Shadow DOM policy | 0.3 | Browser-local interaction integrates safely with HTMX swaps. |
| Component package authoring and browser-asset declarations | 0.4 | Public extension and audit contracts. |
| `hedron-explorer` and official Explorer browser assets | 0.2 preview; 0.4 full | Optional development distribution with production opt-in controls. |

### Developer experience and extensibility

| Planned capability | Target phase | Notes |
|---|---:|---|
| Minimal previews, route/HTMX/security inspection | 0.2 | Ships with the FastAPI MVP. |
| Full Explorer components/pages/actions/routes/settings navigation | 0.4 | Same registry as rendering and routing. |
| Explorer props/examples/request simulator/graphs/render traces | 0.4 | Includes inverse consumers and source ownership. |
| Explorer accessibility/security/performance/async/cache/package panels | 0.4 | Later integrations extend the same panels. |
| CLI new/dev/build/check/inspect/eject/components/routes/graph/preview/audit | 0.4 | Stable text, JSON, and SARIF diagnostics. |
| Development watching and atomic incremental rebuilds | 0.3–0.4 | HDN/CSS first, full registry/build at 0.4. |
| Pytest helpers, async clients, snapshots, browser/a11y/visual hooks | 0.4 | Supports named examples and conformance. |
| Plugin discovery, compatibility, capabilities, lifecycle, rollback | 0.4 | Plugins are executable packages, not sandboxed data. |
| Project scaffolding, author docs, package conventions | 0.4 | Supports third-party component packages. |

### Data, intelligence, caching, and utility UI

| Planned capability | Target phase | Notes |
|---|---:|---|
| `Auto()` renderer registry and explicit override | 0.5 | Deterministic priorities independent of import order. |
| Data Intelligence schema/size/cardinality/time/geospatial inspection | 0.5 | Bounded recommendations; no implicit lazy-data collection. |
| DataTable with paging, sorting, filtering, empty states, downloads | 0.5 | Accessible server-rendered baseline. |
| DataEditor model-derived and explicit columns | 0.5 | Text, numeric, boolean, date/time, enum/select, hidden/read-only. |
| Tabulator grid, keyboard behavior, virtualization, undo/redo, pending state | 0.5 | Browser-local editing state. |
| Typed delta changes, batch/row/cell save modes, inserts/deletes | 0.5 | Server validation remains authoritative. |
| Validation retention and optimistic conflict workflows | 0.5 | Reload, retry, compare, and cancel. |
| In-memory, paged, sync/async data-source protocols | 0.5 | App owns transactions, tenants, and domain policy. |
| Lists, Hedron models, Pandas, Polars, PyArrow, Narwhals normalization | 0.5 | Optional heavy dependencies. |
| Cache decorators, scopes, invalidation, single flight, diagnostics | 0.5 | External backends for multi-worker durability. |
| `Metric`, `FileUpload`, `DownloadButton`, `CodeViewer`, `JSONViewer` | 0.5 | Security, limits, escaping, and accessibility contracts included. |
| `Progress`, `Status`, `Toast`, `Expander`, `Tabs`, `Sidebar`, `Grid` | 0.5 | Composition and semantic patterns rather than widget-centric layout. |
| `hedron-data` and Tabulator browser adapter package | 0.5 | Core remains free of dataframe and grid dependencies. |
| SQLAlchemy/SQLModel source adapters | 0.6 | No automatic persistence or ORM ownership. |
| AG Grid Community interoperability | 0.6 | Application API remains backend-neutral. |

### Visualization, content, and service integrations

| Planned capability | Target phase | Notes |
|---|---:|---|
| Visualization adapter and async source contracts | 0.6 | Hedron owns lifecycle, transport, limits, assets, and diagnostics. |
| Beginner charts plus Matplotlib, Plotly, and Altair adapters | 0.6 | Static and interactive output modes. |
| `hedron-charts`, `hedron-charts[matplotlib]`, `[plotly]`, `[altair]` | 0.6 | Lazy optional packages with pinned local browser assets. |
| Chart descriptions, alt text, table fallbacks, payload caps | 0.6 | Security and accessibility are release gates. |
| Local pinned browser runtimes and strict CSP | 0.6 | No arbitrary JavaScript callbacks. |
| Markdown, Pygments-style code highlighting, Pillow images | 0.6 | Raw HTML and active content remain controlled. |
| `hedron[markdown]`, `[code]`, `[images]`, `[email]` extras | 0.6 | Missing extras provide exact install guidance. |
| Email validation, sanitizer integration, trusted icons/SVG | 0.6 | Optional extras with explicit trust boundaries. |
| Authlib and FastAPI security conveniences | 0.6 | No proprietary identity system. |
| Lazy imports, version gates, missing-extra guidance | 0.4–0.6 | Required for every optional integration. |

### Frameworks, operations, quality, and release

| Planned capability | Target phase | Notes |
|---|---:|---|
| Flask and Django distributions and re-exported component API | 0.7 | Do not install FastAPI. |
| `hedron-flask` and `hedron-django` release artifacts | 0.7 | Published and tested independently of the flagship package. |
| Native framework auth, CSRF, sessions, forms, lifecycle, URL reversing | 0.7 | Host framework remains authoritative. |
| Cross-adapter rendering/HTMX/security/testing conformance | 0.7 | Verifies the framework-neutral core boundary. |
| Structured gather, blocking bridge, lifecycle-ordered async resources | 0.7 | No separate async runtime or detached request tasks. |
| External cache contracts and durable job-backend protocol | 0.7 | BackgroundTasks remains for small post-response work. |
| Container, multi-worker, proxy/root-path, static host, offline deployment | 0.7 | Includes graceful shutdown and health/readiness. |
| Logging, traces, timing, cache/job failures, component supply-chain audit | 0.7 | Secrets are redacted before storage or display. |
| Security development/standard/strict profiles | 0.2, 0.8 | Baseline enforcement at 0.2; final audit at 0.8. |
| Accessibility contracts and WCAG-oriented acceptance | 0.1–0.8 | Required incrementally for every built-in and integration. |
| Performance benchmarks, payload limits, and budgets | 0.1–0.8 | Stage-level evidence before optimization. |
| Public API/artifact stability classification and freeze | 0.8 | Includes HDN, plugin, manifest, metadata, and markup promises. |
| Semantic versioning, deprecation, upgrade, migration, compatibility | 0.8 | Enforced before 1.0. |
| Published reference application and release artifacts | 0.1–1.0 | Grows cumulatively and validates clean installation. |

## RFC-to-phase coverage

| RFC | Primary phase assignment |
|---|---|
| 0001 Vision | 0.0 |
| 0002 Core architecture | 0.0–0.2; adapter proof in 0.7 |
| 0003 Component model | 0.1 |
| 0004 FastAPI integration | 0.2 |
| 0005 HDN language | 0.3 |
| 0006 Scoped styles | 0.3 |
| 0007 Component Explorer | 0.2 minimal; 0.4 full; extended through 0.7 |
| 0008 Addressable components | 0.2 |
| 0009 HTMX integration | 0.2 |
| 0010 Data components | 0.5; optional adapters in 0.6 |
| 0011 Visualization | 0.6 |
| 0012 Security | 0.1–0.8 |
| 0013 Async architecture | 0.2, 0.5, and 0.7 |
| 0014 Plugin architecture | 0.4; integration packages through 0.7 |
| 0015 Routing | 0.2 |
| 0016 OpenAPI | 0.2; Explorer/docs integration in 0.4 |
| 0017 CLI | 0.2 minimal; 0.3 compiler commands; 0.4 full |
| 0018 Packaging | 0.0–0.8 |
| 0019 Testing | 0.0–0.8 |
| 0020 Performance | 0.1–0.8 |
| 0021 Browser runtime | 0.3; rich widgets in 0.5–0.6 |
| 0022 Theming | 0.3 |
| 0023 Accessibility | 0.1–0.8 |
| 0024 Developer experience | 0.2–0.6 |
| 0025 Component lifecycle | 0.1–0.3 |
| 0026 State management | 0.2 and 0.5; operations in 0.7 |
| 0027 Data sources | 0.5–0.6 |
| 0028 Deployment | 0.7–0.8 |
| 0029 Roadmap to 1.0 | 0.0–1.0 |

## Post-1.0 candidates

The following ideas remain planned possibilities but are not part of the 1.0 commitment. Each requires a separate accepted RFC and demonstrated demand:

- **Live transport:** SSE live regions, WebSocket components, focused chunked lists, and general streamed documents.
- **Advanced async:** component-level async `prepare()` lifecycle, adaptive concurrency, and distributed tracing integrations.
- **HDN tooling:** language server, editor extensions, advanced static analysis, and guided React-to-HDN conversion.
- **Styles and assets:** route-level CSS splitting, dynamic HTMX asset negotiation, cross-file composition, optional preprocessors, advanced minification, hot style replacement, and a full design-token compiler.
- **DataEditor:** formulas, merged cells, Excel-formatting parity, pivot tables, tree grids, collaborative editing, additional enterprise grid adapters, and spreadsheet import/export beyond CSV.
- **Data scale:** Dask/distributed sources, automatic server transform planning, and more advanced lazy-query pushdown.
- **Visualization:** ECharts, Datashader, MapLibre, Folium, Bokeh, HoloViews/hvPlot, Pygal, geospatial layers, Plotly resampling, and advanced Vega server transforms.
- **Developer tooling:** AI-assisted Explorer diagnostics, visual authoring, broader migration tooling, generated component endpoint SDKs, and optional OpenAPI callback/webhook presentation tools.
- **Portability and performance:** language-neutral component specification, Java and Node runtimes, conformance code generation, and optional Rust acceleration after profiling.
