# What's new in 0.50

**Published `v0.50.0`**. Owning decisions: D-085 / D-086.
Tracking: [#501](https://github.com/eddiethedean/hedron/issues/501). Companion authoring:
[#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500),
[#502](https://github.com/eddiethedean/hedron/issues/502),
[#503](https://github.com/eddiethedean/hedron/issues/503).

Pin `hedron>=0.50.0,<0.51`. Public-index notes: [Installation](../getting-started/installation.md).

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

This cut does not tag Git, publish a GitHub Release, or upload PyPI.
