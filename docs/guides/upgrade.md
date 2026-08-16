# Upgrade to Hedron 0.44

This guide covers an application upgrade onto the **0.44.x** train
(current tip **`v0.44.0`**). New applications should use
[Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.44.x adds opt-in type-driven authoring over 0.43 refreshable views and
commands (D-072 / RFC-0071):

- `ViewParams` / `FormBody` mark one Pydantic model as the bindable or form boundary
- `Sensitive` / `InstanceKey` / `Control` / `Refreshes` / `Updates` are immutable annotation metadata
- `ActionHandle.form()` generates native forms for the closed field inventory
- Declared effects are checked against returned `refresh()` / `PatchSet` values; they never execute
- `OutcomeMap(case(...), ...)` maps discriminated results; arbitrary `BaseModel` returns are not auto-rendered
- Optional `RefreshableView` / `CommandHandler` classes compile to the same handles as functions
- Unmodeled 0.43 handlers, explicit `Form(action=handle)`, and low-level `region` / `swap` APIs remain

Prior trains remain in force: refreshable views and commands (0.43), production-grade
Web Component inventory (0.42), browser composition / draft transfer / navigation (0.41),
authoring kit (0.40), rich data / OptimisticMutation (0.39), high-fidelity charts
(`hedron-charts` `0.2.x`, 0.38), MCP (`hedron-mcp` `0.2.x`), Workbench ASGI
(`fastapi-workbench` `1.x`), and Posit (`hedron[posit]` / `HedronPosit`). Polling remains
the production recommendation for live status. SSE, WebSocket, streaming, and navigation
preload remain experimental.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm you are on a recent pin (`hedron>=0.29.0,<0.30` through `>=0.43.0,<0.44`,
   or the tip pin already).
3. Existing 0.42 and 0.43 handlers keep working without `ViewParams` / `FormBody`.
4. Adopt one `ViewParams` or `FormBody` model before class handlers.
5. If you use editable grids or charts, keep `hedron[data]` / `hedron[charts]` on the
   tip pin (or `hedron-charts>=0.2.0,<0.3`).
6. If you use Posit Workbench or Connect, prefer `hedron[posit]` / `HedronPosit`.

## Install

```bash
python -m pip install -U "hedron>=0.44.0,<0.45"
python -m pip install -U "hedron[data]>=0.44.0,<0.45"
python -m pip install -U "hedron[charts]>=0.44.0,<0.45"
# independent charts satellite:
python -m pip install -U "hedron-charts>=0.2.0,<0.3"
# optional production-grade elements inventory:
python -m pip install -U "hedron[elements]>=0.44.0,<0.45"
```

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

- Keep existing region and unmodeled handle pages running unchanged, then add one
  `ViewParams` / `FormBody` model at a time.
- Smoke command buttons and generated forms through ordinary HTTP as well as HTMX.
- Confirm Explorer's redacted TypeSchema and `hedron check` (static never imports the target).

## See also

- [What's new in 0.44](whats-new-0.44.md)
- [What's new in 0.43](whats-new-0.43.md)
- [Type-driven authoring](../api/TYPE_DRIVEN_AUTHORING.md)
- [Release notes](release-notes.md)
- [upgrade-fixtures-044](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/upgrade-fixtures-044.md)
- [COMPATIBILITY](../COMPATIBILITY.md)
- [RELEASE_0_44](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_44.md)
