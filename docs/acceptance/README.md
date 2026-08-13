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
- [Web Component platform](WEB_COMPONENT_PLATFORM.md) — draft 0.36–0.41 program
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
- [`v0.33` unified Posit deployment adapter](RELEASE_0_33.md) — **Planned** (packet refine
  complete; RFC-0066 **Accepted**; D-061; [#167](https://github.com/eddiethedean/hedron/issues/167);
  Stage 1 package extraction unblocked; Supported bridge dropped per Stage 0)
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
  [release-gate-0.33.toml](release-gate-0.33.toml) (Planned)

Unchecked boxes are requirements, not optional suggestions, unless marked Deferred with an owning
RFC, destination phase, owner, and public stability impact.
