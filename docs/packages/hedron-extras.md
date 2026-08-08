# hedron-extras

Curated optional extras and analysis workbenches for Hedron.

**Package maturity:** Beta · **Train:** `0.22.0` · pin `>=0.22.0,<0.23`  
**Flagship extra:** `hedron[extras]` · **Import:** `hedron_extras`  
**Plugin:** registers via `hedron.plugins` — not a second component runtime

Composition / workbench surfaces are Beta. Specialty surfaces (`TerminalView`,
joystick / device bridges, browser-Python sandbox) are **Experimental** and fail
closed without explicit policy.

## Install

```bash
pip install "hedron[extras]>=0.22.0,<0.23"
# or
pip install "hedron-extras>=0.22.0,<0.23"
# feature-scoped:
pip install "hedron-extras[code_editor,data_explorer]>=0.22.0,<0.23"
```

Absent extras add **no** core import, browser asset, startup, or transitive dependency
cost.

### Optional extras

| Extra | Notes |
|---|---|
| `code_editor` / `json_editor` | Editor surfaces — **`CodeEditor` is a CSP-safe host stub** (no pinned CodeMirror 6); `JSONEditor` is the fuller editor |
| `data_explorer` | Pulls `hedron-data` |
| `chart_workbench` | Pulls `hedron-data` + `hedron-charts` (Alpha) |
| `image_tools` / `calendar` / `signature` / `typeahead` | UI tools |
| `sandbox` / `terminal` / `joystick` | Experimental specialty surfaces |
| `all` | `hedron-data` + `hedron-charts` |

## When to use

- Specialized data-app interactions beyond core built-ins
- JSON editors, calendars, image tools, recipe cards

Do **not** treat `CodeEditor` as a full IDE widget — it is a **host stub** (Experimental;
see [What’s ready](../guides/whats-ready.md)). Do **not** treat specialty bridges
(`TerminalView`, joystick, device, sandbox) as Supported production defaults. Native
desktop shell is a separate docs recipe — see
[Native desktop shell](../guides/native-desktop-shell.md).

## Quick start

```python
from hedron_extras import MetricCard

card = MetricCard(label="Active users", value="1,284", hint="+12% WoW")
```

Components register automatically when the package is installed.

## Surfaces

| Area | Components |
|---|---|
| Workbenches | `JSONEditor`, `DataExplorer`, `ChartWorkbench`, `CallableActionForm` |
| Editors (stub) | `CodeEditor` — **CSP-safe host stub** (no CodeMirror 6 bundle); Experimental |
| Composition | `ChoiceCards`, `TreeView`, `Steps`, `SplitPane`, `FloatingAction`, `KeyboardShortcuts` |
| Editors | `Calendar`, `SignaturePad`, `Typeahead` |
| Image | `ImageCompare`, `ImageCrop`, `ImageRegionSelect`, `ImageAnnotations` |
| Recipes | `AvatarProfile`, `BadgeLink`, `MetricCard`, `TodoList` |
| Display | `LogConsole`, `TokenWeightedText`, `DiagramOutput` |
| Specialty (Experimental) | `TerminalView`, `Joystick`, `DeviceBridge`, `BrowserPythonSandbox` |

## Errors and failure modes

| Condition | Behavior |
|---|---|
| Expecting a full CodeMirror editor from `CodeEditor` | Out of scope — host stub only; see What’s ready |
| Specialty surface without policy | Fail closed — no silent privilege |
| Missing `data_explorer` / chart deps | Import / feature unavailable until extras installed |
| Expecting a second runtime | Out of scope — extras are plugins on `hedron-core` |

## Related docs

- [What’s ready](../guides/whats-ready.md)
- [Plugins API](../api/PLUGINS.md)
- [Native desktop shell recipe](../guides/native-desktop-shell.md) (not this package’s runtime)

## Links

- [PyPI](https://pypi.org/project/hedron-extras/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-extras/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-extras)
