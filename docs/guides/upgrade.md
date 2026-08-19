# Upgrade to Hedron 0.50

This guide covers an application upgrade onto the **0.50.x** train
(`v0.50.1` on PyPI; in-tree `v0.50.3`). Public-index notes: [Installation](../getting-started/installation.md).
New applications should use [Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.50.x ships Explorer architecture and companion HTMX authoring on top of the
0.49 FastAPI/Pydantic convergence:

- Thin `explorer_router`, `ExplorerProvider` isolation, cursor pagination, catalog diffs, and CLI/HTML/JSON agreement when `hedron-explorer` is installed
- Production still force-offs `explorer="development"` after `RISK_EXPLORER_DEVELOPMENT` (accept the risk, Explorer still does not mount)
- `ActionHandle.effect` / `after(load=)`, `Lazy` error templates, `Select.depends_on`, and danger `Toast` dismiss compile to HTMX
- 0.49 handle, TypeSchema, and catalog contracts remain:

Hedron 0.49.x compiles existing handle, TypeSchema, and catalog plans onto FastAPI:

- `DependsOn` / `DependencyLifetime` compile to FastAPI `Depends(scope="function"|"request")`
- `BoundaryBindingPlan` chooses native-model or expanded-fields; `BindingPlan` stays URL identity
- Additive TypeSchema v2 input/output projections; v1 readers remain
- Tagged public-wire `kind` unions and cached TypeAdapter on non-FormBody candidates
- Router provenance, typed OpenAPI, and non-granting `RequiresScopes`
- Workbench/Posit keep custom loaders. FailFast / Pydantic `MISSING` stay research-only

0.48 HTMX extensions remain:

- Closed `Page.htmx_extensions` / `HtmxExtension` / `ExtensionSet` with demand-driven pinned local `sse`, `head-support`, and `preload` assets
- Unset pages keep the 0.47 `sse` + `head-support` compatibility default; `htmx_extensions=()` loads zero extension bytes
- Typed `SseRegion` / `SseTrigger` over experimental SSE helpers; polling remains the Supported fallback
- Idiomorph / morph swap is **Deferred** and is not a Supported capability

Maps from 0.47 remain:

- `MapSpec` / `MapPlan` / `compile_map` compile a closed, redacted map grammar
- `hedron_maps.Map` defaults to attributed `OpenStreetMap.standard()`; core `hedron.Map` is unchanged
- Custom XYZ / TileJSON / vector sources, static images, PMTiles, bounded MBTiles, and blank maps
- Pinned strict-CSP MapLibre behind `hedron-map`; `MapInteraction` binds typed events
- Semantic table alternatives survive no JavaScript / WebGL / CSP / network failure

Apps that never install `hedron-maps` stay request-path identical to 0.46. Direct
`hedron.Map` and explicit chart map adapters remain. Prior trains remain in force:
package-native workflows (0.46), typed interaction catalog (0.45), type-driven authoring (0.44),
refreshable views and commands (0.43), production-grade
Web Component inventory (0.42), browser composition / draft transfer / navigation (0.41),
authoring kit (0.40), rich data / OptimisticMutation (0.39), high-fidelity charts
(`hedron-charts` `0.2.x`, 0.38), MCP (`hedron-mcp` `0.2.x`), Workbench ASGI
(`fastapi-workbench` `1.x`), and Posit (`hedron[posit]` / `HedronPosit`). Polling remains
the production recommendation for live status. SSE, WebSocket, streaming, and navigation
preload remain experimental.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm you are on a recent pin (`hedron>=0.29.0,<0.30` through `>=0.51.0,<0.52`,
   or the tip pin already). Public-index notes: [Installation](../getting-started/installation.md).
3. Existing 0.42–0.46 handlers and unused `include_feature` keep working.
4. Adopt maps only via `hedron[maps]` / `from hedron_maps import …`.
5. If you use editable grids or charts, keep `hedron[data]` / `hedron[charts]` on the
   tip pin (or `hedron-charts>=0.2.0,<0.3`).
6. If you use Posit Workbench or Connect, prefer `hedron[posit]` / `HedronPosit`.

## Install

```bash
python -m pip install -U "hedron>=0.51.0,<0.52"
python -m pip install -U "hedron[data]>=0.51.0,<0.52"
python -m pip install -U "hedron[charts]>=0.51.0,<0.52"
python -m pip install -U "hedron[maps]>=0.51.0,<0.52"
# independent charts satellite:
python -m pip install -U "hedron-charts>=0.2.0,<0.3"
# optional production-grade elements inventory:
python -m pip install -U "hedron[elements]>=0.51.0,<0.52"
```

Public-index notes: [Installation](../getting-started/installation.md).

## Behavioral notes (0.46 → 0.47)

1. **Core Map stays core.** `from hedron import Map` does not gain an OSM default or MapLibre host.
2. **OSM default is `hedron_maps.Map` only.** `basemap=None` is a blank map, not OSM.
3. **Charts map adapters stay explicit.** MapLibre/Folium/PyDeck on `hedron-charts` do not
   silently switch to `hedron-maps`.
4. **Rollback:** uninstall `hedron-maps` and revert `hedron_maps` imports; pin
   `hedron>=0.46.0,<0.47` from the registry.
5. **Map origin policy.** Custom `OpenStreetMap(tile_url=...)` and `Map(tiles=)` require
   exact-origin allowlists; empty prefixes fail closed.
6. **Generated list views page.** `DataWorkspace` list routes honor `offset` / `limit` /
   `sort` / `q` and allowlisted field filters.
7. **MCP authorize isolation.** Pin `hedron-mcp>=0.2.1,<0.3` (or `hedron[mcp]`) so a second
   `McpExposure.apply` cannot overwrite the first tool's authorize hook.

## Behavioral notes (0.45 → 0.46)

Hedron 0.46.x added opt-in package-native features that compile onto existing
0.43–0.45 seams:

- `FeatureBundle` / `Hedron.include_feature` atomically register ordinary handles, components,
  scenarios, and stacked projections; they are not executors
- `DataWorkspace` produces a beginner `app.include_feature(orders)` bundle over an explicit
  `DataEditorSource` and `DataWorkspacePolicy`
- `ChartInteraction` maps Supported `select` / `inspect` / `focus` / `reset` onto `ActionHandle`
  effects; `legend_filter` / `brush` / `drill_intent` stay Experimental
- Schema-aware elements are opt-in (`ActionHandle.form(enhance="elements")`); native forms remain
  canonical
- `McpExposure` and `RemoteWorkflow` wrap live MCP/Gradio registration; catalog presence never
  grants exposure

1. **Bundles are not executors.** `include_feature` registers ordinary 0.43–0.45 handles,
   components, scenarios, and stacked projections. Authz stays explicit; catalog presence is not
   a capability.
2. **Unused include is request-path identical.** Apps that never call `include_feature` keep the
   0.45 request path.
3. **MCP/Gradio stay opt-in.** `McpExposure` / `RemoteWorkflow` wrap live registration; consuming
   the catalog never grants exposure.
4. **Rollback:** pin `hedron>=0.45.0,<0.46`. Eject or remove `include_feature` first; explicit
   handlers stay.

## Behavioral notes (0.44 → 0.45)

1. **Catalog is not authority.** Routes, validation, authorization, and execution still come from
   0.43 descriptors and optional 0.44 `TypeSchema`. Catalog ids/fingerprints are not capabilities.
2. **Unused catalog is request-path neutral.** Apps that never inspect `app.interactions` keep the
   0.44 request path.
3. **Production `interactions.json`** is required only when the live sealed catalog has entries.
4. **Rollback:** pin `hedron>=0.44.0,<0.45`. Remove catalog consumers first; handlers stay.

## Behavioral notes (0.43 → 0.44)


1. **Opt-in only.** Unmodeled handlers keep structural `bind`, explicit forms, and
   dynamic/observed effects. `schema` stays `None` until a Hedron marker is present.
2. **One compiled validator.** `bind(model)` and `bind(**fields)` share the Pydantic
   adapter. A bare `BaseModel` argument is not inferred as a boundary.
3. **Forms are inventory-backed.** `ActionHandle.form()` exists only for a supported
   `FormBody`. Nested models, unions, and lists of models need explicit `Form` overrides.
4. **Declared effects do not execute.** Actual `refresh()` / `PatchSet` targets must be
   a subset of declared same-app handles.
5. **Rollback:** pin `hedron>=0.43.0,<0.44`. Generated form ids follow the 0.43 handle ids.

## Behavioral notes (0.42 → 0.43)

1. **Additive only.** `@app.fragment` and `@app.action` still return the original function.
   New `@app.refreshable` / `@app.command` return handles.
2. **Refresh is not a full page reload.** Top-level `refresh()` compiles to bounded
   `HX-Trigger` events; it does not set `HX-Refresh`.
3. **Generated ids are not rollback-stable.** Explicit `path=` / `key=` are the
   compatibility hatches. Rollback: pin `hedron>=0.42.0,<0.43`.
4. **Mixed refresh + patch** in one return fails closed. Toast + refresh is allowed.

## After upgrading

- Keep existing pages and 0.46 map-free routes running unchanged, then add one
  `hedron_maps.Map` at a time.
- Smoke OSM, custom XYZ, and one offline path (static image or blank map) with and without JavaScript.
- Confirm Explorer `/hedron-explorer/maps` and `hedron inspect` without treating catalog presence as
  exposure.

## See also

- [What's new in 0.50](whats-new-0.50.md)
- [What's new in 0.49](whats-new-0.49.md)
- [What's new in 0.48](whats-new-0.48.md)
- [What's new in 0.46](whats-new-0.46.md)
- [What's new in 0.45](whats-new-0.45.md)
- [What's new in 0.44](whats-new-0.44.md)
- [What's new in 0.43](whats-new-0.43.md)
- [Package-native typed workflows](../api/PACKAGE_WORKFLOWS.md)
- [Interaction catalog](../api/INTERACTION_CATALOG.md)
- [Type-driven authoring](../api/TYPE_DRIVEN_AUTHORING.md)
- [Release notes](release-notes.md)
- [upgrade-fixtures-046](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/upgrade-fixtures-046.md)
- [COMPATIBILITY](../COMPATIBILITY.md)
- [RELEASE_0_46](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_46.md)
