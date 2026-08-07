# Security

Hedron treats escaping, CSRF, cache policy, and redirects as framework boundaries—not
optional middleware you remember later.

## Profiles

Pass `security=` to `Hedron` (or build a `SecurityPolicy`):

| Profile | CSRF | CSP (summary) | Explorer default | Notes |
|---|---|---|---|---|
| `development` | on | relaxed / unset | may mount | Local iteration only |
| `standard` | on | self + limited inline styles | off | Default for apps |
| `strict` | on | no `unsafe-inline` styles | off | Requires explicit `session_secret` |

```python
from hedron import Hedron

app = Hedron(
    title="Ops",
    security="standard",
    session_secret="load-from-secret-store",
    explorer="off",
)
```

See [Security types](../api/SECURITY_TYPES.md) for boundary types (`SafeUrl`, …).

## HDJ templates

HDJ files are trusted application source, like Python modules and JavaScript files. They may use
native HTML, CSS, JavaScript, Web Components, Jinja, and HTMX directly. Strict HDJ mode protects
dynamic values and component/view contracts; it does not redefine HTML.

Before serving a template, HDJ compares its capability report with the active security and asset
policy. Inline script/style, HTMX eval or response-script processing, remote origins, and
extensions must be allowed deliberately. Hedron never adds `unsafe-inline`, `unsafe-eval`, remote
origins, or a nonce automatically. Prefer registered modules/styles under strict CSP. Template
authors remain trusted; do not load tenant, CMS, prompt, upload, or database text as executable HDJ.

## CSRF

When CSRF is enabled (all built-in FastAPI profiles):

- Safe GET responses may set the CSRF cookie (`hedron_csrf` by default).
- Unsafe methods on page/component/action routes (including `include_component` when POST
  is declared) require a matching `X-CSRF-Token` header or `csrf_token` form field.
- On HTTPS, the CSRF cookie is marked `Secure`.

Flask adapter: `hedron_route` and `HedronFlask.respond` validate the same double-submit cookie
for unsafe methods (auto cookie issuance on safe GETs remains on by default).

Django adapter: `CsrfViewMiddleware` remains authoritative. Safe GETs through
`HedronDjango.respond` / `hedron_view` call `get_token` so the CSRF cookie is seeded. For
portable clients that send `X-CSRF-Token`, set `CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"`.
Form posts may use `csrfmiddlewaretoken` or `csrf_token`.

Seed the cookie with a GET against a real page route, then POST an action or component
route that requires CSRF. Example using the
[HTMX interactions](htmx-interactions.md) sample (`/` seeds; `/status` is GET-only—add a
POST action for writes):

### Try it (simulated)

=== "Demo"

    POST with CSRF succeeds; missing token → 403. Docs simulation.

    <!-- hedron-sim:csrf-guard -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from fastapi import Request

    from hedron import Hedron, Page, Stack, Text, csrf_token_for_request, html

    app = Hedron(
        title="CSRF demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )


    def _csrf(request: Request) -> str:
        return csrf_token_for_request(request, request.app.state.hedron_security)


    @app.page("/")
    def home(request: Request) -> Page:
        token = _csrf(request)
        return Page(
            Stack(
                Text("GET seeds hedron_csrf"),
                html.form(
                    html.input(type="hidden", name="csrf_token", value=token),
                    html.button("POST with CSRF", type="submit"),
                    action="/do",
                    method="post",
                ),
                html.form(
                    html.button("POST without CSRF", type="submit"),
                    action="/do",
                    method="post",
                ),
            ),
            title="CSRF",
        )


    @app.action("/do", method="POST")
    def do_action() -> Page:
        return Page(Text("POST ok"), title="Done")
    ```

```python
from hedron import Hedron, Page, Text

app = Hedron(title="CSRF demo", security="standard", session_secret="replace-me")


@app.page("/")
def home() -> Page:
    return Page(Text("GET seeds hedron_csrf"), title="Home")


@app.action("/do")
def do_action() -> Page:
    return Page(Text("POST ok"), title="Done")
```

```bash
# Terminal: uv run uvicorn app:app --reload
curl -c jar -b jar http://127.0.0.1:8000/
TOKEN=$(grep hedron_csrf jar | awk '{print $NF}')
curl -b jar -H "X-CSRF-Token: $TOKEN" -X POST http://127.0.0.1:8000/do
```

Without the header, expect **403**. Safe GETs alone do not require the token.

## Redirects and HTMX headers

- `redirect_local("/path")` accepts only local paths (rejects `//…` and `\` open-redirect forms).
- `redirect_external(...)` fails closed unless the policy sets `allow_external_redirects=True`.
- Approved HTMX headers (`HX-Redirect`, `HX-Push-Url`, …) must use local paths.
- HTMX target and reselect values must use Hedron's safe selector subset.
- Route `fragment_regions` allowlists reject an unauthorized `HX-Target` with `403`.
- `InteractionResult.headers` cannot introduce arbitrary response headers; approved names
  are re-validated through the same URL and selector checks as typed fields.

Use `InteractionResult(redirect=..., retarget=..., cache=...)` instead of constructing
raw `HX-*` headers when a typed field exists. See the
[HTMX interaction guide](htmx-interactions.md).

## Explorer modes

| Mode | Behavior |
|---|---|
| `off` | Not mounted |
| `development` | Mounted for local use; **forced off in production** |
| `secured` | Mounted behind `explorer_dependencies` / auth gate |

Prefer `explorer="off"` in scaffolds and production. Install `hedron[dev]` when you need
Explorer, then open **`/hedron-explorer/`** (trailing slash) on the running app.

## Markdown sanitize and chart callbacks

- `Markdown` renders through `TrustedHtml.nh3` — install `hedron[markdown]` /
  `hedron[sanitize]`. Do not pass unsanitized HTML through `html.raw` without an explicit
  trust boundary (`TrustedHtml.reviewed` or `TrustedHtml.nh3`).
- Chart adapters reject raw JavaScript callbacks and unapproved remote CDN assets.
  Browser runtimes are pinned and served locally under Hedron static paths.

See [Content](../api/CONTENT.md), [Charts](../api/CHART.md), and
[Security types](../api/SECURITY_TYPES.md).

## See also

- [Deployment](deployment.md)
- [Troubleshooting](troubleshooting.md)
- [Configuration](../CONFIGURATION.md)
