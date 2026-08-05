# Performance acceptance

## Baselines

- [ ] Benchmarks separately measure startup, dependency/I/O preparation, tree construction, serialization, page response, fragment response, Jinja checking/rendering, CSS compilation, and asset build.
- [ ] DataEditor and chart tests record rows, bytes, transforms, and browser initialization cost.
- [x] Explorer measures its own overhead and can be absent in production. *(phase 0.4 — audit/rate-limit hooks; default `explorer="off"`)*

## Budgets

- [x] Phase 0.7/0.8 publishes reproducible page, fragment, and render-stage workloads plus latency
  budgets before/at the freeze.
  *(`PERF-08-001` / [PERFORMANCE_BUDGETS.md](../PERFORMANCE_BUDGETS.md))*
- [x] Output and diagnostic payload budgets are documented and enforced.
  *(`PERF-08-002` / `tests/performance/test_budgets.py`)*
- [ ] Lazy/distributed data cannot be collected implicitly.
- [x] Production performs no required runtime CSS compilation. *(phase 0.3 — `HED-BUILD-0004` + production lifespan deny; build uses force-allow)*
- [ ] Cache single-flight and bounded concurrency prevent stampedes and resource exhaustion.

## Native decision gate

- [x] Any Rust proposal names a measured bottleneck, target improvement, benchmark corpus, parity suite, wheel plan, and fallback behavior.
  *(phase 0.14 — RFC-0020 / D-048 / `ACCEL-RUST-014`: bulk HTML escaping via optional `hedron-native`)*

## Exit

The reference application meets published budgets under a reproducible workload, and regressions
can be attributed to a pipeline stage. Phase 0.8 enforces budgets; it does not invent them during
release stabilization.
