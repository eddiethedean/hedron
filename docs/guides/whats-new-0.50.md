# What's new in 0.50

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and published 1.0 status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

For new apps, use the current compatibility floor `hedron>=1.0.0`. The 0.50 train last uploaded on PyPI as
**0.50.1**; in-tree 0.50 patches remained **0.50.3**.

## 0.50.3 patch

Correctness and security patch on the 0.50 train: `@command` and compiled refresh/patch
HTMX policies fail closed, secrets stay redacted at tabular/data boundaries, scaffolds
pin the PyPI floor while `registry_status` is deferred, and data/chart/patch/CSS/image/collab
defects listed in `tests/unit/test_bugfix_0503.py`.

## 0.50.2 patch

Correctness and security patch on the 0.50 train: login/OIDC CSRF compare, OIDC
`extra_params` and logout redirect, Flask leftover-session and CSRF fail-closed
gates, `include_component` rollback, handle ownership and ActionHandle merge,
FragmentHandle exception leak, HTMX 422/`h-view-*` targets, Explorer simulate,
Django policy/`include_component_path`, Flask cache-on-auth-error, `process_image`
root jail, Redis pipeline fail-closed, and plugin specifier parse codes.

## 0.50.1 patch

Correctness and security patch on the 0.50 train. Spreadsheet combining-mark
prefixes, HTMX `this` targets, control `id`s, TerminalView CSRF, formula coerce-to-zero,
chart tabular/negative-Y/GreatTables/`hedron[charts]` pin, frozen element markup,
ActionAsync `hx-target`, and Explorer dashboard-graph / packages / maps / security wiring.

## 0.50.0

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
