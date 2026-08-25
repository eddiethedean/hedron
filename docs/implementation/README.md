# Implementation specifications

These documents describe how accepted RFC behavior will be implemented. They define subsystem boundaries, artifacts, failure behavior, and verification without freezing private class names prematurely.

- [Model system](MODEL_SYSTEM.md)
- [Rendering engine](RENDERING_ENGINE.md)
- [HTML serializer](HTML_SERIALIZER.md)
- [CSS compiler](CSS_COMPILER.md)
- [Component registry](COMPONENT_REGISTRY.md)
- [Router generator](ROUTER_GENERATOR.md)
- [OpenAPI generator](OPENAPI_GENERATOR.md)
- [Explorer backend](EXPLORER_BACKEND.md)
- [Explorer frontend](EXPLORER_FRONTEND.md)
- [Asset pipeline](ASSET_PIPELINE.md)
- [Default presentation quality](DEFAULT_PRESENTATION_033_PLUS.md) — cross-cutting 0.33–0.42 plan
  for polished out-of-box styles, shell composition, responsive containment, and visual evidence
- [`hedron-posit` phase 0.33](HEDRON_POSIT_033.md) — staged licensed Connect probe, package
  extraction, native mode, bounded authenticated bridge, compatibility, and release closure
- [`hedron-gradio` phase 0.34](HEDRON_GRADIO_034.md) — production-grade remote client interop,
  allowlisted egress, bounded files/streams, and HF vendor evidence
- [High-fidelity charts](HEDRON_CHARTS_038.md) — phase 0.38 D3-class typed chart platform
- [Chart grammar catalogs](CHART_SPEC.md) — `ChartSpec` / `ChartPlan` fields, operators, events,
  diagnostics, tokens, fallback (0.38 planning)
- [Web Component platform](WEB_COMPONENT_PLATFORM.md) — 0.36–0.42 program
- [Web Component interaction contracts](WEB_COMPONENT_INTERACTION_CONTRACTS.md) — state,
  async interaction, optimism, gestures/overlays, and React migration
- [Browser composition, draft transfer, and navigation](HEDRON_COMPOSITION_041.md) — phase 0.41
  D-069 architecture, work slices, failure boundaries, and evidence plan
- [Production-grade Web Component platform](HEDRON_ELEMENTS_042.md) — phase 0.42 D-070 Stage 0
  graduation plan, Supported inventory, AT-042 honesty, and fleet remediation bind
- [Refreshable views and command handles](INTERACTION_HANDLES_043.md) — phase 0.43 D-071 / D-073
  requirements, architecture, work slices, traceability, compatibility, and evidence plan
- [Type-driven authoring](TYPE_DRIVEN_AUTHORING_044.md) — phase 0.44 D-072 / D-073 / D-076 Pydantic
  boundaries, annotation markers, generics, generated forms, effects/outcomes, optional class
  lifecycles, and shared schema requirements
- [Typed interaction ecosystem](TYPED_INTERACTION_ECOSYSTEM_045.md) — phase 0.45 D-074 / D-077 catalog,
  manifest, package projections/dispositions, hosts, tooling, remote, portable, and deployment
  convergence requirements
- [Package-native typed workflows](PACKAGE_NATIVE_WORKFLOWS_046.md) — phase 0.46 D-075 / D-079 feature
  bundles, data workspaces, linked charts, enhanced elements, remote workflows, workbenches, and
  scenario requirements
- [First-class maps](HEDRON_MAPS_047.md) — phase 0.47 D-078 / D-082 `hedron-maps`, MapLibre, custom
  raster/vector sources, typed interaction, offline assets/archives, and air-gapped requirements
- [HTMX extension integration](HTMX_EXTENSION_INTEGRATION_048.md) — phase 0.48 D-080 / D-083
  declared activation, demand-driven assets, SSE/head-support/preload slices, and morph disposition
- [FastAPI/Pydantic convergence](FASTAPI_PYDANTIC_CONVERGENCE_049.md) — phase 0.49 D-081 / D-084
- [Explorer architecture](EXPLORER_050.md) — phase 0.50 **Published** `v0.50.1` on PyPI; in-tree `v0.50.3` (D-085 / D-086; 0.50.3 tag deferred)
- [Curated extras depth](EXTRAS_051.md) — phase 0.51 **Verified** in-tree / **Published** on PyPI as `v0.51.0` (D-087 / D-088; RFC-0078; [#507](https://github.com/eddiethedean/hedron/issues/507))
- [Conformance authority](CONFORMANCE_052.md) / [Posit lifecycle](POSIT_LIFECYCLE_052.md) — phase 0.52 **Verified** in-tree `v0.52.0` (D-089 / D-090; RFC-0079; [#522](https://github.com/eddiethedean/hedron/issues/522); PyPI `v0.51.0` until upload)
- [Progressive feature and styling authoring](PROGRESSIVE_AUTHORING_058.md) — phase 0.58
  D-101 / D-102 / D-105 W0–W17 workstreams for screens, forms, workspaces, task/dashboard/session/
  upload flows, `DesignSystem`, brand compilation, recipes/feature roles, scopes, unified
  explanation/preview/diff/ejection, all starter migrations, and twenty-gate release evidence
  (Stage 0 Refined)
- [Modern CSS platform and intuitive built-in styling](MODERN_CSS_059.md) — phase 0.59 D-106 / D-107
  refined workstreams for the scoped compiler, cascade/tokens, modern color/type, container layout,
  media/overlay/motion, control/AppShell/pipeline consumer slices, tooling, fleet adoption, and
  23-gate release evidence (Stage 1 blocked on probes and issue mirrors)
- [Phase 0.59 execution plan](EXECUTION_0_59.md) — ordered E0–E9 implementation milestones,
  dependencies, evidence, stop conditions, and release handoff
- [Custom theme platform and styling completion](THEME_PLATFORM_060.md) — proposed phase 0.60
  W0–W12 workstreams for typed modern color, ThemeSpec/ThemePatch, registry-derived validation
  profiles, packages/conformance, accessibility modes, recipes/scopes, preference selection,
  built-in themes, and #627–#635 closure
- [Phase 0.60 execution plan](EXECUTION_0_60.md) — ordered E0–E10 milestones, dependency rules,
  pull-request sequence, stop conditions, and release handoff
- [Reactive interaction platform](REACTIVE_INTERACTION_PLATFORM_061_063.md) — proposed phases
  0.61–0.63 program invariants, ownership, stage sequence, reference journeys, and stop conditions
- [Phase 0.61 action state and async boundaries](ACTION_STATE_ASYNC_061.md) — W0–W11 contract,
  lifecycle/race, boundary lowering, host/element, trace, budget, compatibility, and release plan
- [Phase 0.62 navigation, optimism, and failure isolation](NAVIGATION_OPTIMISM_062.md) — W0–W12
  navigation, prefetch/transition, optimistic risk, failure, identity, dashboard, and browser plan
- [Phase 0.63 theme contract, interaction tooling, and interoperability](INTERACTION_TOOLING_063.md) — W0–W15
  theme resolution/evidence, trace/profiler, static checks, metadata ABI, migration dispositions,
  conformance, and interop plan
- [Phase 0.63 execution plan](EXECUTION_0_63.md) — E0–E15 implementation order, issue work packages,
  dependencies, verification sequence, stop conditions, and release handoff
- [Phase 0.64 Hedron HTMX interaction extension](HTMX_HEDRON_EXTENSION_064.md) — W0–W10
  pinned extension asset, lifecycle state, accessibility, concurrency presentation, CSP-safe
  cleanup, browser traces, Hedron integration, and release plan
- [Integrated styling platform and application CSS](APPLICATION_STYLING_065.md) — proposed phase
  0.65 W0–W11 workstreams for first-class local stylesheet assets, public hooks, namespaced tokens,
  an explicit application layer, diagnostics, provenance-preserving ejection, the four open styling
  issues, and the touched-surface fallback matrix; see the [refined scope](../acceptance/application-styling-scope-065.md)
- [Phase 0.65 execution plan](EXECUTION_0_65.md) — repository seam map, W0–W15 implementation
  packages, test/evidence inventory, pull-request sequence, rollout, rollback, and release handoff
- [Phase 0.66 HDJ parity](HDJ_PARITY_066.md) — app-scoped binding, registry projection, live
  logical-ID helpers, portable HTMX facts, provider/style parity, and claim-honest gates
- [Hedron-native documentation application](HEDRON_NATIVE_DOCUMENTATION.md) — draft unassigned
  workstreams for compiling the Markdown corpus into native Hedron component trees, building the
  docs shell/search/API/live-demo application, proving parity, and cutting over to FastAPI Cloud
- [Plugin loader](PLUGIN_LOADER.md)
- [Async runtime integration](ASYNC_RUNTIME.md)
- [Cache layer](CACHE_LAYER.md)
- [Security controls](SECURITY_CONTROLS.md)
- [Build system](BUILD_SYSTEM.md)
- [Framework adapters](FRAMEWORK_ADAPTERS.md)
- [Production operations](OPERATIONS.md)
- [Job interaction runtime](JOB_RUNTIME.md)
- [Observability](OBSERVABILITY.md)
