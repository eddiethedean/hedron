# What’s new in 0.16


!!! note "Current train is 0.41"

    Pin `hedron>=0.41.0,<0.42` for new apps. The pin below is historical for this train only.
    See [What’s new in 0.41](whats-new-0.41.md).

!!! note "Historical phase"

    This page describes **0.16**. The current published train is **0.41.x** (last `v0.41.0`). Pin `hedron>=0.41.0,<0.42`.

Phase **0.16** adds an optional `hedron-extras` toolkit for specialized data-app interactions and
analysis workbenches — without expanding the core runtime or adopting Streamlit-style reruns or a
Vue/WebSocket client.

## Highlights

- **`hedron[extras]` / `hedron-extras`:** independently installable feature extras with
  `FeatureManifest` discovery and install isolation.
- **Composition UI:** `ChoiceCards`, `TreeView`, `Steps`, `SplitPane`, `FloatingAction`,
  `KeyboardShortcuts`, focus/scroll-by-id, and lightweight recipes.
- **Workbenches:** faceted `DataExplorer` (emits bounded `TransformPlan`), schema-aware
  `JSONEditor`, CSP-safe `CodeEditor` **host stub** (no pinned CodeMirror 6 bundle),
  `ChartWorkbench`, and `CallableActionForm`.
- **Image tools:** compare, crop, region selection, and annotation overlays with numeric/list
  alternatives to dragging.
- **Editor extras:** `Calendar`, `SignaturePad`, `Typeahead`.
- **Display:** bounded `LogConsole` (no process-global capture) and presentation recipes.
- **Sandbox:** isolated browser-Python bridge with budgets and no server/session access.
- **Specialty (Experimental):** fail-closed `TerminalView`, joystick/device bridges, and a
  [native desktop shell recipe](native-desktop-shell.md).

## Testing

Workbench-flow helpers extend `AppScenario` (`assert_transform_plan_bounded`,
`assert_action_authorized`, `assert_http_fallback_present`, plus fixtures for trees/JSON/regions/
sandbox budgets).

## Upgrade notes

Pin `hedron>=0.16.0,<0.17` and install `hedron[extras]` only when needed. Specialty surfaces remain
Experimental — do not market them as unqualified Supported for CRUD/admin onboarding.
