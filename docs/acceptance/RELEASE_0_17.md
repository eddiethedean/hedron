# Hedron `v0.17` reactive dashboards and agent interfaces acceptance

Phase 0.17 delivers cohesive cross-filter dashboards, bounded incremental updates,
server-side notebook previews, an optional deny-by-default MCP projection, HTMX shell
authoring primitives, and leftover docs/assert completions — without a universal client
callback runtime or weakening the request/action boundary. Evidence is indexed by
[`release-gate-0.17.toml`](release-gate-0.17.toml).
**Zero Deferred:** every 0.17-owned gate row must be Verified at cut.

Owning RFCs: [RFC-0040](../rfcs/RFC-0040-INTERACTION-GRAPH.md),
[RFC-0041](../rfcs/RFC-0041-PROPERTY-COLLECTION-PATCH.md),
[RFC-0042](../rfcs/RFC-0042-NOTEBOOK-PREVIEW.md),
[RFC-0043](../rfcs/RFC-0043-MCP-PROJECTION.md),
[RFC-0044](../rfcs/RFC-0044-SHELL-INTERACTION-RESULT.md).

## Spec packet

- [x] ROADMAP §0.17 scope accepted; Dash and NiceGUI cross-checks refreshed for 0.17 entry.
- [x] RFCs 0040–0044 Accepted.
- [x] Entry gate: 0.16 evidence remains closed; 0.17 gate TOML owns Planned→Verified rows only.
- [x] Gate checker recognizes `0.17` (`python scripts/check_release_gate.py 0.17.0 --allow-planned`
  during scaffold; Zero Deferred + Verified at cut).

## Graph and patches

- [ ] `DashboardBinding` / `InteractionGraph` / `TriggerContext` / lifecycle. *(`GRAPH-017`)*
- [ ] `PropertyPatch` / `CollectionPatch` / structured collections. *(`PATCH-017`)*
- [ ] Cross-filter composition (chart/grid/form/state/jobs/map viewport triggers). *(`XFILTER-017`)*
- [ ] Interaction-graph recorder and deterministic replay. *(`REPLAY-017`)*

## Notebook and MCP

- [ ] Optional `hedron-notebook` preview helper (experimental; localhost-oriented). *(`NOTEBOOK-017`)*
- [ ] Optional `hedron-mcp` Streamable HTTP projection (experimental; deny-by-default empty).
  *(`MCP-017`)*

## Shell, docs, asserts, migration

- [ ] NavLink / `class_` / OobHost / AppShell / public InteractionResult→Response API.
  *(`SHELL-017`)*
- [ ] `error-codes.md` aligned with registered `HED-*` catalog (`#15`). *(`HEDDOC-017`)*
- [ ] Dialog / Tabs / Pagination / Lazy markup asserts (`#24`; Toast remains 0.15).
  *(`ASSERT-017`)*
- [ ] Dash / NiceGUI migration inventories without auto-conversion claims. *(`MIGRATE-017`)*

## Packaging

- [ ] Coordinated package verify (`scripts/verify_pkg_17.py` when packages exist). *(`PKG-017`)*

## Exit

- [ ] Full regression suite. *(`REGRESS-017`)*

**Exit pending** — promote every 0.17-owned row to Verified with Zero Deferred before publishing
`v0.17.0`.
