# hedron-extras

[![PyPI](https://img.shields.io/pypi/v/hedron-extras.svg)](https://pypi.org/project/hedron-extras/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-extras.svg)](https://pypi.org/project/hedron-extras/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Curated optional extras and analysis workbenches for Hedron.

Specialized data-app interactions built on public Hedron plugin contracts — not
a second component runtime. Install as `hedron-extras` or via `hedron[extras]`.
Absent extras add no core import, browser asset, startup, or transitive
dependency cost.

**Package maturity:** Beta · **Train:** `0.33.x` (last published `0.33.0`) · pin `>=0.33.0,<0.34`

`CodeEditor`, `TerminalView`, and joystick/device bridges require the separate
**`hedron[experimental-ui]`** opt-in (import `hedron_extras.experimental`) and are not
part of the supported product UI under `hedron[extras]`. See
[What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).

## Install

```bash
pip install "hedron[extras]>=0.33.0,<0.34"
# or
pip install "hedron-extras>=0.33.0,<0.34"
# experimental UI (requires an explicit opt-in):
pip install "hedron[experimental-ui]>=0.33.0,<0.34"
```

Requires Python 3.11–3.14 and `hedron-core`.

### Optional extras

| Extra | Notes |
|---|---|
| `json_editor` / `data_explorer` | Editor / explorer workbenches |
| `chart_workbench` | Pulls `hedron-data` + `hedron-charts` (Beta) |
| `image_tools` / `calendar` / `signature` / `typeahead` | UI tools |
| `sandbox` | Experimental browser-Python sandbox |
| `experimental-ui` | Quarantined CodeEditor / TerminalView / joystick / device |
| `all` | `hedron-data` + `hedron-charts` |

## Quick start

```python
from hedron_extras import MetricCard

card = MetricCard(label="Active users", value="1,284", hint="+12% WoW")
```

Components register automatically via the `hedron.plugins` entry point when the
package is installed.

## Component highlights

| Area | Components |
|---|---|
| Workbenches | `JSONEditor`, `DataExplorer`, `ChartWorkbench` |
| Composition | `ChoiceCards`, `TreeView`, `Steps`, `SplitPane`, `FloatingAction` |
| Editors | `Calendar`, `SignaturePad`, `Typeahead` |
| Image | `ImageCompare`, `ImageCrop`, `ImageRegionSelect`, `ImageAnnotations` |
| Recipes | `AvatarProfile`, `BadgeLink`, `MetricCard`, `TodoList` |
| Quarantined (`hedron[experimental-ui]`) | `CodeEditor`, `TerminalView`, `Joystick`, `DeviceBridge` |

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-extras/)
- [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/)
- [Plugins API](https://hedron.readthedocs.io/en/latest/api/PLUGINS/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-extras/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-extras)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron-data`](https://pypi.org/project/hedron-data/) ·
  [`hedron`](https://pypi.org/project/hedron/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
