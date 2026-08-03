# hedron

FastAPI-native typed component framework for HTML and HTMX (`0.2.0`).

Builds on framework-neutral `hedron-core` with pages, addressable components,
typed actions, CSRF-aware forms, OpenAPI `text/html` metadata, and a thin
`Hedron()` application facade.

## Install

```bash
pip install hedron
# or
uv add hedron
```

Development Explorer preview:

```bash
pip install "hedron[dev]"
```

Requires Python 3.12, 3.13, or 3.14.

## Quick start

```python
from hedron import Hedron, Page, Text

app = Hedron(title="Demo", security="standard")


@app.page("/")
def home() -> Page:
    return Page(Text("Hello, Hedron"), title="Demo")
```

## License

MIT. See [LICENSE](LICENSE).
