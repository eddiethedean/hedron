# Upgrade to Hedron 0.40

This guide covers an application upgrade onto the **0.40.x** train
(current tip **`v0.40.0`**). New applications should use
[Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.40.x ships the public Web Component authoring kit and metadata parity
(D-068 / RFC-0060):

- Public author kit and `hedron new element` scaffold for third-party elements
- Plugin `register_element_definition` / `register_asset` without private registry APIs
- HDJ / Explorer / theme / conformance parity for element ABI, parts, slots, and tokens
- `ReactMigrationMatrix` with dispositions; Experimental React-island bridge as
  docs/reference only (not inside `hedron-elements`)
- Optional in-repo `@hedron/elements` modules/TS types; Python no-Node path unchanged
- Remediations #162, #203, #204, #219, #220, and #222

Prior trains remain in force: rich data / OptimisticMutation (0.39), high-fidelity charts
(`hedron-charts` `0.2.x`, 0.38), Alpha `hedron-elements` form/primitives (0.37), Web
Component ABI (0.36), MCP (`hedron-mcp` `0.2.x`), Workbench ASGI (`fastapi-workbench`
`1.x`), and Posit (`hedron[posit]` / `HedronPosit`). Polling remains the production
recommendation for live status. SSE, WebSocket, streaming, and navigation preload remain
experimental.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm you are on a recent pin (`hedron>=0.29.0,<0.30` through `>=0.39.0,<0.40`,
   or the tip pin already).
3. If you author custom elements, plan to use the public author kit / plugin APIs rather
   than private registry imports — see [What's new in 0.40](whats-new-0.40.md).
4. If you use editable grids or charts, keep `hedron[data]` / `hedron[charts]` on the
   tip pin (or `hedron-charts>=0.2.0,<0.3`).
5. If you use Posit Workbench or Connect, prefer `hedron[posit]` / `HedronPosit`.
6. Optional: keep `hedron[elements]` for Alpha form-associated hosts from 0.37+.

## Install

```bash
python -m pip install -U "hedron>=0.40.0,<0.41"
python -m pip install -U "hedron[data]>=0.40.0,<0.41"
python -m pip install -U "hedron[charts]>=0.40.0,<0.41"
# independent charts satellite:
python -m pip install -U "hedron-charts>=0.2.0,<0.3"
# optional Alpha elements:
python -m pip install -U "hedron[elements]>=0.40.0,<0.41"
```

## Behavioral notes (0.39 → 0.40)

1. **Element authoring** uses public `PluginContext` registration and
   `ElementDefinitionMeta` fields (`parts` / `slots` / `tokens`) rather than private
   registry helpers.
2. **HDJ prologues** may declare `elements`, `element_abi`, `element_modules`, and
   `element_events`; undeclared custom tags fail closed when validated against a registry.
3. **React islands** remain Experimental docs/reference only — do not treat the island
   bridge as Supported production surface inside `hedron-elements`.
4. **Rollback** from 0.40 tip: pin `hedron>=0.39.0,<0.40` (and keep charts on
   `hedron-charts>=0.2.0,<0.3` if needed).

## After upgrading

- If you ship custom elements, smoke register/load via the public plugin APIs.
- Re-check HDJ element declarations against Explorer / conformance fixtures if you declare
  custom tags.
- Re-run your app's critical paths on Chromium; Firefox/WebKit remain in the CI matrix.

## See also

- [What's new in 0.40](whats-new-0.40.md)
- [What's new in 0.39](whats-new-0.39.md)
- [Release notes](release-notes.md)
- [upgrade-fixtures-040](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/upgrade-fixtures-040.md)
- [COMPATIBILITY](../COMPATIBILITY.md)
- [RELEASE_0_40](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_40.md)
