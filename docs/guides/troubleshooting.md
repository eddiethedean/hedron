# Troubleshooting

## Wrong or unexpected version

**Symptom:** Features in the docs are missing from your install, or verify text does not match.

**Fix:** Check `python -c "import hedron; print(hedron.__version__)"`. Upgrade with
`pip install -U "hedron>=0.10.0"` (or `uv add "hedron>=0.10.0"`). The published train is
**0.10.0**—see [STATUS](../STATUS.md). If docs describe a feature from an unreleased next-phase
checkout that is missing on your PyPI install, upgrade or use a git checkout of that work.

## CSRF 403 on POST (FastAPI / Flask)

**Cause:** Missing or mismatched CSRF token/cookie.

**Fix:** Perform a safe GET first to receive `hedron_csrf`, then send `X-CSRF-Token`
(or form field `csrf_token`) with the same value. On HTTPS, ensure the client stores
`Secure` cookies. See [Security](security.md).

## CSRF 403 on Django POST

**Cause:** Django `CsrfViewMiddleware` rejected the token, or the header name does not match settings.

**Fix:** Seed the cookie with a safe GET through `HedronDjango.respond` / `hedron_view`.
Send Django's `X-CSRFToken` **or** set `CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"` and send
Hedron's portable `X-CSRF-Token`. Form fields: `csrfmiddlewaretoken` or `csrf_token`.
See [Django quickstart](../getting-started/django.md).

## Explorer 404 or missing in production

**Cause:** `explorer="off"`, missing `hedron[dev]`, or production forced development mode off.

**Fix:** Install `hedron[dev]` for local Explorer; use `explorer="development"` only
locally; open **`http://127.0.0.1:8000/hedron-explorer/`** (trailing slash); use `secured`
with auth in rare cases; keep production off.

## `hedron new` installs an old train

**Cause:** Scaffold from a pre-0.10 CLI wrote `hedron>=0.4.0`.

**Fix:** Edit `pyproject.toml` to `hedron>=0.10.0` and `uvicorn[standard]>=0.30`, then
reinstall. Current `hedron new` scaffolds the 0.10 floor automatically.

## SSE / WebSocket / preload not working

**Cause:** Using Flask/Django expecting FastAPI live helpers; proxy buffering SSE; preload
left disabled; Origin rejected.

**Fix:** Live helpers (`job_status_sse_response`, `accept_page_session_channel`,
`NavigationPreloadPolicy`) are FastAPI-flagship Supported surfaces—use polling on adapters.
Disable response buffering for `text/event-stream`. Enable preload only with an explicit
`NavigationPreloadPolicy(enabled=True)`. See [live interaction](live-interaction.md).

## Production startup: missing manifest (`HED-BUILD-0003`)

**Cause:** `HEDRON_ENV=production` / `production=True` without `hedron build` output.

**Fix:** Run `hedron build` and set `HEDRON_BUILD_DIR` if the manifest is not at
`.hedron/build/manifest.json`. Quickstarts do not create a production manifest—build before
setting production mode.

## Cannot import `Auto` / `DataTable` / chart helpers

**Cause:** `Auto` is core (`from hedron import Auto`). `DataTable` / `DataEditor` and
charts need optional extras—not a planned feature gap.

**Fix:**

```bash
# Auto needs no extra
pip install "hedron[data]"      # DataTable, DataEditor
pip install "hedron[charts]"    # LineChart / adapters
pip install "hedron-charts[plotly]"   # example backend
```

See [Installation](../getting-started/installation.md) and
[charts and HTMX](charts-and-htmx.md).

## `NodeLike` import error from `hedron`

**Cause:** `NodeLike` lives in `hedron_core`.

**Fix:** `from hedron_core import NodeLike` (or avoid naming it and return built-ins).

## Mounted app / reverse proxy broken URLs

**Cause:** ASGI `root_path` or WSGI `SCRIPT_NAME` not applied; absolute reverse URLs prefixed wrongly.

**Fix:** Configure your proxy/`root_path` correctly. Flask reverse forces path-only URLs
before applying prefixes—see adapter tests and [Architecture](../ARCHITECTURE.md).

## Redis / jobs optional

**Cause:** Compose examples set `HEDRON_REDIS_URL` for optional job backends.

**Fix:** Redis is not required for basic pages. Omit the variable unless you configure a
job backend that needs it. See [CONFIGURATION](../CONFIGURATION.md).

## Flask async view RuntimeError

**Cause:** Flask async views need the optional async extra (`greenlet`).

**Fix:** Install Flask's async extra, or keep sync views (Supported sync-only path).

## Still stuck?

Open a GitHub issue with Hedron version, command/traceback, host framework (FastAPI /
Flask / Django), and whether `HEDRON_ENV` is set. Check [FAQ](faq.md),
[Error codes](error-codes.md), and [Support](support.md) first. Report vulnerabilities
privately via [SECURITY.md](../SECURITY.md).

## Auth 401 forever

**Cause:** A `require_user` dependency reads `session["username"]`, but no login route
ever sets it.

**Fix:** Follow [Authentication](authentication.md) (login/logout with CSRF), or use the
reference app’s HTTP Basic pattern.

## HTMX form `type: ignore` / attrs typing

**Cause:** Spreading HTMX attrs onto `Form(...)` may need a type ignore in strict checkers.

**Fix:** Prefer the [minimal form](minimal-form.md) HTML form path first, or see the
typed attrs pattern in [Forms and actions](forms-and-actions.md).
