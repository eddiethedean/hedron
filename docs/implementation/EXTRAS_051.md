# Curated extras depth and lifecycle closure (`v0.51`)

**Status:** Planned; Stage 0 contract refined against Published in-tree `v0.50.3` (D-088). Human AT (`SR-021`) stays open.<br>
**Tracking:** [#507](https://github.com/eddiethedean/hedron/issues/507)<br>
**Related:** [#504](https://github.com/eddiethedean/hedron/issues/504)–[#506](https://github.com/eddiethedean/hedron/issues/506)<br>
**Decision/RFC:** D-087, refined by D-088 / [RFC-0078](../rfcs/RFC-0078-CURATED-EXTRAS-LIFECYCLE.md)<br>
**Planning baseline:** Published in-tree `v0.50.3`<br>
**Target:** Hedron `v0.51.0`<br>
**Required predecessor:** Verified in-tree `v0.50.3`

Do **not** start Stage 1 during this refine. No 0.51 runtime or version claim.
In-tree Verified 0.50.3 is enough predecessor evidence; do not wait on
[#501](https://github.com/eddiethedean/hedron/issues/501) PyPI assets.

## Consume shipped, do not fork

- `hedron_extras.plugin` / `hedron_extras.experimental` entry points.
- `HEDRON_EXPERIMENTAL_UI` or explicit `hedron_extras_experimental` enable.
- `feature_specs`: `composition`, `workbench`, `image_tools`, `calendar`,
  `signature`, `typeahead`, `display`, `recipes`, `sandbox`.
- Browser hosts listed in
  [extras-lifecycle-051.toml](../acceptance/extras-lifecycle-051.toml).
- Optional extras in `packages/hedron-extras/pyproject.toml`.
- EXTRAS-025 quarantine
  ([extras-quarantine-025.toml](../acceptance/extras-quarantine-025.toml)).
- Do **not** reopen `polling_only`, `MORPH-048`, Explorer 0.50, 0.52, 0.53,
  or `SR-021`.

Lock files:
[extras-capability-inventory-051.toml](../acceptance/extras-capability-inventory-051.toml),
[extras-descriptor-051.toml](../acceptance/extras-descriptor-051.toml),
[extras-experimental-disposition-051.toml](../acceptance/extras-experimental-disposition-051.toml),
[extras-workbench-051.toml](../acceptance/extras-workbench-051.toml),
[extras-lifecycle-051.toml](../acceptance/extras-lifecycle-051.toml),
[extras-companion-authoring-051.toml](../acceptance/extras-companion-authoring-051.toml).

## Architecture

```text
hedron-extras          ExtrasFeature inventory, plugin registration, assets
       │
       ├── Supported toolkit (composition, workbench, editors, image, display, recipes)
       ├── Experimental sandbox (opt-in registration in Stage 1)
       └── experimental-ui plugin (CodeEditor / Terminal / joystick / device)
hedron (flagship)      companion #504–#506 authoring (not extras gates)
hedron-core            element ABI / FeatureBundle / catalog projections only
```

1. `ExtrasFeature` lives in `hedron-extras`. It consumes `register_feature`.
2. Experimental UI stays a separate plugin. Quarantine XOR remains.
3. Sandbox stays Experimental; Supported `hedron[extras]` must not pull it.
4. Companion password/reveal/busy work is flagship HTMX, not extras inventory.

## Work packages (Stage 1 only)

### M1 — Inventory and descriptor

- Machine-readable capability inventory from 0.50.3 components.
- `ExtrasFeature` additive over `feature_specs`.
- Align sandbox stability label with Experimental.

### M2 — Lifecycle and isolation

- Shared HTMX connect/disconnect/reconnect/cleanup for Supported hosts.
- Optional-dependency isolation (minimal / per-feature / all wheels).
- Move sandbox default registration to opt-in.

### M3 — Workbench / image / input depth

- Bounded JSON/Data/Chart workflows; no embedded-code eval.
- Image intents with server-confirmed output.
- TreeView/Typeahead providers with abort and fallbacks.

### M4 — Evidence and companion authoring

- Browser/a11y/security/visual/supply matrices for Supported extras.
- Flagship #504–#506 close or explicit defer.
- 0.50 upgrade/rollback fixtures.

## Explicitly not in 0.51

CodeMirror 6 graduation, Terminal/joystick/device graduation, sandbox in
Supported `hedron[extras]`, `hedron package doctor`, conformance runtimes,
live-transport promotion, `SR-021`, Hedron `1.0`.
