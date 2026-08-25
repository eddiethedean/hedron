# Acceptance specifications

Acceptance documents are release gates. A subsystem is not complete when its implementation exists; it is complete when the relevant functional, security, accessibility, performance, compatibility, documentation, and testing checks pass.

For the phase 0.6 closure gate and every later release, completion also follows the
[release evidence policy](EVIDENCE.md): stable requirement IDs, exact commands, supported matrix
dimensions, retained artifacts, and named ownership are required. A checked box without evidence is
status commentary, not a satisfied release gate.

- [Component model](COMPONENT_MODEL.md)
- [FastAPI integration](FASTAPI_INTEGRATION.md)
- [HTMX](HTMX.md)
- [HDJ authoring](JINJA.md)
- [Scoped styles](SCOPED_STYLES.md)
- [Component Explorer](EXPLORER.md)
- [CLI](CLI.md)
- [Plugins](PLUGINS.md)
- [Testing](TESTING.md)
- [DataEditor](DATA_EDITOR.md)
- [Visualization](VISUALIZATION.md)
- [Caching and utility components](CACHING_UTILITIES.md)
- [Security](SECURITY.md)
- [Async](ASYNC.md)
- [Framework adapters](ADAPTERS.md)
- [Production operations](OPERATIONS.md)
- [Jobs and asynchronous work](JOBS.md)
- [Observability](OBSERVABILITY.md)
- [Accessibility](ACCESSIBILITY.md)
- [Web Component platform](WEB_COMPONENT_PLATFORM.md) — 0.36–0.42 program; **Published** through 0.42 (D-070)
- [`v0.36` Web Component ABI](RELEASE_0_36.md) — **Published**; all owned gates Verified; tip `v0.36.0`
- [`v0.37` form-associated elements and primitives](RELEASE_0_37.md) — **Published** (`v0.37.0`)
- [`v0.38` high-fidelity charts](RELEASE_0_38.md) — **Published** (`v0.38.0` / `hedron-charts` `0.2.0`); RFC-0069 / D-066; [#251](https://github.com/eddiethedean/hedron/issues/251)
- [`v0.39` rich data and OptimisticMutation](RELEASE_0_39.md) — **Published** (`v0.39.0`); RFC-0060 / D-067; [#94](https://github.com/eddiethedean/hedron/issues/94) closed
- [`v0.40` authoring and React migration](RELEASE_0_40.md) — **Published** (`v0.40.0`; D-068; [#95](https://github.com/eddiethedean/hedron/issues/95) closed)
- [`v0.41` browser composition, state, and navigation](RELEASE_0_41.md) — **Published** (`v0.41.0`; D-069; [#96](https://github.com/eddiethedean/hedron/issues/96))
- [`v0.42` production-grade Web Component platform](RELEASE_0_42.md) — **Published** (`v0.42.0`; D-070; [#97](https://github.com/eddiethedean/hedron/issues/97))
- [`v0.43` refreshable views, commands, and typed updates](RELEASE_0_43.md) — **Published** (`v0.43.0`; D-071 / RFC-0070, refined by D-073; [#311](https://github.com/eddiethedean/hedron/issues/311))
- [`v0.44` type-driven authoring](RELEASE_0_44.md) — **Published** in-tree as `v0.44.0`
  (tag/PyPI deferred; D-072 / RFC-0071, refined by D-073 / D-076; [#318](https://github.com/eddiethedean/hedron/issues/318))
- [`v0.45` typed interaction ecosystem](RELEASE_0_45.md) — **Published** in-tree as `v0.45.0`
  (tag/PyPI deferred; D-074 / RFC-0072, refined by D-077;
  [#328](https://github.com/eddiethedean/hedron/issues/328))
- [`v0.46` package-native typed workflows](RELEASE_0_46.md) — **Published** as `v0.46.0`
  (D-075 / RFC-0073, refined by D-079;
  [#334](https://github.com/eddiethedean/hedron/issues/334))
- [`v0.47` first-class maps](RELEASE_0_47.md) — **Published** as in-tree `v0.47.0`
  (tag/PyPI deferred; D-078 / RFC-0074, refined by D-082; `hedron-maps` `0.1.0`;
  [#350](https://github.com/eddiethedean/hedron/issues/350))
- [`v0.48` HTMX extension integration](RELEASE_0_48.md) — **Published** as in-tree `v0.48.0`
  (tag/PyPI deferred; D-080 / RFC-0075, refined by D-083;
  [#373](https://github.com/eddiethedean/hedron/issues/373); `MORPH-048` Deferred)
- [`v0.49` FastAPI/Pydantic convergence](RELEASE_0_49.md) — **Published** as `v0.49.1`
  (D-081 / RFC-0076, refined by D-084;
  [#380](https://github.com/eddiethedean/hedron/issues/380); SETTINGS retain-custom-loader;
  RESEARCH Experimental)
- [`v0.50` Explorer architecture](RELEASE_0_50.md) — **Published** as `v0.50.1` on PyPI;
  in-tree `v0.50.3` (0.50.3 tag deferred; D-085 / RFC-0077, refined by D-086;
  [#501](https://github.com/eddiethedean/hedron/issues/501) stays open until publish assets;
  related [#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500) /
  [#502](https://github.com/eddiethedean/hedron/issues/502) /
  [#503](https://github.com/eddiethedean/hedron/issues/503) closed)
- [`v0.51` curated extras](RELEASE_0_51.md) — **Verified** (D-087 / RFC-0078, refined by D-088;
  [#507](https://github.com/eddiethedean/hedron/issues/507); related
  [#504](https://github.com/eddiethedean/hedron/issues/504)–[#506](https://github.com/eddiethedean/hedron/issues/506);
  published `v0.51.0`)
- [`v0.58` progressive feature and styling authoring](RELEASE_0_58.md) — **Published/Verified**
  as `v0.58.0` on PyPI (D-101 / D-102 / D-105 / RFC-0085; twenty Verified
  gates; predecessor `v0.57.0` Published/Verified in-tree)
- [`v0.59` modern CSS platform and intuitive built-in styling](RELEASE_0_59.md) — **Published**
  as `v0.59.0` on PyPI (D-106 / D-107 / RFC-0087)
- [`v0.60` custom theme platform and styling completion](RELEASE_0_60.md) — **Implemented, verified,
  tagged, and published** as `v0.60.0` (D-108 / RFC-0089; 27 gates Verified; owns Hedron #627–#635)
- [Reactive interaction shared acceptance rules](REACTIVE_INTERACTION_PHASES_061_063.md) — Proposed
  maturity, artifact, evidence, fallback, and cross-phase rules; no availability claim
- [`v0.61` action state and async boundaries](RELEASE_0_61.md) — **Verified** release packet with
  18 Verified contract, lifecycle, race, host, trace, security, a11y, budget, upgrade, and package gates
- [`v0.62` navigation, optimism, and failure isolation](RELEASE_0_62.md) — Proposed release plan with
  17 Planned navigation, fallback, risk, conflict, identity, browser, budget, and package gates
- [`v0.63` theme contract, interaction tooling, and interoperability](RELEASE_0_63.md) — Proposed
  release plan with 27 Planned theme, trace, profiler, static-check, metadata, migration,
  conformance, and package gates
- [`v0.64` Hedron HTMX interaction extension](RELEASE_0_64.md) — Proposed release plan with
  14 Planned contract, asset, lifecycle, accessibility, race, trace, browser, integration, and package gates
- [`v0.65` integrated styling platform and application CSS](RELEASE_0_65.md) — Verified release candidate
  packet with public-hook, asset, layer, token, diagnostics, ejection, bounded open-issue slices,
  touched-surface fallback, performance, upgrade, fleet, documentation, and package gates; see
  the [refined scope](application-styling-scope-065.md)
- [`v0.66` HDJ parity, registry integration, and open-issue closure](RELEASE_0_66.md) — **In
  progress**: the app-scoped HDJ foundation is Verified; thirteen issue gates remain Planned in the
  [open-issue inventory](open-issues-066.toml); see [release-gate-0.66.toml](release-gate-0.66.toml)
- [Human AT (0.21)](human-at/README.md) — protocol / ledger (D-052; engineering-complete /
  sessions outstanding)
- [Packaging and deployment](PACKAGING_DEPLOYMENT.md)
- [Performance](PERFORMANCE.md)
- [`v0.9.0` HDJ replacement](RELEASE_0_9.md) — published; clean HDN removal, explicit `.hdj` format, standards-first authoring
- [`v0.10` live interaction](RELEASE_0_10.md) — published; SSE, focused streaming, WebSocket channels, Chat/Dialog, preload (owned Deferred follow-ups noted)
- [`v0.11` native Flask/Django depth](RELEASE_0_11.md) — published; Blueprint/`init_app`, Django forms/QuerySet, portable harness, HDJ inventory/CSP (owned Deferred follow-ups noted)
- [`v0.12` data and visualization scale](RELEASE_0_12.md) — published
- [`v0.13` advanced async and observability](RELEASE_0_13.md) — published; zero-Deferred for 0.13-owned rows
- [`v0.14` portable runtimes and acceleration](RELEASE_0_14.md) — conformance kit, Java/Node runtimes, Rust accel, HDJ instrumentation
- [`v0.15` data-app surface](RELEASE_0_15.md) — published
- [`v0.16` curated extras](RELEASE_0_16.md) — published
- [`v0.17` reactive dashboards](RELEASE_0_17.md) — published
- [`v0.18` model demos and inference](RELEASE_0_18.md) — published; zero-Deferred for 0.18-owned rows
- [`v0.19` accessibility engineering](RELEASE_0_19.md) — **Published**; contracts, ATAG, Explorer, automated AT matrix, PE/landmarks/scripts
- [`v0.20` production security floor and adapter parity](RELEASE_0_20.md) — **Published** (D-051); CSRF composition split to 0.22
- [`v0.21` human AT](RELEASE_0_21.md) — engineering-complete / sessions outstanding (D-052)
- [`v0.22` CSRF and SecurityPolicy composition](RELEASE_0_22.md) — **Published** (D-051)
- [`v0.23` stable-tier expansion](RELEASE_0_23.md) — **Published** (D-053 / RFC-0056)
- [`v0.24` live-transport disposition](RELEASE_0_24.md) — **Published** (`v0.24.0`; `polling_only`) (D-053 / RFC-0056)
- [`v0.25` production archetype and landmine quarantine](RELEASE_0_25.md) — **Published** (`v0.25.0`; packet Verified complete) (D-053 / RFC-0056)
- [`v0.32` production-grade MCP projection](RELEASE_0_32.md) — **Published** (`v0.32.0`; `hedron-mcp` `0.2.0` Beta; D-060 / RFC-0065; [#89](https://github.com/eddiethedean/hedron/issues/89))
- [`v0.33` unified Posit deployment adapter](RELEASE_0_33.md) — **Published** (`v0.33.0`; `hedron-posit` `0.33.0` Beta; D-061 / RFC-0066; [#167](https://github.com/eddiethedean/hedron/issues/167); Supported bridge dropped per Stage 0)
- [Release evidence policy](EVIDENCE.md)
- Phase indices: [release-gate-0.6.toml](release-gate-0.6.toml),
  [release-gate-0.7.toml](release-gate-0.7.toml),
  [release-gate-0.8.toml](release-gate-0.8.toml),
  [release-gate-0.9.toml](release-gate-0.9.toml),
  [release-gate-0.10.toml](release-gate-0.10.toml),
  [release-gate-0.11.toml](release-gate-0.11.toml),
  [release-gate-0.12.toml](release-gate-0.12.toml),
  [release-gate-0.13.toml](release-gate-0.13.toml),
  [release-gate-0.14.toml](release-gate-0.14.toml),
  [release-gate-0.15.toml](release-gate-0.15.toml),
  [release-gate-0.16.toml](release-gate-0.16.toml),
  [release-gate-0.17.toml](release-gate-0.17.toml),
  [release-gate-0.18.toml](release-gate-0.18.toml),
  [release-gate-0.19.toml](release-gate-0.19.toml),
  [release-gate-0.20.toml](release-gate-0.20.toml),
  [release-gate-0.21.toml](release-gate-0.21.toml),
  [release-gate-0.22.toml](release-gate-0.22.toml),
  [release-gate-0.23.toml](release-gate-0.23.toml),
  [release-gate-0.24.toml](release-gate-0.24.toml),
  [release-gate-0.25.toml](release-gate-0.25.toml),
  [release-gate-0.32.toml](release-gate-0.32.toml) (Verified),
  [release-gate-0.33.toml](release-gate-0.33.toml) (Verified),
  [release-gate-0.34.toml](release-gate-0.34.toml) (Verified),
  [release-gate-0.35.toml](release-gate-0.35.toml) (Verified),
  [release-gate-0.36.toml](release-gate-0.36.toml) (Verified),
  [release-gate-0.37.toml](release-gate-0.37.toml) (Verified),
  [release-gate-0.38.toml](release-gate-0.38.toml) (Verified),
  [release-gate-0.39.toml](release-gate-0.39.toml) (Verified),
  [release-gate-0.40.toml](release-gate-0.40.toml) (Verified),
  [release-gate-0.41.toml](release-gate-0.41.toml) (Verified),
  [release-gate-0.42.toml](release-gate-0.42.toml) (Verified),
  [release-gate-0.43.toml](release-gate-0.43.toml) (Verified),
  [release-gate-0.44.toml](release-gate-0.44.toml) (Verified),
  [release-gate-0.45.toml](release-gate-0.45.toml) (Verified),
  [release-gate-0.46.toml](release-gate-0.46.toml) (Verified),
  [release-gate-0.47.toml](release-gate-0.47.toml) (Verified),
  [release-gate-0.48.toml](release-gate-0.48.toml) (Verified except `MORPH-048` Deferred),
  [release-gate-0.49.toml](release-gate-0.49.toml) (Verified; D-084),
  [release-gate-0.50.toml](release-gate-0.50.toml) (Verified; D-086),
  [release-gate-0.51.toml](release-gate-0.51.toml) (Verified; D-088)

Unchecked boxes are requirements, not optional suggestions, unless marked Deferred with an owning
RFC, destination phase, owner, and public stability impact.
