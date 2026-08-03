# RFC-0020: Performance

**Status:** Accepted

## Approach

Hedron establishes budgets and representative benchmarks before optimization. Development diagnostics prioritize clarity; production builds prioritize deterministic cached compilation and external fingerprinted assets.

Measure endpoint dependency time, I/O preparation, component rendering, serialization, response size, asset size, cache behavior, chart payloads, and DataEditor row transfer separately. Explorer traces must distinguish concurrent wall time from estimated sequential time.

## Guardrails

- Avoid FFI calls per node if native acceleration is ever introduced.
- Avoid implicit collection of lazy or distributed dataframes.
- Bound browser rows, JSON payloads, concurrency, upload sizes, and remote calls.
- Compile HDN and CSS ahead of time for production.
- Prefer lazy addressable regions to streaming entire documents.

## Native threshold

Rust work requires a repeatable benchmark, a documented target improvement, representative production profiles, pure-Python semantic parity, wheel feasibility, and a fallback path.

## Acceptance criteria

- CI records baseline benchmarks without relying solely on brittle hard failures.
- Release gates define page render, fragment render, startup, and bundle-size budgets.
- Regressions can be attributed to a documented stage rather than a single aggregate timer.

