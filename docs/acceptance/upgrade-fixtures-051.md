# Phase 0.51 upgrade and rollback fixtures

**Status:** Verified; Stage 1 shipped against Published in-tree `v0.50.3` (D-088)<br>
**Planning baseline:** Published in-tree `v0.50.3`<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.50.3`<br>
**Target:** Hedron `v0.51.0`<br>
**Decision/RFC:** D-087 / D-088 / [RFC-0078](../rfcs/RFC-0078-CURATED-EXTRAS-LIFECYCLE.md)<br>
**Tracking:** [#507](https://github.com/eddiethedean/hedron/issues/507)

Baseline import, plugin, and optional-extra capture remains read-only during Stage 0.
PKG-051 upgrade source is **0.50**, not 0.49. Do not start Stage 1 during this refine.

## 0.50.3 install fixtures

1. `hedron[extras]` does not enable `hedron_extras_experimental` by default.
2. `CodeEditor` / `TerminalView` / `Joystick` / `DeviceBridge` import from
   `hedron_extras.experimental` only.
3. Optional extras: `json_editor`, `data_explorer`, `chart_workbench`,
   `image_tools`, `calendar`, `signature`, `typeahead`, `sandbox`,
   `code_editor`, `terminal`, `joystick`, `experimental-ui`, `all`.
4. `all` pulls `hedron-data` + `hedron-charts` only.
5. Plugin entry points: `hedron_extras`, `hedron_extras_experimental`, `hedron_extras_sandbox`.

## Honesty fixtures (Stage 1 migration)

1. `BrowserPythonSandbox` is Experimental. Stage 1 moved default registration to
   `hedron_extras_sandbox` / `HEDRON_EXTRAS_SANDBOX`. Rollback to 0.50.3 if an app
   relied on default-plugin sandbox registration.
2. Import `from hedron_extras.sandbox import BrowserPythonSandbox` is unchanged.
3. Do not graduate Experimental UI on upgrade.

## Frozen 0.50.3 browser tags

`hedron-extras-sandbox`, `hedron-extras-image-tools`,
`hedron-extras-calendar`, `hedron-extras-signature`,
`hedron-extras-typeahead`, `hedron-extras-composition`,
`hedron-extras-code-editor`, `hedron-extras-terminal`.

## Hosts

Flask/Django stay `projection_adapter`. No WSGI extras runtime. Explorer panel
`hedron-extras-features` remains at `/hedron-explorer/packages`.
