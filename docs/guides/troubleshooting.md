---
description: Diagnose Hedron installation, interpreter, CSRF, HTMX, asset, proxy, and production failures.
search:
  boost: 1.8
---

# Troubleshooting

## Failure gallery (top 5)

| Symptom | Typical stderr / response | Fix |
|---|---|---|
| `hedron: command not found` | `zsh: command not found: hedron` | `python -m hedron …` or [below](#hedron-command-not-found) |
| Wrong interpreter | `ModuleNotFoundError: No module named 'hedron'` | Activate venv; `pip install -e .` / `uv sync` |
| Port busy | `ERROR: [Errno 48] Address already in use` | `--port 8001` or stop the other process |
| CSRF 403 | HTTP **403** on POST | GET the form page first; FastAPI/Flask: `csrf_token`; Django: `csrfmiddlewaretoken` |
| HTMX 403 | HTTP **403** on fragment | Fix `HX-Target` to a declared region id/selector |

## `hedron: command not found`

**Cause:** The `hedron` console script is not on your shell PATH, or you installed into a
different Python than the one your shell uses.

**Always-works first:** call the module with the same interpreter you used for `pip`:

```bash
python -m hedron new my-hedron-app
python -m hedron check
```

**Other fixes:**

1. Re-open the terminal after install (PATH updates often need a new shell).
2. Prefer `uv tool install "hedron>=0.58.0,<0.59"` (or `pipx install "hedron>=0.58.0,<0.59"`) so the
   tool is on PATH, then run `hedron new …`.
3. Inside a scaffolded project, use the project environment: `uv run hedron check` (or
   activate `.venv` and run `hedron` / `python -m hedron`).
4. On Windows, add the install’s **Scripts** directory to PATH, or call the full path to
   `hedron.exe`.
5. Verify the package with the same interpreter as `uvicorn`:

   ```bash
   python -c "import hedron; print(hedron.__version__)"
   ```

   If that fails with `ModuleNotFoundError`, activate the correct venv and reinstall
   (`pip install -e .` / `uv sync`). See also [FAQ](faq.md#hedron-command-not-found).

## FastAPI version conflict on install

**Symptom:** `pip` / `uv` reports a resolver error, `ResolutionImpossible`, or an unexpected
FastAPI/Pydantic version after install.

**Cause:** Another package pins FastAPI/Pydantic outside Hedron’s **declared** range
(`fastapi>=0.141.1,<0.150`, `pydantic>=2.13.4,<2.15`), or you need the **CI-supported**
band for a known-good first app (`fastapi>=0.141.1,<0.142`, `pydantic>=2.13.4,<2.14`).
Declared ranges are wider than Supported — versions outside Supported can still install
but are not CI-proven.

**Fix:** Create a **clean virtual environment** for the Hedron app (do not reuse a shared
env that already pins an older FastAPI). Install only Hedron + uvicorn first
(`hedron>=0.58.0,<0.59`), then add other dependencies. For first apps, prefer staying
inside the Supported band. See [Compatibility](../COMPATIBILITY.md).

## Wrong interpreter or ModuleNotFoundError for hedron

**Cause:** `uvicorn` or `python` is from a different environment than the one where you
installed Hedron (global vs venv, or forgotten `pip install -e .` after `hedron new`).

**Fix:** Activate the project venv, run `pip install -e .` or `uv sync`, then
`python -c "import hedron; print(hedron.__version__)"` before starting uvicorn.

## Blank page / HTMX or CSS not loading

**Cause:** Hedron static assets (`/hedron-static/`) or app assets are not reachable—wrong
host/port, reverse proxy stripping paths, or a plain FastAPI app that never called
`mount_hedron_static`.

**Fix:** With the `Hedron()` app facade, static mounts are automatic. For plain FastAPI,
call `mount_hedron_static(app)`. Confirm
[http://127.0.0.1:8000/hedron-static/](http://127.0.0.1:8000/hedron-static/) returns
assets while the server runs. Behind a reverse proxy, forward `/hedron-static/` and
`/hedron-assets/` unchanged. See [Deployment](deployment.md) and
[Plain FastAPI](plain-fastapi.md).

## Port already in use (`Address already in use` on :8000)

**Cause:** Another process is bound to port 8000.

**Fix:** Stop the other server, or run `uvicorn app:app --reload --port 8001` and open
that port in the browser.

## Wrong or unexpected version

**Symptom:** Features in the docs are missing from your install, or verify text does not match.

**Fix:** Check `python -c "import hedron; print(hedron.__version__)"`.
Expect **`0.58.0`** in a PyPI-installed application and in this repository.
Upgrade an application with `pip install -U "hedron>=0.58.0,<0.59"`; use `uv sync` only
inside the repository.
See [What's ready](whats-ready.md). If docs describe a feature missing from your
install, either upgrade toward the pin that matches this documentation or switch the
docs to the tag that matches your installed release.

## CSRF 403 on POST (FastAPI / Flask)

**Cause:** Missing or mismatched CSRF token/cookie.

**Fix:** Perform a safe GET first to receive `hedron_csrf`, then send `X-CSRF-Token`
(or form field `csrf_token`) with the same value. On HTTPS, ensure the client stores
`Secure` cookies. See [Security](security.md).

## Tutorial code does not match `hedron new`

**Cause:** A guide still shows `app.region` / `@app.fragment` / `RefreshButton.for_region`,
but `hedron new` generates `@app.refreshable("/status")` and `status.refresh_button(...)`.

**Fix:** Keep the generated app. Add a second `@app.refreshable` as in
[HTMX interactions](htmx-interactions.md). Do not paste a region/fragment scaffold over
Hello. See [Which interaction API?](../getting-started/interaction-apis.md).

## `HEDRON_SESSION_SECRET` did nothing

**Cause:** Hedron does not read that environment variable. It is an adopter convention.

**Fix:** Pass `session_secret=` into `Hedron(...)`, typically
`session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production")`.
See [Secrets and workers](secrets-and-workers.md).

## HTMX 403 on fragment request

**Cause:** The request’s `HX-Target` is not in the route’s declared region allowlist
(typo in the region id / selector, or wrong fragment route).

**Fix:** Prefer the generated handle: `@app.refreshable("/status")` plus
`status.refresh_button(...)`. If you use the explicit allowlist path, keep one region
object end-to-end: `status = app.region("service-status")`,
`RefreshButton.for_region(status, href="/status", ...)`, and
`@app.fragment("/status", region=status)`. Confirm with:

```bash
curl -H 'HX-Request: true' -H 'HX-Target: #service-status' http://127.0.0.1:8000/status
```

### Try it (simulated)

=== "Demo"

    Correct target swaps; wrong `#panel` returns 403 with no swap. Docs simulation.

    <!-- hedron-sim:allowlist-403 -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import Hedron, Page, Stack, html, swap

    app = Hedron(
        title="Allowlist 403",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    status = app.region("service-status", description="Status panel")


    def status_panel():
        return html.div(
            html.strong("Service healthy"),
            html.span("Allowlisted #service-status"),
            id=status.id,
            role="status",
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                status_panel(),
                html.button(
                    "Correct #service-status → 200",
                    type="button",
                    **{
                        "hx-get": "/status",
                        "hx-target": status.selector,
                        "hx-swap": "outerHTML",
                    },
                ),
                html.button(
                    "Wrong #panel → 403",
                    type="button",
                    **{
                        "hx-get": "/status",
                        "hx-target": "#panel",
                        "hx-swap": "outerHTML",
                    },
                ),
            ),
            title="Allowlist",
        )


    @app.fragment("/status", region=status)
    def refresh():
        return swap(status_panel())
    ```

See [HTMX interactions](htmx-interactions.md).

## CSRF 403 on Django POST

**Cause:** Django `CsrfViewMiddleware` rejected the token, or the header name does not match settings.

**Fix:** Seed the cookie with a safe GET through `HedronDjango.respond` / `hedron_view`.
Send Django's `X-CSRFToken` **or** set `CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"` and send
Hedron's portable `X-CSRF-Token`. **Form field must be `csrfmiddlewaretoken`.**
Django's `CsrfViewMiddleware` does **not** accept Hedron's portable `csrf_token` name.
See [Django quickstart](../getting-started/django.md) and [Security](security.md).

## Explorer 404 or missing in production

**Cause:** `explorer="off"`, missing `hedron[dev]`, or production forced development mode off.

**Fix:** Install `hedron[dev]` for local Explorer; use `explorer="development"` only
locally; open **`http://127.0.0.1:8000/hedron-explorer/`** (trailing slash); use `secured`
with auth in rare cases; keep production off.

## `hedron new` installs an old train

**Cause:** An old CLI wrote `hedron>=0.4.0` (or another pre-0.11 floor).

**Fix:** Edit `pyproject.toml` to `hedron>=0.58.0,<0.59` and `uvicorn[standard]>=0.30`, then
reinstall. Current `hedron new` scaffolds `hedron>=0.58.0,<0.59` automatically.

## SSE / WebSocket / preload not working

**Cause:** Using Flask/Django expecting FastAPI live helpers; proxy buffering SSE; preload
left disabled; Origin rejected; treating experimental live APIs as production-required.

**Fix:** Live helpers (`job_status_sse_response`, `accept_page_session_channel`,
`NavigationPreloadPolicy`) are FastAPI **experimental** surfaces
(`hedron.experimental`) — prefer [polling](live-interaction.md) on every host, including
FastAPI. Disable response buffering for `text/event-stream`. Enable preload only with an
explicit `NavigationPreloadPolicy(enabled=True)`. Maturity source of truth: [What’s ready](whats-ready.md).

## Production startup: missing manifest (`HED-BUILD-0003`)

**Cause:** `HEDRON_ENV=production` / `production=True` without `hedron build` output.

**Fix:** Run `hedron build` and set `HEDRON_BUILD_DIR` if the manifest is not at
`.hedron/build/manifest.json`. Quickstarts do not create a production manifest—build before
setting production mode.

## Cannot import `Auto` / `DataTable` / chart helpers

**Cause:** `Auto` is core (`from hedron import Auto`). `DataTable` / `DataEditor` need the
data extra. First-party charts require `hedron[charts]` on the same pin as the rest of
Hedron (`>=0.58.0,<0.59`).

**Fix:**

```bash
# Auto needs no extra
pip install "hedron[data]>=0.58.0,<0.59"      # DataTable, DataEditor
pip install "hedron[charts]>=0.58.0,<0.59"   # chart components
```

The old `hedron-charts 0.1.x` line is incompatible with current Hedron. See
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor),
[Installation](../getting-started/installation.md), and
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

## HTMX form attrs typing

**Cause:** Hyphenated HTMX attribute names (`hx-post`, …) must be passed via a `dict`
unpacked into `Form(...)`.

**Fix:** Build a typed `dict[str, str]` (see [Forms and actions](forms-and-actions.md))
or use `html.form(...)` as in [minimal form](minimal-form.md). A `# type: ignore` on the
unpack is rarely needed when the dict is annotated.
