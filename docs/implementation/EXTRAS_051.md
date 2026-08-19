# Curated extras depth and lifecycle closure (`v0.51`)

**Status:** Verified in-tree `v0.51.0` (D-088 Stage 0 preserved; Stage 1 shipped). Human AT (`SR-021`) stays open.<br>
**Tracking:** [#507](https://github.com/eddiethedean/hedron/issues/507) (tag/PyPI deferred)<br>
**Related:** [#504](https://github.com/eddiethedean/hedron/issues/504)–[#506](https://github.com/eddiethedean/hedron/issues/506)<br>
**Decision/RFC:** D-087, refined by D-088 / [RFC-0078](../rfcs/RFC-0078-CURATED-EXTRAS-LIFECYCLE.md)<br>
**Planning baseline:** Published in-tree `v0.50.3`<br>
**Target:** Hedron `v0.51.0` (in-tree; no Git tag yet)

## Consume shipped, do not fork

- `hedron_extras.plugin` / `hedron_extras.experimental` / `hedron_extras_sandbox`.
- `HEDRON_EXPERIMENTAL_UI` or explicit `hedron_extras_experimental` enable.
- `HEDRON_EXTRAS_SANDBOX` or explicit `hedron_extras_sandbox` enable.
- `feature_specs` via `ExtrasFeature`: `composition`, `workbench`, `image_tools`,
  `calendar`, `signature`, `typeahead`, `display`, `recipes`; sandbox on the
  opt-in plugin.
- Browser hosts listed in
  [extras-lifecycle-051.toml](../acceptance/extras-lifecycle-051.toml).
- Optional extras in `packages/hedron-extras/pyproject.toml`.
- EXTRAS-025 quarantine
  ([extras-quarantine-025.toml](../acceptance/extras-quarantine-025.toml)).
- Do **not** reopen `polling_only`, `MORPH-048`, Explorer 0.50, 0.52, 0.53,
  or `SR-021`.

## Architecture

```text
hedron-extras          ExtrasFeature inventory, plugin registration, assets
       │
       ├── Supported toolkit (composition, workbench, editors, image, display, recipes)
       ├── Experimental sandbox (hedron_extras_sandbox / HEDRON_EXTRAS_SANDBOX)
       └── experimental-ui plugin (CodeEditor / Terminal / joystick / device)
hedron (flagship)      companion #504–#506 authoring (not extras gates)
hedron-core            element ABI / FeatureBundle / catalog projections only
```

1. `ExtrasFeature` lives in `hedron-extras`. It consumes `register_feature`.
2. Experimental UI stays a separate plugin. Quarantine XOR remains.
3. Sandbox stays Experimental; Supported `hedron[extras]` must not pull it.
4. Companion password/reveal/busy work is flagship HTMX, not extras inventory.
