# Acceptance specifications

Acceptance documents are release gates. A subsystem is not complete when its implementation exists; it is complete when the relevant functional, security, accessibility, performance, compatibility, documentation, and testing checks pass.

For the phase 0.6 closure gate and every later release, completion also follows the
[release evidence policy](EVIDENCE.md): stable requirement IDs, exact commands, supported matrix
dimensions, retained artifacts, and named ownership are required. A checked box without evidence is
status commentary, not a satisfied release gate.

- [Component model](COMPONENT_MODEL.md)
- [FastAPI integration](FASTAPI_INTEGRATION.md)
- [HTMX](HTMX.md)
- [HDN](HDN.md)
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
- [Packaging and deployment](PACKAGING_DEPLOYMENT.md)
- [Performance](PERFORMANCE.md)
- [`v1.0.0` release](RELEASE_1_0.md) — rolls up 0.8 freeze evidence + RC rehearsal
- [Release evidence policy](EVIDENCE.md)
- Phase indices: [release-gate-0.6.toml](release-gate-0.6.toml),
  [release-gate-0.7.toml](release-gate-0.7.toml),
  [release-gate-0.8.toml](release-gate-0.8.toml)

Unchecked boxes are requirements, not optional suggestions, unless marked Deferred with an owning
RFC, destination phase, owner, and public stability impact.
