# Posit Workbench

Run Hedron behind Posit Workbench or RStudio Server with a Workbench-aware app
facade or by changing only the launch command of an existing app.

**Requires:** `hedron-workbench>=0.29.0,<0.30` (or `hedron[workbench]`).

## One application class, local and Workbench

```python
from hedron import Page, Text
from hedron_workbench import HedronWorkbench

app = HedronWorkbench(
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
app = HedronWorkbench(..., workbench_mount="/s/example/p/8050")
```

The explicit mount scopes cookies during construction and routes both
mount-prefixed requests and already-stripped proxy requests.

## Workbench launcher

```bash
hedron-workbench run app:app
hedron-workbench run app:create_app --factory
hedron-workbench check --format json
```

The launcher:

1. Binds a loopback socket (including port `0`)
2. Runs `/usr/lib/rstudio-server/bin/rserver-url -l <port>` when `RS_SERVER_URL` is set (no shell)
3. Exports `HEDRON_ROOT_PATH` **before** importing the app
4. Wraps once and serves the pre-bound socket

Session and CSRF cookies are then scoped to the browser mount.
`HedronWorkbench` consumes the resolved launcher handoff and is not wrapped a
second time. An existing `Hedron` or generic ASGI app still receives the outer
`workbenchify` wrapper, so changing only the command remains supported.

Dynamic discovery cannot happen inside `HedronWorkbench.__init__`: the
`rserver-url` command needs the listener's selected port before the application
module is imported.

## Explicit wrapper

```python
import os
from hedron_workbench import workbenchify

os.environ["HEDRON_ROOT_PATH"] = "/s/example/p/8050"  # before Hedron()
from app import app

app = workbenchify(app)
```

`workbenchify` rewrites HTTP/WebSocket scopes only. It does not change cookie
`Path` after construction.

## Diagnostics and trust

`hedron-workbench check --format json` resolves configuration without binding,
executing discovery, or importing the app. `app.workbench_status()` reports the
facade's redacted resolved state.

For email invites, OAuth callbacks, and other links that leave the browser, use
`app.external_url(...)` or `app.external_url_for(...)`. Configure
`workbench_public_base_url="https://workbench.example/s/.../p/..."` when
`rserver-url` supplies only a mount path. Link generation rejects implicit
loopback origins and never derives an origin from the inbound `Host` header.

- Listener binds are loopback-only unless `--allow-external-bind` is explicit.
- Forwarded proxy trust is one exact IP allowlist shared by Uvicorn and Hedron;
  wildcard trust is rejected.
- Invalid mounts, public URLs with credentials, conflicting queries, traversal,
  and oversized absolute targets fail closed.
- The built-in pre-bound runner is one process without reload. Use an external
  supervisor for other process topologies.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Cookies missing under `/s/…/p/…` | Export `HEDRON_ROOT_PATH` before `Hedron()`; do not rely on `--root-path` alone |
| HTMX 403 | Declare fragment regions; mount stripping is fail-closed |
| `HED-WB-0003` | `rserver-url` missing or non-absolute; pass `--mount` for local repro |
| `HED-WB-0009` | Reload/multi-worker requested from the pre-bound runner; use one process or an external supervisor |
| Double-prefixed URLs | Use `redirect_local(..., mount=)` / `prefix_local_path` once |

## Non-goals

Flask/Django, auto-activation, bundling `rserver-url`, Posit Connect publishing,
and treating Workbench login as Hedron identity.
