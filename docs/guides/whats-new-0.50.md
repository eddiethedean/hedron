# What's new in 0.50

Pin `hedron>=0.50.1,<0.51`. This version is on PyPI.

## 0.50.1 patch

Correctness and security patch on the 0.50 train. Spreadsheet combining-mark
prefixes, HTMX `this` targets, control `id`s, TerminalView CSRF, formula coerce-to-zero,
chart tabular/negative-Y/GreatTables/`hedron[charts]` pin, frozen element markup,
ActionAsync `hx-target`, and Explorer dashboard-graph / packages / maps / security wiring.

## Highlights

- Explorer architecture: thin `explorer_router`, services/views split, frozen
  `/hedron-explorer/` mount and CSRF/simulate allowlists.
- Additive `ExplorerProvider` v1 beside `ExplorerPanelMeta` (timeout, crash, payload,
  ordering, redaction isolation).
- Cursor pagination and `HED-EXPLORER-0001` truncation diagnostics instead of silent slices.
- Catalog/manifest/route/schema diffs; CLI `inspect`/`graph`/`check`/`routes` share
  explorer services when `hedron-explorer` is installed (labeled skip otherwise).
  SARIF stays `hedron check --format sarif` via `diagnostics_to_sarif`.
- Bounded interaction lab and read-only package health (not `hedron package doctor`).
- HTMX authoring: `Hx(trigger/include/validate)`, `ActionHandle.effect` / `.after`,
  dependent `Select`/`Control(depends_on=)`, `Lazy`/`FragmentHost` error slots,
  `Toast(..., ttl_ms=)` / `ToastHost()`, `InteractionPolicy.history_restore`.

Explorer architecture, operator-grade development tooling, and HTMX authoring
primitives. Tracking: [#501](https://github.com/eddiethedean/hedron/issues/501).
