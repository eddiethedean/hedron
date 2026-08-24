# What’s new in 0.17


!!! note "Current train is 0.63"

    Pin `hedron>=0.53.0,<0.54` for new apps (checkout tip; current PyPI pin `>=0.63.0,<0.64`). The pin below is historical for this train only.
    See [What’s new in 0.51](whats-new-0.51.md).

!!! note "Historical phase"

    This page describes **0.17**. The current repository train is **0.63.x** (`v0.63.0` in-tree and on PyPI). Pin `hedron>=0.63.0,<0.64` from PyPI.

Phase **0.17** adds reactive dashboards and agent interfaces — finite interaction graphs,
bounded patches, optional notebook preview and deny-by-default MCP — plus HTMX shell authoring
primitives. See [release gate](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/release-gate-0.17.toml).

## Highlights

- **`DashboardBinding` / `InteractionGraph` / `TriggerContext`:** page-local, fail-closed graphs
  (RFC-0040).
- **`PropertyPatch` / `CollectionPatch`:** versioned incremental updates with full-fragment
  fallback (RFC-0041).
- **Cross-filter + recorder/replay:** compose chart/grid/map viewport triggers; deterministic
  fixtures (no sleep-based races).
- **`hedron-notebook` (Experimental / Alpha):** localhost-oriented server-side preview — not the
  0.16 browser-Python sandbox.
- **`hedron-mcp` (Experimental / Alpha):** Streamable HTTP projection; disabled and empty by
  default.
- **Shell DX:** `HtmxLink`/`NavLink`, `OobHost`/`AttrHost`, `AppShell`/`MainPanel`, public
  `render_interaction` (RFC-0044).
- **Docs/tests:** full `error-codes.md` catalog alignment; Dialog/Tabs/Pagination/Lazy markup
  asserts.

## Honesty

- Live SSE/WebSocket transports remain **experimental**; polling is Supported.
- Notebook preview and MCP are **not** Supported production servers/tools by default.
- No Dash-style global callback DAG and no automatic callback/JS conversion
  ([Dash migration](dash-migration.md), [NiceGUI migration](nicegui-migration.md)).

## Upgrade notes

Stay on the 0.17 line with an upper-bound pin when you need this phase.
Install `hedron[notebook]` / `hedron[mcp]` only when needed.
