# Upgrade to Hedron 0.39

This guide covers an application upgrade onto the **0.39.x** train
(current tip **`v0.39.0`**). New applications should use
[Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.39.x ships rich data surfaces on the public element ABI (D-067 / RFC-0060):

- ABI-conforming `<hedron-data-editor>` with retained SSR fallback after upgrade
- Typed `OptimisticMutation` for **bounded DataEditor / collection cell edits** only
  (deny-by-default for auth, payments, irreversible deletes, and other risk classes)
- `compose_chartlink_039` so DataTable/DataEditor selection consumes Published 0.38
  `hedron-chart` events without a parallel renderer
- Owned Experimental exceptions for map / media / editor surfaces that cannot yet meet
  the shared ABI gates

Prior trains remain in force: high-fidelity charts (`hedron-charts` `0.2.x`, 0.38),
Alpha `hedron-elements` form/primitives (0.37), Web Component ABI (0.36), MCP
(`hedron-mcp` `0.2.x`), Workbench ASGI (`fastapi-workbench` `1.x`), and Posit
(`hedron[posit]` / `HedronPosit`). Polling remains the production recommendation for
live status. SSE, WebSocket, streaming, and navigation preload remain experimental.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm you are on a recent pin (`hedron>=0.29.0,<0.30` through `>=0.38.0,<0.39`,
   or the tip pin already).
3. If you use editable grids, plan to install `hedron[data]>=0.39.0,<0.40` and read the
   DataEditor ABI notes in [DATA.md](../api/DATA.md).
4. If you use charts with table cross-filter, keep `hedron[charts]>=0.39.0,<0.40` (or
   `hedron-charts>=0.2.0,<0.3`) — chartlink consumes the Published 0.38 chart contract.
5. If you use Posit Workbench or Connect, prefer `hedron[posit]` / `HedronPosit`.
6. Optional: keep `hedron[elements]` for Alpha form-associated hosts from 0.37.

## Install

```bash
python -m pip install -U "hedron>=0.39.0,<0.40"
python -m pip install -U "hedron[data]>=0.39.0,<0.40"
python -m pip install -U "hedron[charts]>=0.39.0,<0.40"
# independent charts satellite:
python -m pip install -U "hedron-charts>=0.2.0,<0.3"
# optional Alpha elements:
python -m pip install -U "hedron[elements]>=0.39.0,<0.40"
```

## Behavioral notes (0.38 → 0.39)

1. **DataEditor markup** upgrades to `<hedron-data-editor data-hedron-abi …>` with the
   previous SSR table retained as a fallback (`data-hedron-fallback`, `aria-hidden`
   after boot). Do not assume the fallback node is removed from the DOM.
2. **Optimistic edits** are Supported only for bounded collection/cell edits. Other risk
   classes fail closed (`assert_optimism_allowed` / deny-by-default).
3. **Chart composition** uses `compose_chartlink_039` from `hedron_core.cross_filter`
   (or the data package helpers that wrap it). Do not introduce a second chart host for
   table↔chart linking.
4. **Rollback** from 0.39 tip: pin `hedron>=0.38.0,<0.39` (and keep charts on
   `hedron-charts>=0.2.0,<0.3` if needed).

## After upgrading

- Smoke your DataEditor save path and selection events.
- If you compose charts with tables, confirm cross-filter still fires on Published chart
  event kinds.
- Re-run your app's critical paths on Chromium; Firefox/WebKit remain in the CI matrix.

## See also

- [What's new in 0.39](whats-new-0.39.md)
- [What's new in 0.38](whats-new-0.38.md)
- [Release notes](release-notes.md)
- [upgrade-fixtures-039](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/upgrade-fixtures-039.md)
- [COMPATIBILITY](../COMPATIBILITY.md)
- [RELEASE_0_39](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_39.md)
