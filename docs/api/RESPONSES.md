---
status: shipped
---

# Response APIs


!!! note "Stability (0.8 compatibility baseline)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Shipped in `0.6.0`

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

They also inject a declarative HTMX 2 configuration that disables eval, response script tags, and
HTMX's inline indicator style; keeps requests same-origin; disables `HX-Request` on history cache
misses; and enables native form-validity reporting. If the page already contains a
`<meta name="htmx-config">` element, Hedron leaves it untouched and the application owns the full
configuration.

All Hedron responses use contextual escaping, registered assets, declared headers, and framework-managed background tasks. Response helpers do not weaken cache, CSP, CSRF, or redirect policy. Adapter `extra_headers` are merged through the same validation path as `InteractionResult.headers` (no raw overwrite of approved `HX-*` URL/selector fields; no `Cache-Control: public`).

Focused streaming uses `StreamingComponentResponse` / `stream_chunked_list` /
`stream_document` / `stream_tokens` (RFC-0032). Ordinary `Component.render()` remains
non-streaming. Applications that need a lower-level escape hatch may still use the host
framework's explicit `StreamingResponse`.

## `InteractionResult`

Handlers may return `InteractionResult` for typed primary content, out-of-band (OOB) updates,
status, history, and cache/`Vary` hints. HTML and `HX-*` headers remain visible via
`interaction_headers` / `approved_headers`.

```python
from hedron import Hedron, InteractionResult, OobUpdate, Text

app = Hedron(title="Demo", security="standard", session_secret="replace-me")


@app.page("/panel")
def panel() -> InteractionResult:
    return InteractionResult(
        content=Text("Primary panel"),
        oob=(OobUpdate(Text("Sidebar note"), element_id="sidebar-note"),),
        trigger="panelUpdated",
        history="push",
        cache="vary-htmx",
        explanation="Refresh primary panel and announce sidebar note",
    )
```

### Fields

| Field | Role |
|---|---|
| `content` | Primary swap body (`NodeLike` / `Component` / `None`) |
| `status_code` | HTTP status (default `200`) |
| `target` / `swap` / `retarget` / `reswap` / `reselect` | HTMX target/swap overrides |
| `oob` | Tuple of `OobUpdate(content, swap=..., select=..., element_id=...)` |
| `trigger` / `trigger_after_swap` / `trigger_after_settle` | `HX-Trigger*` payloads |
| `push_url` / `replace_url` / `history` | History (`push` / `replace` / `none`) |
| `redirect` / `refresh` / `location` | Local redirect, full refresh, or `HX-Location` |
| `cache` | `"private"` / `"no-store"` / `"vary-htmx"` (default) |
| `region_id` / `policy` | Declared fragment region + `InteractionPolicy` |
| `headers` | Approved extra response headers; names and values are re-validated |
| `explanation` | Diagnostics / Explorer trace text |

When `cache="vary-htmx"`, responses include `Vary: HX-Request, HX-History-Restore-Request`
(and `HX-Target` when `policy.vary_on_target` is set).

See [Interaction](INTERACTION.md) for `HtmxRequest`, policies, and form sync attrs.
For a complete endpoint and test, follow
[Build an HTMX interaction](../guides/htmx-interactions.md).

## Validation errors: HTMX HTML vs JSON

FastAPI request-validation failures use semantic **422** handling:

- HTMX requests (`HX-Request: true`) receive an **HTML fragment** suitable for swap/retarget
  (accessible validation feedback), not a JSON error body.
- Ordinary API clients continue to receive FastAPI's JSON validation payload.

```python
# Browser HTMX form POST missing a required field → 422 text/html fragment
# curl -H "Accept: application/json" without HX-Request → 422 application/json
```

Default status policies for 202, 204, 401, 403, 409, 422, 429, and 500 are available through
`status_policy_for` — see [Interaction](INTERACTION.md).
