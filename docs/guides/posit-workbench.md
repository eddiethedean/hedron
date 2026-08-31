# Posit Workbench

Run Hedron behind Posit Workbench or RStudio Server with a Workbench-aware app facade or by
changing only the launch command of an existing app. For a new application, install
`hedron-posit`, use `HedronPosit`, and launch with `hedron-posit run`; the
[`hedron-posit` beginner walkthrough](../getting-started/first-app-posit-workbench.md) explains each
step.

**Preferred for new apps:** `hedron-posit>=1.0.0` (or
`hedron[posit]>=1.0.0`). Plain FastAPI applications should use the
independent `fastapi-workbench>=1.0.0` package.

If `python3.11` is unavailable, use the walkthrough's [Python 3.11 pyenv fallback](../getting-started/first-app-posit-workbench.md#python-311-fallback)
before creating the virtual environment. When finished, return to [One application class, local and Workbench](#one-application-class-local-and-workbench).

Supported Workbench floor is **2025.05.1** (linux/amd64). Current verified lane is
Workbench **2026.07.0**. Prefer `HedronPosit` / `hedron-posit run` for new apps.

## One application class, local and Workbench

```python
from hedron import Page, Text
from hedron_posit import HedronPosit

app = HedronPosit(
    title="My app",
    security="standard",
    explorer="off",
    session_secret="replace-me",
)

@app.page("/")
def home() -> Page:
    return Page(Text("Hello"), title="Home")
```

Outside Posit Workbench this behaves like `Hedron`: no Workbench mount or
signal means no path normalization. Ordinary Uvicorn and generic ASGI
`root_path` deployments retain the same routing and cookie behavior.

## Ordinary local

```bash
uvicorn app:app --reload
```

For local reproduction of a prefixed Workbench request:

```python
app = HedronPosit(..., workbench_mount="/s/example/p/8050")
```

The explicit mount scopes cookies during construction and routes both
mount-prefixed requests and already-stripped proxy requests.

## Workbench launcher

```bash
hedron-posit check
hedron-posit run app:app
hedron-posit run app:create_app --factory

# The flagship command also delegates when the Posit extra is installed:
hedron run app:app
```

Use the `hedron-posit` commands for a new app. `hedron run` automatically delegates to an
installed Posit adapter when `RS_SERVER_URL` is present.

The launcher:

1. Binds a loopback socket (including port `0`)
2. Runs `/usr/lib/rstudio-server/bin/rserver-url -l <port>` when `RS_SERVER_URL` is set (no shell)
3. Exports `HEDRON_ROOT_PATH` **before** importing the app
4. Wraps once and serves the pre-bound socket

Some Workbench versions expose `UVICORN_ROOT_PATH` as the full URL returned by
`rserver-url`, while others expose only its path. Hedron accepts either form but
keeps only the validated local mount. The mount must also belong to the listener
that was actually bound: if an inherited hint names another session port, the
launcher calls `rserver-url` again for the bound port. This is why application
code should not copy a `/s/.../p/...` value from an earlier session or hard-code
port `8000`.

Session and CSRF cookies are then scoped to the browser mount. Hedron component
URLs, safe redirects, HTMX headers, assets, OpenAPI, and browser runtime helpers
are prefixed exactly once without application-side `local_href` calls.
`HedronPosit` consumes the resolved launcher handoff and is not wrapped a
second time. An existing `Hedron` or generic ASGI app still receives the outer
`workbenchify` wrapper, so changing only the command remains supported.

Dynamic discovery cannot happen inside `HedronPosit.__init__`: the
`rserver-url` command needs the listener's selected port before the application
module is imported.

## Compatibility wrapper for an existing app

```python
import os
from hedron_posit import workbenchify

os.environ["HEDRON_ROOT_PATH"] = "/s/example/p/8050"  # before Hedron()
from app import app

app = workbenchify(app)
```

`workbenchify` rewrites HTTP/WebSocket scopes and safe local response headers.
It also repairs Hedron-owned cookies left at `Path=/`; third-party cookies are
not rewritten.

Posit Connect applies its content prefix to outgoing cookie paths but does not
rewrite application redirects. When Connect's protected runtime marker and
singular app-base header are both present, Hedron therefore emits its owned
cookies at `/` for Connect to scope once while continuing to mount redirects and
HTMX response headers itself.

## Diagnostics and trust

`hedron-posit check --format json` resolves configuration without binding,
executing discovery, or importing the app. `app.workbench_status()` reports the
facade's redacted resolved state.

`hedron-posit doctor app:app --live` additionally binds, discovers, imports,
and ASGI-probes generated URLs and cookie paths. Use `--topology` with `local`,
`launcher-local`, `launcher-kubernetes`, `launcher-slurm`, or `reverse-proxy`.

For current-session navigation use `app.browser_url*`. For email invites, OAuth
callbacks, and other durable links use `app.external_url*` / `app.durable_url*`.
The durable API rejects Workbench `/s/.../p/...` session URLs because sessions
can be suspended, killed, or replaced; use a stable `external_base_url`, usually
a Posit Connect deployment. Link generation rejects implicit loopback origins
and never derives an origin from the inbound `Host` header.

For a response redirect that must survive a Workbench proxy rewriting
path-absolute `Location` headers, use `app.redirect(path, absolute=True)` or
`app.browser_redirect(path)`. Named routes and request-bound `posit_for(request)`
contexts provide the corresponding `*_for` helpers. The absolute target is built
only from the resolved Workbench/Connect base or an explicit `external_base_url`.
In an active Workbench deployment, Hedron also normalizes safe local `Location`
headers to that absolute form automatically; HTMX navigation headers remain
mounted paths.

- Listener binds are loopback-only unless `--allow-external-bind` is explicit.
- Forwarded proxy trust accepts exact IPs or bounded CIDRs shared by Uvicorn and
  Hedron; wildcard trust is rejected.
- Invalid mounts, public URLs with credentials, conflicting queries, traversal,
  and oversized absolute targets fail closed.
- The launcher supports either reload or multiple Uvicorn workers by handing the
  pre-bound listener to a supervisor; those two modes are mutually exclusive.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Cookies missing under `/s/…/p/…` | Prefer `HedronPosit` / `hedron-posit run`; request-time `root_path` repairs Hedron-owned cookies only |
| HTMX 403 | Declare fragment regions; mount stripping is fail-closed |
| `HED-WB-0003` | `rserver-url` missing or non-absolute; pass `--mount` for local repro |
| `HED-WB-0009` | Reload and multiple workers were combined; select one supervisor mode |
| Double-prefixed URLs | Return ordinary local paths; Hedron prefixes components and safe response headers once |

## Non-goals

Flask/Django, bundling `rserver-url`, automated Posit Connect publishing,
treating Workbench login as Hedron identity, and guessing stable sharing URLs.
