# Response APIs

**Status:** Accepted

## `HTML(component)`

Wraps a component return when using ordinary `FastAPI` routing. It renders using the active Hedron integration and makes the HTML intent explicit.

```python
@app.get("/card", **hedron_response(UserCard))
def card():
    return HTML(UserCard(...))
```

## Response classes

- `ComponentResponse`: validated component HTML.
- `PageResponse`: complete document behavior.
- `FragmentResponse`: explicit fragment behavior.
- `FileComponentResponse`: file/download results produced through safe source contracts.

`hedron_response(ComponentType)` supplies accurate `text/html` OpenAPI metadata for plain FastAPI routes. Explicit framework `Response` objects bypass component conversion.

All Hedron responses use contextual escaping, registered assets, declared headers, and framework-managed background tasks. Response helpers do not weaken cache, CSP, CSRF, or redirect policy.

General component streaming is outside the 1.0 contract. Applications that need a streaming escape hatch use the framework's explicit `StreamingResponse`; Hedron does not expose a public `StreamingComponentResponse` in the 0.x–1.0 API.
