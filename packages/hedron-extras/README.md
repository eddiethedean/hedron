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

**Package maturity:** Beta · **Train:** `0.20.0` (Published) · pin `>=0.20.0,<0.21`

Specialty surfaces (`TerminalView`, joystick/device bridges, browser-Python
sandbox) are **Experimental** and fail closed without explicit policy — see
[What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).

## Install

```bash
pip install "hedron[extras]>=0.20.0,<0.21"
# or
pip install "hedron-extras>=0.20.0,<0.21"
# feature-scoped:
pip install "hedron-extras[code_editor,data_explorer]>=0.20.0,<0.21"
```

Requires Python 3.11–3.14 and `hedron-core`.

### Optional extras

| Extra | Notes |
|---|---|
| `code_editor` / `json_editor` | Editor workbenches |
| `data_explorer` | Pulls `hedron-data` |
| `chart_workbench` | Pulls `hedron-data` + `hedron-charts` (Alpha) |
| `image_tools` / `calendar` / `signature` / `typeahead` | UI tools |
| `sandbox` / `terminal` / `joystick` | Experimental specialty surfaces |
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
| Workbenches | `CodeEditor`, `JSONEditor`, `DataExplorer`, `ChartWorkbench` |
| Composition | `ChoiceCards`, `TreeView`, `Steps`, `SplitPane`, `FloatingAction` |
| Editors | `Calendar`, `SignaturePad`, `Typeahead` |
| Image | `ImageCompare`, `ImageCrop`, `ImageRegionSelect`, `ImageAnnotations` |
| Recipes | `AvatarProfile`, `BadgeLink`, `MetricCard`, `TodoList` |
| Specialty | `TerminalView`, `Joystick`, `DeviceBridge`, `BrowserPythonSandbox` |

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

MIT. See [LICENSE](LICENSE).
