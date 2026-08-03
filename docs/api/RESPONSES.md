# Response APIs

**Status:** Accepted

## `HTML(component)`

Wraps a component return when using ordinary `FastAPI` / `HedronRouter` routing. On `HedronRoute`, `HTML(...)` and component returns are converted before FastAPI serializes the endpoint result.

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

## Response classes

- `ComponentResponse`: validated component HTML.
- `PageResponse`: complete document behavior.
- `FragmentResponse`: explicit fragment behavior.
- `FileComponentResponse`: file/download results produced through safe source contracts; filenames are sanitized for `Content-Disposition`.

`hedron_response(ComponentType)` supplies accurate `text/html` OpenAPI metadata for plain FastAPI routes. Explicit framework `Response` objects bypass component conversion.

Full-page responses inject the bundled HTMX script tag when the asset is mounted. Use `Hedron()` or `mount_hedron_static(app)` so `/hedron-static/htmx.min.js` resolves.

All Hedron responses use contextual escaping, registered assets, declared headers, and framework-managed background tasks. Response helpers do not weaken cache, CSP, CSRF, or redirect policy.

General component streaming is outside the 1.0 contract. Applications that need a streaming escape hatch use the framework's explicit `StreamingResponse`; Hedron does not expose a public `StreamingComponentResponse` in the 0.x–1.0 API.
