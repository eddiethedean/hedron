# OpenAPI and HTML routes

Hedron does not invent a separate schema language. It rides FastAPI’s OpenAPI document
and marks HTML/component routes explicitly.

## What appears in `/docs`

| Route kind | Typical OpenAPI behavior |
|---|---|
| `@app.page` | Included by default (`include_in_schema=True`); response `text/html` |
| `@app.action` | Included by default |
| `@app.view` | **Excluded** by default (`include_in_schema=False`) — internal HTMX resources |
| Ordinary FastAPI JSON routes | Untouched |

Override with `include_in_schema=True/False` on the decorator when you want a fragment
in the schema or a page omitted.

## Mix HTML and JSON deliberately

One application can expose a typed JSON resource, a private HTMX view, and a documented HTML
page without maintaining separate routers:

```python
from pydantic import BaseModel

from hedron import Hedron, Stack, Text

app = Hedron(title="Service console", security="standard")


class ServiceStatus(BaseModel):
    state: str
    version: str


@app.get("/api/status", response_model=ServiceStatus)
def api_status() -> ServiceStatus:
    return ServiceStatus(state="ready", version="1.0.0")


@app.view("/status", include_in_schema=False)
def status_view():
    return Text("Service ready")


@app.page("/", include_in_schema=True)
def home():
    return Stack(
        Text("Service console"),
        status_view(),
        status_view.refresh_button("Refresh status"),
    )
```

FastAPI documents `/api/status` with its JSON response model and `/` as an HTML route.
The internal `/status` view stays out of `/docs` while remaining addressable by HTMX.

## Practical tips

1. Keep JSON APIs and HTML pages on the same FastAPI app — Hedron only changes HTML
   returns and metadata.
2. Prefer documenting public **pages** and **actions**; leave HTMX fragment routes out of
   the schema unless partners need them.
3. Production generation strips source paths, private Explorer URLs, and sensitive
   examples (`x-hedron-*` extensions are sanitized).

## See also

[Hedron](../api/HEDRON.md) · [Router](../api/ROUTER.md) · [Plain FastAPI](plain-fastapi.md)
