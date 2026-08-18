---
status: beta
---

# Explorer architecture (0.50 Planned)

Phase 0.50 (D-085 / D-086 / RFC-0077) turns the Component Explorer into a modular
development product with a versioned `ExplorerProvider`, shared query services, and
headless/CLI parity. Planning baseline is Published in-tree `v0.49.1`. Tracking
[#501](https://github.com/eddiethedean/hedron/issues/501). Related authoring
[#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500) /
[#502](https://github.com/eddiethedean/hedron/issues/502) /
[#503](https://github.com/eddiethedean/hedron/issues/503) are bound to 0.50 and
are not Explorer gates. **No Stage 0 runtime or version claim.** Living tip stays
`v0.49.1`.

The shipped 0.49 mount/mode contract remains [Explorer API](EXPLORER.md).

## Frozen mount

```python
from hedron import Hedron, Page, Text

app = Hedron(
    title="Demo",
    security="standard",
    session_secret="replace-me",
    explorer="development",  # requires hedron[dev]
)
```

Prefix `/hedron-explorer/`. Modes `off` / `development` / `secured`. Production
forces `development` off. Flask/Django do not mount `explorer_router`.

`explorer_router` is the FastAPI factory. `ExplorerPanelMeta` and
`register_explorer_panel` stay; `ExplorerProvider` is additive in `hedron-core`.

## Provider (Planned)

`ExplorerProvider` declares capabilities, timeout, max payload, ordering, and
redaction profile. Existing `path=` registrations remain valid. First-party
metadata panels (`hedron-data-schema`, `hedron-charts-viz`, `hedron-maps`,
`hedron-extras-features`, `sample-kit-callout`) do not gain nav entries from
`path=` alone.

## Query and headless (Planned)

Silent `[:200]` component slices become pagination or truncation diagnostics.
CLI `hedron inspect` / `graph` / `check` share identities with HTML/JSON when
`hedron-explorer` is installed; otherwise skip is labeled. SARIF stays
`hedron check --format sarif` (`diagnostics_to_sarif`). Graph JSON currently
diverges on `inverse_consumers`.

## Laboratory (Planned)

Safe preview ops only: `POST /hedron-explorer/api/simulate`,
`GET /hedron-explorer/api/click-preview`,
`POST /hedron-explorer/api/element-simulate`. Mutations stay 403 by default.
No invented auth. Package health is read-only; `hedron package doctor` stays 0.53.

## Explicitly not in 0.50

`EXPLORER-10-001` live traces stay Deferred. `/a11y` is not `EXPLORER-019`.
`REV-026-003` process-local audit stays accepted risk. Explorer is not a
production default.

See [RFC-0077](../rfcs/RFC-0077-EXPLORER-ARCHITECTURE.md) and
[implementation plan](../implementation/EXPLORER_050.md).
