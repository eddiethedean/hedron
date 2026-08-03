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

See [Security types](../api/SECURITY_TYPES.md) for boundary types (`SafeURL`, …).

## CSRF

When CSRF is enabled (all built-in profiles):

- Safe GET responses may set the CSRF cookie (`hedron_csrf` by default).
- Unsafe methods on page/component/action routes (including `include_component` when POST
  is declared) require a matching `X-CSRF-Token` header or `csrf_token` form field.
- On HTTPS, the CSRF cookie is marked `Secure`.

Seed the cookie with a GET, then post with the header:

```bash
curl -c jar -b jar http://127.0.0.1:8000/seed
TOKEN=$(grep hedron_csrf jar | awk '{print $NF}')
curl -b jar -H "X-CSRF-Token: $TOKEN" -X POST http://127.0.0.1:8000/do
```

## Redirects and HTMX headers

- `redirect_local("/path")` accepts only local paths (rejects `//…` and `\` open-redirect forms).
- `redirect_external(...)` fails closed unless the policy sets `allow_external_redirects=True`.
- Approved HTMX headers (`HX-Redirect`, `HX-Push-Url`, …) must use local paths.

## Explorer modes

| Mode | Behavior |
|---|---|
| `off` | Not mounted |
| `development` | Mounted for local use; **forced off in production** |
| `secured` | Mounted behind `explorer_dependencies` / auth gate |

Prefer `explorer="off"` in scaffolds and production. Install `hedron[dev]` when you need
Explorer.

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
