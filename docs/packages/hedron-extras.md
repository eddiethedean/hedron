# hedron-extras

Curated optional extras and analysis workbenches for Hedron.

**Package maturity:** Beta · **Train:** `0.40.x` (published `v0.40.0`) · pin `>=0.40.0,<0.41`  
**Flagship extra:** `hedron[extras]` · **Import:** `hedron_extras`  
**Plugin:** registers via `hedron.plugins` — not a second component runtime

Composition / workbench surfaces are Beta. The specialty sandbox remains Experimental.
Experimental UI is **registration/discovery gated**, not import-gated:
`CodeEditor`, `TerminalView`, joystick, and device bridges remain importable from
`hedron_extras.experimental` (and older `workbench` / `specialty` paths where present), but
**default plugin registration** skips `hedron_extras_experimental` unless you install
**`hedron[experimental-ui]`** (honesty/pin signal — the extra itself does not block imports)
and set ``HEDRON_EXPERIMENTAL_UI=1`` or explicitly enable the experimental plugin. They are
**not** part of the curated `hedron[extras]` product UI.

## Install

```bash
pip install "hedron[extras]>=0.40.0,<0.41"
# or
pip install "hedron-extras>=0.40.0,<0.41"
# feature-scoped:
pip install "hedron-extras[data_explorer]>=0.40.0,<0.41"
# experimental UI (requires an explicit opt-in):
pip install "hedron[experimental-ui]>=0.40.0,<0.41"
# then set HEDRON_EXPERIMENTAL_UI=1 or enable plugin hedron_extras_experimental
```

Absent extras add **no** core import, browser asset, startup, or transitive dependency
cost.

### Optional extras

| Extra | Notes |
|---|---|
| `json_editor` / `data_explorer` | Editor / explorer surfaces |
| `chart_workbench` | Pulls `hedron-data` + `hedron-charts` (Beta) |
| `image_tools` / `calendar` / `signature` / `typeahead` | UI tools |
| `sandbox` | Experimental browser-Python sandbox |
| `experimental-ui` | Explicit opt-in for CodeEditor / TerminalView / joystick / device surfaces. Runtime gates are the environment flag and plugin enablement; the extra does **not** block Python imports. |
| `all` | `hedron-data` + `hedron-charts` |

## When to use

- Specialized data-app interactions beyond core built-ins
- JSON editors, calendars, image tools, recipe cards

Do **not** install `hedron[extras]` expecting CodeEditor / TerminalView / joystick / device —
those require **`hedron[experimental-ui]`** and remain Experimental. Native desktop shell is a
separate docs recipe — see [Native desktop shell](../guides/native-desktop-shell.md).

## Quick start

```python
from hedron_extras import MetricCard

card = MetricCard(label="Active users", value="1,284", hint="+12% WoW")
```

Components register automatically when the package is installed.

```python
# Experimental UI (requires hedron[experimental-ui] + plugin enable / env):
from hedron_extras.experimental import CodeEditor, TerminalView
```

## Surfaces

| Area | Components |
|---|---|
| Workbenches | `JSONEditor`, `DataExplorer`, `ChartWorkbench`, `CallableActionForm` |
| Composition | `ChoiceCards`, `TreeView`, `Steps`, `SplitPane`, `FloatingAction`, `KeyboardShortcuts` |
| Editors | `Calendar`, `SignaturePad`, `Typeahead` |
| Image | `ImageCompare`, `ImageCrop`, `ImageRegionSelect`, `ImageAnnotations` |
| Recipes | `AvatarProfile`, `BadgeLink`, `MetricCard`, `TodoList` |
| Display | `LogConsole`, `TokenWeightedText`, `DiagramOutput` |
| Sandbox (Experimental) | `BrowserPythonSandbox` |
| Quarantined (`hedron[experimental-ui]`) | `CodeEditor`, `TerminalView`, `Joystick`, `DeviceBridge` |

## Errors and failure modes

| Condition | Behavior |
|---|---|
| Expecting experimental UI from `hedron[extras]` | Out of scope — use `hedron[experimental-ui]` |
| Expecting a full CodeMirror editor from `CodeEditor` | Out of scope — host stub only; see What’s ready |
| Specialty surface without policy | Fail closed — no silent privilege |
| Missing `data_explorer` / chart deps | Import / feature unavailable until extras installed |
| Expecting a second runtime | Out of scope — extras are plugins on `hedron-core` |

## Related docs

- [What’s ready](../guides/whats-ready.md)
- [Production archetype](../api/PRODUCTION_ARCHETYPE.md) (maintainer evidence and graduation criteria)
- [Plugins API](../api/PLUGINS.md)
- [Native desktop shell recipe](../guides/native-desktop-shell.md) (not this package’s runtime)

## Links

- [PyPI](https://pypi.org/project/hedron-extras/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-extras/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-extras)
