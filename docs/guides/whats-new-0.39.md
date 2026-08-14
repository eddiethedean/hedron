# What's new in Hedron 0.39

Hedron **`v0.39.0`** converges DataTable/DataEditor onto the public element ABI, proves typed
`OptimisticMutation` on bounded collection edits, and links Published `hedron-chart` cross-filter
composition without a parallel renderer.

## Highlights

- ABI-conforming `<hedron-data-editor>` with SSR fallback retained after upgrade
- `OptimisticMutation` state machine (proposed → submitted → confirmed) with idempotency and conflict rebase
- `compose_chartlink_039` binds Published 0.38 chart events to grid selection
- Owned Experimental exceptions for map/media/editor/specialty surfaces
- Worker/object-URL abort cleanup; media Range streaming; spreadsheet/import remediations

## Install

```bash
pip install "hedron>=0.39.0,<0.40"
```

Charts remain on the Published 0.2 line:

```bash
pip install "hedron-charts>=0.2.0,<0.3"
```

## Upgrade

See [upgrade-fixtures-039](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/upgrade-fixtures-039.md) and [upgrade](upgrade.md).
Rollback pins `hedron>=0.38.0,<0.39`.
