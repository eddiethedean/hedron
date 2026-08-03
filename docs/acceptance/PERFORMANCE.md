# Performance acceptance

## Baselines

- [ ] Benchmarks separately measure startup, dependency/I/O preparation, tree construction, serialization, page response, fragment response, HDN compilation, CSS compilation, and asset build.
- [ ] DataEditor and chart tests record rows, bytes, transforms, and browser initialization cost.
- [ ] Explorer measures its own overhead and can be absent in production.

## Budgets

- [ ] Representative page and fragment latency budgets are set before release candidates.
- [ ] Output, CSS, JavaScript, and chart payload budgets are documented.
- [ ] Lazy/distributed data cannot be collected implicitly.
- [x] Production performs no required runtime HDN/CSS compilation. *(phase 0.3 — `HED-BUILD-0004` + production lifespan deny; build uses force-allow)*
- [ ] Cache single-flight and bounded concurrency prevent stampedes and resource exhaustion.

## Native decision gate

- [ ] Any Rust proposal names a measured bottleneck, target improvement, benchmark corpus, parity suite, wheel plan, and fallback behavior.

## Exit

The reference application meets published budgets under a reproducible workload, and regressions can be attributed to a pipeline stage.

