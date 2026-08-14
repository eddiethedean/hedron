# What's new in Hedron 0.39

!!! note "Current train is 0.40"

    Pin `hedron>=0.40.0,<0.41` for new apps. See [What's new in 0.40](whats-new-0.40.md).

**Published** as `v0.39.0` on 2026-08-14. Historical pin: `hedron>=0.39.0,<0.40`. Charts remain on the
Published 0.2 line: `hedron-charts>=0.2.0,<0.3`.

Phase **0.39** converges rich data surfaces onto the public Web Component ABI and proves typed
optimistic edits ([RFC-0060](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) / D-067).

## Highlights

- ABI-conforming **`<hedron-data-editor>`** with SSR fallback retained after upgrade
  (`data-hedron-fallback` / `aria-hidden`)
- Typed **`OptimisticMutation`** state machine (`proposed` → `submitted` → `confirmed`) with
  idempotency keys, conflict rebase, and deny-by-default risk classes outside bounded collection
  edits
- **`compose_chartlink_039`** binds Published 0.38 `hedron-chart` events to DataTable/DataEditor
  selection without a parallel chart renderer
- Owned **Experimental** exceptions for map / media / code-editor / specialty surfaces that cannot
  yet meet the shared ABI gates
- Worker / object-URL abort cleanup, media Range streaming, and the locked 27-issue rich-data
  remediation packet

## Honesty

- Human screen-reader / compensated AT (`SR-021`) remains **Planned** — not Supported.
- MapLibre / media capture / AG Grid / specialty editors stay **Experimental** where the inventory
  records an owned exception.
- Live SSE / WebSocket / streaming remain **experimental**; polling is the Supported production
  story.

## Pins

```bash
pip install "hedron>=0.40.0,<0.41"
pip install "hedron[data]>=0.40.0,<0.41"
# charts satellite (Published 0.38 line):
pip install "hedron-charts>=0.2.0,<0.3"
```

## See also

- [Data API](../api/DATA.md)
- [hedron-data package](../packages/hedron-data.md)
- [Upgrade](upgrade.md)
- [RELEASE_0_39](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_39.md)
