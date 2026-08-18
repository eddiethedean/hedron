---
status: beta
---

# Explorer architecture (0.50)

Phase 0.50 (D-085 / D-086 / RFC-0077) turns the Component Explorer into a modular
development product with a versioned `ExplorerProvider`, shared query services, and
headless/CLI parity. Planning baseline was Published in-tree `v0.49.1`. Tracking
[#501](https://github.com/eddiethedean/hedron/issues/501). Related authoring
[#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500) /
[#502](https://github.com/eddiethedean/hedron/issues/502) /
[#503](https://github.com/eddiethedean/hedron/issues/503) shipped on this cut and
are not Explorer gates. Living tip is in-tree `v0.50.0` (tag/PyPI deferred).

The shipped 0.49 mount/mode contract remains [Explorer API](EXPLORER.md). This page is
the 0.50 architecture contract.

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

## Provider

`ExplorerProvider` declares capabilities, timeout, max payload, ordering, and
redaction profile. Register with `PluginContext.register_explorer_provider(...)`
(stamps `plugin=self.meta.name`). Existing `register_explorer_panel` and `path=`
registrations remain valid; meta-only rows get conservative provider defaults.
First-party metadata panels (`hedron-data-schema`, `hedron-charts-viz`, `hedron-maps`,
`hedron-extras-features`, `sample-kit-callout`) keep their paths and do not gain nav
entries from `path=` alone. Isolation (timeout/crash/payload/ordering/redaction)
lives in `hedron-explorer`.

Migration from 0.49: keep `register_explorer_panel`; add `register_explorer_provider`
only when you need timeout, capabilities, or redaction_profile. Do not add fields to
`ExplorerPanelMeta`.

## Query and headless

Silent `[:200]` component slices become pagination or truncation diagnostics.
CLI `hedron inspect` / `graph` / `check` share identities with HTML/JSON when
`hedron-explorer` is installed; otherwise skip is labeled. SARIF stays
`hedron check --format sarif` (`diagnostics_to_sarif`). Graph JSON currently
diverges on `inverse_consumers`.

## Laboratory

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
