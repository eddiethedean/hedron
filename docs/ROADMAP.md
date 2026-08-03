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
- Theme registration, light/dark **token modes**, accessible tokens, and application override layers
  (system `prefers-color-scheme` and `data-theme` selectors; no first-party toggle UI yet).
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
- First-party **light/dark styling controls**: `ColorMode` / theme-mode API, accessible toggle UI,
  preference persistence (cookie/session/local with documented defaults), and explicit override of
  system preference while keeping contrast, forced-colors, and reduced-motion contracts.

### Exit gate

- The reference application securely edits a paged async dataset, handles validation and stale-update conflicts, and demonstrates intelligent rendering and utility components.
- Light/dark styling can be switched from the reference UI without breaking scoped styles or accessibility contracts.
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
- HTMX 2 browser conformance for focus, titles, live regions, OOB swaps, history misses, request
  races, error fragments, and custom-element teardown around first-party integrations.
- A shared typed FastAPI/HTMX interaction contract—`HtmxRequest`, `InteractionResult`, and
  `InteractionPolicy` or equivalent—that represents request context, primary content, validated
  targets/swaps, OOB updates, event timing, history changes, status, concurrency, and cache policy
  without hiding the resulting HTML, HTTP status, or `HX-*` headers.
- Semantic HTML response handling for FastAPI validation and common interaction outcomes: 202 job
  acceptance, 204 no-swap events, 401/403 session and authorization states, 409 conflicts, 422
  validation fragments, 429 retry states, and stable 5xx error regions. Ordinary non-HTMX API
  requests retain framework-native JSON behavior.
- Route-declared fragment regions and target-aware rendering with authorization-safe allowlists;
  boosted navigation preserves titles, canonical/history behavior, progressive full-page
  navigation, and declared assets rather than treating every page child as an interchangeable
  fragment.
- Correct page/fragment cache variation and keys (`HX-Request`, history restoration, and
  `HX-Target` only when output varies by target), plus form/search policies for `hx-sync`, disabled
  controls, indicators, `aria-busy`, CSRF, focus restoration, and idempotency where required.
- Explorer interaction debugging for ordinary, boosted, fragment, history-restore, validation,
  conflict, and error requests, including primary/OOB destinations, event timing, history effects,
  asset requirements, cache variation, and the inference/override source.
- Explicit fragment asset/head policy: predeclared shell assets by default, with conformance-gated
  evaluation of pinned `head-support`, Idiomorph, response-targets, and View Transitions where core
  HTMX behavior is insufficient.

### Exit gate

- The complete data-and-chart reference workflow runs offline with locally served assets and no secret-field leakage.
- Initial visualization and content adapters pass security, accessibility, payload, browser-lifecycle, and optional-dependency tests.
- HTMX navigation and swaps do not lose required assets, focus, accessible status, or browser-local
  widget state; any selected extension has pinned local assets and documented fallbacks.
- The reference application demonstrates the typed interaction contract, declared fragment regions,
  semantic 422 validation, a conflict/error path, OOB updates, correctly varied page/fragment
  caching, synchronized submission, and independently navigable boosted URLs.

### Phase 0.6 closure gate

Phase 0.7 implementation does not begin merely because `0.6.0` metadata is internally
consistent. The 0.6 behavioral contracts are dependencies of every later framework adapter and
must first be closed with linked evidence:

- typed interaction headers cannot bypass local-URL, selector, cache, or approved-header policy;
- OOB swap/select behavior, declared fragment-region authorization, target-aware rendering, and
  `private` / `no-store` / target-specific cache behavior pass integration and browser tests;
- chart fallback output and trusted SVG/icon paths pass adversarial active-content tests;
- Plotly and Vega browser runtimes are pinned, fingerprinted, locally served, and exercised offline;
- SQLAlchemy/SQLModel adapters apply bounded query operations rather than collecting an unbounded
  result before paging; and
- every checked 0.6 acceptance requirement names an automated test or immutable evidence artifact.

Unclosed behavior is fixed in the 0.6 maintenance line or explicitly reclassified as experimental;
it is not silently inherited as a portable 0.7 contract.

## 0.7 — Framework adapters and production operations (`v0.7.0`)

**Outcome:** Hedron has a proven portable adapter boundary, capability-accurate framework
integrations, and a documented production operating model.

### Entry gate

- The phase 0.6 closure gate is green.
- Adapter, operations, jobs, and observability acceptance specifications exist with stable IDs and
  named evidence commands.
- Supported Flask, Django, ASGI/WSGI server, cache-backend, and browser ranges are recorded in the
  compatibility matrix before adapter implementation begins.
- Adapter-neutral interaction, URL, asset/build-manifest, session/auth signal, lifecycle, and
  diagnostic contracts have accepted public ownership in `hedron-core`; concrete framework request
  and response objects remain in their adapter packages.
- The Explorer dependency direction is resolved so adapter packages do not acquire FastAPI through
  a required development or runtime dependency.

### Staged delivery

#### 0.7A — Portable adapter foundation

- Move adapter-neutral interaction values and policies out of the FastAPI package boundary while
  keeping raw request, response, session, and dependency objects framework-owned.
- Define protocols for request context, page/fragment selection, safe response headers, URL
  reversal, static/build assets, authenticated-state signals, lifespan resources, and diagnostics.
- Publish a capability matrix that separates the portable baseline from ASGI-only, WSGI-only, and
  framework-specific behavior. Identical rendering and HTTP semantics are required where portable;
  cancellation, dependency injection, validation, lifespan, and background work are capability
  claims rather than fictional parity.
- Restructure Explorer services and adapter bridges to consume sanitized core registry/trace
  contracts without creating circular dependencies.

#### 0.7B — FastAPI production operations

- Container, multi-worker, reverse-proxy/root-path, external static-host, and offline deployment
  proof with deterministic configuration and graceful shutdown.
- Structured async diagnostics, deadlines, cancellation checkpoints, bounded concurrency,
  single-flight backend contracts, and lifecycle-ordered plugin resources.
- A precisely specified `hedron.gather()` and `hedron.run_sync()` contract covering sibling failure,
  partial results, `ContextVar` propagation, thread capacity, cancellation, and CPU-heavy rejection.
- External cache conformance plus logging, traces, health/readiness, cache/job failure reporting,
  component-package audit, and supply-chain operating guidance.

#### 0.7C — Flask adapter

- A separately installable `hedron-flask` distribution using native Flask routing, request context,
  security hooks, CSRF/session integrations, error handling, lifecycle, and `url_for` behavior.
- A native Flask reference slice and shared conformance suite; WSGI limitations are reported in the
  capability matrix rather than hidden behind FastAPI-shaped APIs.

#### 0.7D — Django adapter

- A separately installable `hedron-django` distribution using native URL configuration, middleware,
  CSRF, sessions, forms/validation, async capability, lifecycle, and `reverse` behavior.
- A native Django reference slice, Django QuerySet data-source decision, and shared conformance suite.

#### 0.7E — Jobs and cross-adapter behavior

- FastAPI `BackgroundTasks` helpers remain limited to small post-response work; a pluggable durable
  `JobBackend` contract defines submission, idempotency, authorization/tenant scope, status states,
  retry/failure semantics, retention, cancellation requests, and cleanup.
- A 202 interaction renders an accessible bounded-polling status component, uses `Retry-After`, and
  provides useful non-HTMX behavior without requiring a live transport.
- Cross-adapter HTMX 2 conformance covers supported headers, DELETE query parameters,
  boost/history, 204 and validation/error responses, 3xx header behavior, proxies, and deployment
  prefixes through each framework's request-aware reverse router.

#### 0.7F — Optional transport decision

- Define an independently versioned HTMX extension asset contract with exact versions/digests,
  local serving, CSP declarations, load order, compatibility tests, and Explorer inventory.
- Time-box evaluation of the official SSE extension against bounded polling. SSE adoption is not a
  phase exit requirement; if evidence is insufficient it remains post-1.0.
- WebSocket components remain post-1.0 unless a new accepted RFC demonstrates a genuinely
  bidirectional requirement.

### Exit gate

- Every advertised adapter has an explicit `supported`, `experimental`, or `deferred` stability
  label. Supported adapters pass their declared compatibility, packaging, security, and conformance
  matrices; unfinished adapters do not count toward the phase gate.
- Portable semantics pass once through a shared suite, and every framework capability claim has a
  native test. ASGI/WSGI differences are documented rather than normalized into misleading parity.
- The FastAPI reference application deploys behind a prefixed reverse proxy with multiple workers,
  an external cache and job conformance implementation, and externally hosted static assets.
- Native Flask and Django reference slices prove routing, CSRF/session behavior, validation,
  reverse URLs, assets, and error responses without importing FastAPI.
- Any selected HTMX extension passes offline asset, CSP, authentication, reconnect/cancellation,
  lifecycle, and cross-adapter conformance; removed HTMX 1 attributes remain rejected.
- Adapter, operations, jobs, and observability acceptance ledgers link every completed requirement
  to a test command and evidence artifact; checkbox state alone is insufficient.

## 0.8 — Release candidate and hardening (`v0.8.0`)

**Outcome:** Hedron’s `v1.0.0` public surface is frozen at a hardening baseline and supported by
release-quality evidence. Phase 0.8 adds no new product subsystem, framework adapter, or transport.

### Scope

- Public API, HDN, registry metadata, plugin protocol, compiled artifact, and rendered-markup stability classifications.
- Enforce the compatibility matrix, semantic-versioning rules, numeric deprecation window, upgrade
  tooling, changelog, and migration guides established before the freeze.
- Complete security threat-model review, dependency and browser-asset audit, accessibility audit, and performance budgets.
- Packaging tests for wheels and source distributions across supported platforms and Python versions.
- Documentation usability testing, error-message review, example verification, and no-Node/offline test path.
- Chromium, Firefox, and WebKit HTMX conformance for history, focus, OOB, races, extension teardown,
  CSP, and reduced motion; pinned core/extension asset and license audit.
- Release tests prove that intermediary and application caches cannot confuse pages, fragments, or
  target-specific variants; the complete interaction-status matrix preserves authorization,
  accessibility, retry semantics, and useful non-HTMX fallbacks.
- Produce an SBOM, dependency and browser-asset vulnerability report, license inventory, build
  provenance/attestation, rollback rehearsal, and immutable acceptance evidence bundle.
- Release-candidate stabilization: only fixes, documentation, compatibility work, and explicitly approved scope changes.

`v0.8.0` is the public API-freeze baseline, not a substitute for testing the final version number.
After the 0.8 maintenance line is green, publish one or more PEP 440 prereleases
(`1.0.0rc1`, `1.0.0rc2`, ...) for clean-install, upgrade, deployment, and rollback rehearsals. No
stable `1.0.0` artifact is published without a successful `1.0.0rcN` rehearsal.

### Exit gate

- All `v1.0.0` acceptance documents pass using published `1.0.0rcN` artifacts.
- No unresolved critical/high security issue, release-blocking accessibility defect, undocumented breaking change, or unowned compatibility failure remains.
- The full reference application is deployed and tested from a clean installation.
- No net-new feature or newly advertised adapter enters after the 0.8 freeze.

## 1.0 — Stable Hedron (`v1.0.0`)

**Outcome:** Hedron is a stable, documented, secure, and supportable framework for typed FastAPI component applications.

### Release commitments

- Stable documented public APIs governed by semantic versioning and the compatibility policy.
- FastAPI flagship experience, framework-neutral core, and accurately stated Flask/Django support.
- Secure components, addressable resources, HTMX interaction, HDN, scoped styles, themes, Explorer, data tools, charts, plugins, and production tooling at their documented stability levels.
- Published reference application, tutorials, API reference, architecture/RFC history, deployment guides, and migration support.
- Reproducible release artifacts, provenance, vulnerability response process, and maintained acceptance baselines.
- Published support, maintenance/backport, deprecation, and security-response policies with named
  ownership and supported adapter/server/browser matrices.

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
| Tokens, themes, light/dark token modes, override layers | 0.3 | Accessible CSS-custom-property architecture; system preference + `data-theme`. |
| Light/dark styling toggle, ColorMode API, preference persistence | 0.5 | First-party UI and explicit override of system preference. |
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
| Light/dark styling controls and ColorMode preference persistence | 0.5 | Builds on 0.3 theme token modes; includes accessible toggle UI. |
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
| Portable framework-adapter context, interaction, URL, asset, lifecycle, and diagnostic protocols | 0.7A | Owned by `hedron-core`; raw framework objects stay in adapters. |
| Framework capability matrix | 0.7A | Portable guarantees are separated from ASGI, WSGI, and native-framework capabilities. |
| Flask and Django distributions and re-exported component API | 0.7C–0.7D | Do not install FastAPI; stability is explicit. |
| `hedron-flask` and `hedron-django` release artifacts | 0.7C–0.7D | Published and tested independently of the flagship package when their gates pass. |
| Native framework auth, CSRF, sessions, forms, lifecycle, URL reversing | 0.7 | Host framework remains authoritative. |
| Cross-adapter rendering/HTMX/security/testing conformance | 0.7 | Verifies the framework-neutral core boundary. |
| Typed FastAPI/HTMX request, result, policy, OOB/event/history contract | 0.6 | One explicit interaction envelope; HTML and HTTP mechanics stay visible. |
| Declared fragment regions, boosted metadata, semantic validation/status responses | 0.6 | Target allowlists, full-page fallbacks, and accessible errors. |
| Page/fragment/target cache variation and synchronized form/search policy | 0.6 | Prevents cache confusion and request races. |
| Request-aware URL reversal, capability-aware cancellation, and 202 job interactions | 0.7A–0.7E | Correct under mounts/proxies and explicit ASGI/WSGI capability boundaries. |
| HTMX 2 rich-browser lifecycle, head/assets, errors, morphing, transitions | 0.6 | Core behavior first; optional extensions require conformance evidence. |
| HTMX 2 extension asset contract and transport decision | 0.7F | Independent pins, local serving, CSP; polling is sufficient and SSE may remain deferred. |
| HTMX 2 real-browser, privacy, and supply-chain hardening | 0.8 | Release evidence across Chromium, Firefox, and WebKit. |
| Structured gather, blocking bridge, lifecycle-ordered async resources | 0.7 | No separate async runtime or detached request tasks. |
| External cache contracts and durable job-backend protocol | 0.7 | BackgroundTasks remains for small post-response work. |
| Container, multi-worker, proxy/root-path, static host, offline deployment | 0.7 | Includes graceful shutdown and health/readiness. |
| Logging, traces, timing, cache/job failures, component supply-chain audit | 0.7 | Secrets are redacted before storage or display. |
| Security development/standard/strict profiles | 0.2, 0.8 | Baseline enforcement at 0.2; final audit at 0.8. |
| Accessibility contracts and WCAG-oriented acceptance | 0.1–0.8 | Required incrementally for every built-in and integration. |
| Performance benchmarks, payload limits, and budgets | 0.1–0.8 | 0.7 establishes production workloads/budgets; 0.8 enforces them. |
| Public API/artifact stability classification and freeze | 0.8 | Includes HDN, plugin, manifest, metadata, and markup promises. |
| Semantic versioning, deprecation, upgrade, migration, compatibility | 0.7–0.8 | Defined before the freeze and enforced through RC rehearsal. |
| Published reference application and release artifacts | 0.1–1.0 | Grows cumulatively and validates clean installation. |

## RFC-to-phase coverage

| RFC | Primary phase assignment |
|---|---|
| 0001 Vision | 0.0 |
| 0002 Core architecture | 0.0–0.2; adapter proof in 0.7 |
| 0003 Component model | 0.1 |
| 0004 FastAPI integration | 0.2 baseline; typed HTMX interaction contract in 0.6 |
| 0005 HDN language | 0.3 |
| 0006 Scoped styles | 0.3 |
| 0007 Component Explorer | 0.2 minimal; 0.4 full; extended through 0.7 |
| 0008 Addressable components | 0.2 |
| 0009 HTMX integration | 0.2 baseline; interaction/lifecycle hardening in 0.6–0.8 |
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

- **Live transport beyond the 0.7 decision:** stable SSE live regions, WebSocket components,
  focused chunked lists, and general streamed documents, using separately versioned HTMX 2
  extensions rather than removed `hx-sse` / `hx-ws` attributes.
- **Navigation preloading:** measured opt-in preload for safe GET navigation, including cache
  correctness, bounded speculative traffic, privacy, and `HX-Preloaded` observability. Preload is
  not introduced during the 0.8 feature freeze.
- **Advanced async:** component-level async `prepare()` lifecycle, adaptive concurrency, and distributed tracing integrations.
- **HDN tooling:** language server, editor extensions, advanced static analysis, and guided React-to-HDN conversion.
- **Styles and assets:** route-level CSS splitting beyond the 0.6 fragment/head contract, fully
  dynamic HTMX asset negotiation, cross-file composition, optional preprocessors, advanced
  minification, hot style replacement, and a full design-token compiler.
- **DataEditor:** formulas, merged cells, Excel-formatting parity, pivot tables, tree grids, collaborative editing, additional enterprise grid adapters, and spreadsheet import/export beyond CSV.
- **Data scale:** Dask/distributed sources, automatic server transform planning, and more advanced lazy-query pushdown.
- **Visualization:** ECharts, Datashader, MapLibre, Folium, Bokeh, HoloViews/hvPlot, Pygal, geospatial layers, Plotly resampling, and advanced Vega server transforms.
- **Developer tooling:** AI-assisted Explorer diagnostics, visual authoring, broader migration tooling, generated component endpoint SDKs, and optional OpenAPI callback/webhook presentation tools.
- **Portability and performance:** language-neutral component specification, Java and Node runtimes, conformance code generation, and optional Rust acceleration after profiling.
