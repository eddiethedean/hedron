# RFC-0020: Performance

**Status:** Accepted

## Approach

Hedron establishes budgets and representative benchmarks before optimization. Development diagnostics prioritize clarity; production builds prioritize deterministic cached compilation and external fingerprinted assets.

Measure endpoint dependency time, I/O preparation, component rendering, serialization, response size, asset size, cache behavior, chart payloads, and DataEditor row transfer separately. Explorer traces must distinguish concurrent wall time from estimated sequential time.

## Guardrails

- Avoid FFI calls per node if native acceleration is ever introduced.
- Avoid implicit collection of lazy or distributed dataframes.
- Bound browser rows, JSON payloads, concurrency, upload sizes, and remote calls.
- Compile scoped CSS and fingerprint assets ahead of time; statically check optional Jinja templates.
- Prefer lazy addressable regions to streaming entire documents.

## Native threshold

Rust work requires a repeatable benchmark, a documented target improvement, representative production profiles, pure-Python semantic parity, wheel feasibility, and a fallback path.

## Phase 0.14 native decision gate (D-048)

| Field | `hedron-native` 0.14 proposal |
|---|---|
| Bottleneck | Bulk HTML text/attribute escaping during serialization (`escape_text` / `escape_attr`) |
| Target improvement | ≥20% lower serialize-stage wall time on the published large-tree corpus vs pure Python |
| Benchmark corpus | `tests/performance/test_native_accel_bench.py` (reference-app-scale element trees) |
| Parity suite | Conformance escaping fixtures + `tests/unit/test_native_parity.py` |
| Wheel plan | maturin/PyO3 optional wheel; source-build path; never a hard dependency of `hedron-core` |
| Fallback | Automatic pure-Python path when the extension is absent or unloadable; semantics unchanged |

FFI remains batch-oriented (escape helpers), never per-node tree walking in native code.

## Acceptance criteria

- CI records baseline benchmarks without relying solely on brittle hard failures.
- Release gates define page render, fragment render, startup, and bundle-size budgets.
- Regressions can be attributed to a documented stage rather than a single aggregate timer.
