# Performance acceptance

## Baselines

- [ ] Benchmarks separately measure startup, dependency/I/O preparation, tree construction, serialization, page response, fragment response, HDN compilation, CSS compilation, and asset build.
- [ ] DataEditor and chart tests record rows, bytes, transforms, and browser initialization cost.
- [x] Explorer measures its own overhead and can be absent in production. *(phase 0.4 — audit/rate-limit hooks; default `explorer="off"`)*

## Budgets

- [ ] Phase 0.7 establishes reproducible page, fragment, adapter, reverse-proxy, cache, job-polling,
  and shutdown workloads plus latency/resource budgets before the 0.8 freeze.
- [ ] Output, CSS, JavaScript, chart, job-status, logging, and diagnostic payload budgets are documented.
- [ ] Lazy/distributed data cannot be collected implicitly.
- [x] Production performs no required runtime HDN/CSS compilation. *(phase 0.3 — `HED-BUILD-0004` + production lifespan deny; build uses force-allow)*
- [ ] Cache single-flight and bounded concurrency prevent stampedes and resource exhaustion.

## Native decision gate

- [ ] Any Rust proposal names a measured bottleneck, target improvement, benchmark corpus, parity suite, wheel plan, and fallback behavior.

## Exit

The reference application meets published budgets under a reproducible workload, and regressions
can be attributed to a pipeline stage. Phase 0.8 enforces budgets; it does not invent them during
release stabilization.
