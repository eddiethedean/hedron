# hedron

FastAPI-native typed component framework for HTML and HTMX (`0.2.0`).

Builds on framework-neutral `hedron-core` with pages, addressable components,
typed actions, CSRF-aware forms, OpenAPI `text/html` metadata, interaction
built-ins (`Lazy`, `Poll`, `Pagination`, …), and a thin `Hedron()` application
facade.

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

Requires Python 3.11, 3.12, 3.13, or 3.14.

## Quick start

```python
from hedron import Hedron, Page, Text

app = Hedron(
    title="Demo",
    security="standard",
    session_secret="replace-me",
    explorer="off",
)


@app.page("/")
def home() -> Page:
    return Page(Text("Hello, Hedron"), title="Demo")
```

Plain FastAPI without the `Hedron` subclass:

```python
from fastapi import FastAPI
from hedron import HTML, HedronRouter, Text, hedron_response, mount_hedron_static
from hedron.security.policy import SecurityPolicy

app = FastAPI()
app.state.hedron_security = SecurityPolicy.from_name("standard")
mount_hedron_static(app)
router = HedronRouter()


@router.get("/card", **hedron_response())
def card():
    return HTML(Text("plain"))


app.include_router(router)
```

CLI inspection (optionally load an app module first):

```bash
hedron --app myapp:app routes
hedron --app myapp:app components
hedron --app myapp:app preview home
```

## License

MIT. See [LICENSE](LICENSE).
