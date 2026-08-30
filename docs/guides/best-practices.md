# Best practices

Practical defaults for production Hedron apps from the 0.8 compatibility baseline onward.

## A production-minded baseline

Keep the application constructor, page shell, and replaceable views explicit. Read secrets
from the environment and let authenticated responses select a private cache policy:

```python
import os

from fastapi import Request

from hedron import Hedron, InteractionResult, Stack, Text

app = Hedron(
    title="Account console",
    security="standard",
    explorer="off",
    session_secret=os.environ["HEDRON_SESSION_SECRET"],
)


@app.view("/account/status")
def account_status(request: Request) -> InteractionResult:
    signed_in = bool(request.session.get("user_id"))
    return InteractionResult(
        content=Text("Signed in" if signed_in else "Signed out"),
        cache="private" if signed_in else "vary-htmx",
    )


@app.page("/")
def home():
    return Stack(
        Text("Account console"),
        account_status(),
        account_status.refresh_button("Refresh status"),
    )
```

This keeps one application authority: the session remains server-owned, the view owns its
cache decision, and the page composes the resulting handle without hand-writing HTMX attributes.

## Pages vs fragments

- Use `@app.page` (or full `Page`) for document shells and first paint.
- Use `@app.view` routes for replaceable views and `@app.action` for HTMX mutations into declared regions.
- Declare `FragmentRegion` allowlists when OOB or retarget is in play—do not authorize one
  `#id` and emit `hx-swap-oob` for another.

## CSRF and secrets

- Issue CSRF on safe GETs; send `X-CSRF-Token` (or form field) on unsafe methods.
- Flask: enforced on `hedron_route` / `HedronFlask.respond`.
- Django: use middleware; align `CSRF_HEADER_NAME` for portable headers.
- Never commit real `session_secret` / `SECRET_KEY` values; rotate per environment.

## URLs and redirects

- Pass navigation/asset URLs through `SafeUrl.parse(..., purpose=...)`.
- Prefer `redirect_local` / interaction redirects; avoid open redirects via raw headers.
- Adapter `extra_headers` cannot overwrite validated `HX-*` URL/selector fields or weaken
  `Cache-Control` to `public`.

## Caching

- Prefer `cache="private"` or `no-store` for authenticated fragments.
- Use `vary-htmx` when responses differ by `HX-Request` / target.
- Include tenant or user in cache keys when responses are tenant-scoped.

## Templates

- Prefer Python components for reusable behavior and authorization. Install `hedron-jinja`
  when trusted authors need standards-first control over HTML, CSS, JavaScript, Jinja, and HTMX;
  bind every callable component alias explicitly and keep dynamic trust crossings visible. HDN is
  not available on the 0.9+ train.
- Do not put secrets or untrusted HTML in templates—use `TrustedHtml` at trust boundaries.

## Adapters

- Install `hedron-flask` / `hedron-django` separately; they never pull FastAPI.
- Prefer `hedron_django.forms` and `DjangoQuerySetDataSource` over ad-hoc bridges.
  Capture UI (`CameraCapture`, …) is Supported on the current train — see
  [What's ready](whats-ready.md).
- For mutations on Flask/Django: CSRF + forms bridge (or host forms) and
  [polling](live-interaction.md) for job status.

## Testing

- Unit-render with `render(...)` for components.
- Use TestClient / Flask/Django clients for CSRF and fragment headers.
- Opt into browser suite (`HEDRON_BROWSER=1`) for critical HTMX flows.

## Anti-patterns

| Avoid | Prefer |
|---|---|
| Full-page HTMX swaps for every click | Declared `FragmentRegion` updates |
| `Cache-Control: public` on authenticated HTML | `private` / `no-store` / `vary-htmx` |
| Explorer (`development`) in production | `explorer="off"` or `secured` with real auth |
| Unbounded `Auto` on huge objects | Bound depth / explicit tables |
| Raw `HX-*` headers that bypass validated fields | `InteractionResult` fields |
| Assuming SSE/WS survive every proxy | Polling fallback + proxy buffering off |
| One in-memory job backend across workers | Sticky sessions or shared `JobBackend` |

See also [Security](security.md), [HTMX interactions](htmx-interactions.md),
[Deployment](deployment.md), [Enterprise diligence](enterprise-diligence.md).

## Day-one defaults

1. Prefer the canonical `@app.page` / `@app.view` / `@app.action` roles over hand-wired
   lower-level routes unless you need
   full `Page` control.
2. Pin `hedron>=1.0.0,<1.1` (and matching host packages) in every environment.
3. Keep Explorer off and `session_secret` from the environment in production.
4. Declare HTMX regions; undeclared targets fail closed — treat 403s as configuration bugs.
5. Prefer polling for job UIs until you have proxy/load evidence for SSE/WebSocket.

See also [Ship](ship.md), [Security](security.md), and [What’s ready](whats-ready.md).
