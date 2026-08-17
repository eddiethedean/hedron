# hedron-notebook

Server-side notebook preview helper for Hedron.

**Package maturity:** Beta (tooling-grade; localhost-only) (`0.1.x`) · pin `>=0.1.0,<0.2`  
**Flagship extra:** `hedron[notebook]` · **Import:** `hedron_notebook`  
**Not** a Supported production server. The Supported preview API is **localhost-only**.

Distinct from the browser-Python / JupyterLite sandbox in
[`hedron-extras`](hedron-extras.md) (`BrowserPythonSandbox`).

## Install

```bash
pip install "hedron[notebook]>=0.46.0,<0.47"
# or
pip install "hedron-notebook>=0.1.0,<0.2"
```

Optional server extra:

```bash
pip install "hedron-notebook[server]>=0.1.0,<0.2"   # pulls uvicorn
```

## When to use

- Authoring notebooks that need an inline iframe or external-link preview of a
  normal Hedron ASGI app

`start_preview` **refuses** non-loopback hosts (`ValueError`). Remote or public
serving is excluded from the Supported API.

## Jupyter compatibility matrix

| Frontend | Status |
|---|---|
| JupyterLab 4.x | Supported for localhost preview embedding |
| Jupyter Notebook 7.x | Supported for localhost preview embedding |
| Classic Notebook &lt; 7 | Unsupported — use JupyterLab / Notebook 7 |
| Hosted JupyterHub public bind | Refused by Supported API |

Warning/error UX: missing/wrong preview tokens return HTTP 401 / WS close 4401;
non-loopback bind raises before the server starts.

## Quick start

```python
from hedron import Hedron, Page, Text
from hedron_notebook import start_preview

app = Hedron(
    title="Notebook demo",
    security="standard",
    session_secret="dev-only",
    explorer="off",
)


@app.page("/")
def home() -> Page:
    return Page(Text("Hello from a notebook preview"), title="Demo")


preview = start_preview(app)
print(preview.url)
# In a Jupyter cell, display HTML from preview.iframe_html()
preview.shutdown()
```

## Surfaces

| Symbol | Role |
|---|---|
| `start_preview(app)` | Start a local preview server for an ASGI app |
| `NotebookPreview` | Handle with `.url`, `.iframe_html()`, `.shutdown()` |

## Errors and failure modes

| Condition | Behavior |
|---|---|
| Public / hosted bind | Explicit warning — not Supported production |
| Treating as JupyterLite sandbox | Wrong package — see `BrowserPythonSandbox` in extras |
| Missing uvicorn when using `[server]` paths | Install `hedron-notebook[server]` |

## Related docs

- [What’s ready](../guides/whats-ready.md)
- [Stability](../api/STABILITY.md)
- Contrast: [hedron-extras](hedron-extras.md) specialty sandbox

## Links

- [PyPI](https://pypi.org/project/hedron-notebook/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-notebook/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-notebook)
