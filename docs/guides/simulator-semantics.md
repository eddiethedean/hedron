# Simulator semantics (0.54)

`hedron-sim` is a **tooling-grade** offline HTMX docs/demo simulator. It is not a
browser automation engine and does not silently approximate unsupported features.

## Declared subset

Call `subset_manifest()` / `divergence_manifest()` for the machine-readable
contract (methods, attrs, swaps, history, forms, extensions, errors, timing).
Unsupported authoring raises `UnsupportedSimFeatureError` with code
`HED-SIM-UNSUPPORTED`.

## Recording and time control

`SimRecorder` / `SimScenario` / `SimClock` capture requests, swaps, triggers,
delays, and failures. Import/export is deterministic. Byte/step/depth/time limits
raise with `HED-SIM-LIMIT`.

## Parity

`compare_parity(sim_html, server_html)` differential-tests against real Hedron
HTTP (and browser suites where enabled). Differences are reported; equality after
normalization is required for `PARITY-054` fixtures.
