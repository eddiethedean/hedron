# Upgrade fixtures plan (0.28 charts / native graduation)

**Baseline:** Published **`v0.27.0`**.
**Owning gates:** `CHARTS-028`, `INTERACTIVE-028`, `NATIVE-028`, `SUPPLY-028`
(fixtures feed those gates; inventory agreement closes under `PKG-028` /
`check_contract_028.py`).
**RFC:** [RFC-0059](../rfcs/RFC-0059-PRODUCTION-GRADE-CHARTS-NATIVE.md).

## Capture set

From the Supported inventories (see
[production-grade-inventory-028.toml](production-grade-inventory-028.toml)):

1. **Static chart contracts** (`charts_static.json`) — Matplotlib SVG/PNG
   identity keys, beginner Line/Bar/Area/Scatter static-path markers, a11y
   alternative presence, and payload-budget fields.
2. **Interactive disposition** (`charts_interactive.json`) — Plotly/Altair and
   every optional adapter name labeled Experimental; assert they are absent from
   production-default renderer registration.
3. **Native escape parity** (`native_escape.json`) — `escape_text` /
   `escape_attr` sample corpus outcomes matching the Python reference under
   native present, absent, and runtime-disable injection.
4. **Supply pins** (`charts_supply.json`) — Supported local-asset pin digests /
   license inventory keys required for offline install evidence.

## Location

- Plan SSOT: this file
- Goldens: `tests/upgrade/goldens_0_27_0/` (created when fixtures are captured)
- Tests: `tests/upgrade/test_0_27_0_to_0_28_charts_native.py` (at evidence pass)

## Pass criteria

Silent drift in golden bytes or structural keys fails CI. Intentional breaks
require an explicit changelog note and golden update in the same PR.
