# Upgrade to Hedron 0.43

This guide covers an application upgrade onto the **0.43.x** train
(current tip **`v0.43.0`**). New applications should use
[Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.43.x adds refreshable views, command handles, and typed updates over the
existing region / `InteractionResult` stack (D-071 / RFC-0070):

- `@app.refreshable` returns a `FragmentHandle` that owns route, host, bind, refresh, and patches
- `@app.command` returns an `ActionHandle` for POST+CSRF mutations with ordinary HTTP fallback
- `refresh(view)` compiles to bounded HTMX events that rerun the view GET
- `Patch` / `PatchSet` compile into the existing OOB interaction stack
- Low-level `region` / `swap` / `@app.fragment` / `@app.action` APIs remain supported

Prior trains remain in force: production-grade Web Component inventory (0.42), browser
composition / draft transfer / navigation (0.41), authoring kit (0.40), rich data /
OptimisticMutation (0.39), high-fidelity charts (`hedron-charts` `0.2.x`, 0.38), MCP
(`hedron-mcp` `0.2.x`), Workbench ASGI (`fastapi-workbench` `1.x`), and Posit
(`hedron[posit]` / `HedronPosit`). Polling remains the production recommendation for live
status. SSE, WebSocket, streaming, and navigation preload remain experimental.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm you are on a recent pin (`hedron>=0.29.0,<0.30` through `>=0.42.0,<0.43`,
   or the tip pin already).
3. If you still author with `region` / `swap`, you can keep those pages unchanged on 0.43.
4. If you adopt handles, prefer generated paths/ids unless you already published explicit
   `path=` / `key=` values.
5. If you use editable grids or charts, keep `hedron[data]` / `hedron[charts]` on the
   tip pin (or `hedron-charts>=0.2.0,<0.3`).
6. If you use Posit Workbench or Connect, prefer `hedron[posit]` / `HedronPosit`.

## Install

```bash
python -m pip install -U "hedron>=0.43.0,<0.44"
python -m pip install -U "hedron[data]>=0.43.0,<0.44"
python -m pip install -U "hedron[charts]>=0.43.0,<0.44"
# independent charts satellite:
python -m pip install -U "hedron-charts>=0.2.0,<0.3"
# optional production-grade elements inventory:
python -m pip install -U "hedron[elements]>=0.43.0,<0.44"
```

## Behavioral notes (0.42 → 0.43)

1. **Additive only.** `@app.fragment` and `@app.action` still return the original function.
   New `@app.refreshable` / `@app.command` return handles.
2. **Refresh is not a full page reload.** Top-level `refresh()` compiles to bounded
   `HX-Trigger` events; it does not set `HX-Refresh`.
3. **Generated ids are not rollback-stable.** Explicit `path=` / `key=` are the
   compatibility hatches. Rollback: pin `hedron>=0.42.0,<0.43`.
4. **Mixed refresh + patch** in one return fails closed. Toast + refresh is allowed.

## After upgrading

- Keep existing region pages running unchanged, then migrate one interaction at a time.
- Smoke command buttons and forms through ordinary HTTP as well as HTMX.
- Confirm Explorer's view/command graph and `hedron check` against copied stale paths.

## See also

- [What's new in 0.43](whats-new-0.43.md)
- [What's new in 0.42](whats-new-0.42.md)
- [Release notes](release-notes.md)
- [upgrade-fixtures-043](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/upgrade-fixtures-043.md)
- [COMPATIBILITY](../COMPATIBILITY.md)
- [RELEASE_0_43](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_43.md)
