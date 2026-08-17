# Upgrade to Hedron 0.46

This guide covers an application upgrade onto the **0.46.x** train
(current tip **`v0.46.0`**). New applications should use
[Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.46.x adds opt-in package-native features that compile onto Published 0.43–0.45
seams (D-075 / D-079 / RFC-0073):

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

Apps that never call `include_feature` stay request-path identical to 0.45. Direct package APIs
remain. Prior trains remain in force: typed interaction catalog (0.45), type-driven authoring (0.44),
refreshable views and commands (0.43), production-grade
Web Component inventory (0.42), browser composition / draft transfer / navigation (0.41),
authoring kit (0.40), rich data / OptimisticMutation (0.39), high-fidelity charts
(`hedron-charts` `0.2.x`, 0.38), MCP (`hedron-mcp` `0.2.x`), Workbench ASGI
(`fastapi-workbench` `1.x`), and Posit (`hedron[posit]` / `HedronPosit`). Polling remains
the production recommendation for live status. SSE, WebSocket, streaming, and navigation
preload remain experimental.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm you are on a recent pin (`hedron>=0.29.0,<0.30` through `>=0.45.0,<0.46`,
   or the tip pin already).
3. Existing 0.42–0.45 handlers keep working. Unused `include_feature` is request-path
   identical to 0.45.
4. Adopt bundles after modeled 0.44 types and 0.45 catalog consumers if you need fingerprints.
5. If you use editable grids or charts, keep `hedron[data]` / `hedron[charts]` on the
   tip pin (or `hedron-charts>=0.2.0,<0.3`).
6. If you use Posit Workbench or Connect, prefer `hedron[posit]` / `HedronPosit`.

## Install

```bash
python -m pip install -U "hedron>=0.46.0,<0.47"
python -m pip install -U "hedron[data]>=0.46.0,<0.47"
python -m pip install -U "hedron[charts]>=0.46.0,<0.47"
# independent charts satellite:
python -m pip install -U "hedron-charts>=0.2.0,<0.3"
# optional production-grade elements inventory:
python -m pip install -U "hedron[elements]>=0.46.0,<0.47"
```

## Behavioral notes (0.45 → 0.46)

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

- Keep existing pages and 0.45 catalog consumers running unchanged, then add one
  `include_feature` at a time.
- Smoke workspace list/detail/create/edit through ordinary HTTP as well as HTMX.
- Confirm `hedron inspect features` and Explorer Features without treating catalog presence as
  exposure.

## See also

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
