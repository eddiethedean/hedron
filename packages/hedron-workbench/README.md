# hedron-workbench

[![PyPI](https://img.shields.io/pypi/v/hedron-workbench.svg)](https://pypi.org/project/hedron-workbench/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-workbench.svg)](https://pypi.org/project/hedron-workbench/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Optional Posit Workbench / RStudio Server deployment adapter for Hedron.

An existing FastAPI Hedron app can run unchanged behind Workbench by switching
the launch command. Installing or importing this package does **not** wrap your
application. `RS_SERVER_URL` is discovery-only and never grants trust.

Also available as `hedron[workbench]`.

**Package maturity:** Beta · **Train:** `0.49.x` · pin `>=0.49.0,<0.50`

Supported Workbench floor is **2025.05.1**; current verified lane is **2026.07.0**.

Behavior is reimplemented from observed
[fastapi-workbench 0.3.4](https://github.com/eddiethedean/jwt-user-management/tree/main/fastapi_workbench)
(MIT) with attribution. This package does not depend on or vendor that project.

## Install

```bash
pip install "hedron-workbench>=0.49.0,<0.50"
# or
uv add "hedron[workbench]>=0.49.0,<0.50"
```

## Hedron application facade

Import `HedronWorkbench` in place of `Hedron`. With no Workbench signal it is
an ordinary `Hedron` application: local Uvicorn, generic ASGI `root_path`,
routes, middleware, and cookies retain Hedron behavior.

```python
from hedron_workbench import HedronWorkbench

app = HedronWorkbench(
    title="My app",
    session_secret="replace-me",
)
```

Run the same object locally with Uvicorn or on Workbench with the launcher:

```bash
uvicorn app:app --reload
hedron run app:app  # auto-selects the Workbench launcher when RS_SERVER_URL is present
hedron-workbench run app:app
```

For local proxy reproduction, use
`HedronWorkbench(workbench_mount="/s/session/p/123")`. The explicit mount is
applied before Hedron creates session/CSRF cookies and also handles prefixed
request paths when the ASGI server does not set `root_path`.

The class cannot execute `rserver-url` itself: dynamic discovery needs a bound
listener port before the module is imported. The launcher performs that
ordering and passes the resolved deployment into the class.

## Launcher path

```bash
hedron-workbench run app:app
hedron-workbench check --format json
hedron-workbench run app:create_app --factory
```

The launcher binds a loopback socket, runs `rserver-url` when `RS_SERVER_URL` is
set, exports `HEDRON_ROOT_PATH` **before** importing the app (so session/CSRF
cookie `Path` is correct), recognizes `HedronWorkbench` as already adapted, and
serves with one normalizer.

External binds require the explicit `--allow-external-bind` flag. The built-in
runner supports `--reload` and `--workers`: its parent binds and discovers once,
then execs Uvicorn's supervisor/workers with the inherited listener and resolved
mount. Reload and multiple workers cannot be enabled together.

`workbenchify(app)` remains available for adapting an already-created generic
ASGI application. The response boundary repairs Hedron-owned cookies whose path
is still `/`; third-party cookies remain application-owned.

`app.workbench_status()` returns a redacted deployment diagnostic without
exposing session IDs, URL credentials, or token-shaped values.

## Public links and email invites

Use the facade to build links that leave the current browser, such as email
invites, OAuth callbacks, and password resets:

```python
from fastapi import Request


@app.post("/invite")
def send_invite(request: Request):
    accept_url = app.external_url_for(
        "accept_invite",
        request=request,
        invite_id="abc123",
        query={"token": "signed-single-use-token"},
    )
    # enqueue email containing accept_url
```

`external_url*` is deliberately durable: a disposable Workbench `/s/.../p/...`
session URL is rejected. Use `browser_url*` for a link that stays in the current
interactive session, and deploy durable invitations/callbacks to a stable URL
(typically Posit Connect or an explicit `external_base_url`). On Posit Connect,
a request can supply the platform's app-base header, but it is accepted
only when its path exactly matches ASGI `root_path` and Connect's protected
runtime marker is present (or an immediate proxy peer is explicitly trusted).
Outside either platform, configure a stable base explicitly:

```python
app = HedronWorkbench(
    title="My app",
    session_secret="replace-me",
    external_base_url="https://apps.example.com/my-app",
)
```

If no trusted base exists, link generation raises `ValueError`; it never falls
back to an untrusted inbound `Host` header. Route paths must remain local and
query parameters are encoded structurally. A Workbench discovery result that
contains only a mount path also fails for public links because its inferred
origin is loopback; configure `workbench_public_base_url` for browser-only links
or a stable `external_base_url` for durable links.

## Hands-off URL adaptation

Hedron-owned component URL attributes (`href`, form actions, HTMX request and
history paths, assets), safe local response redirects, HTMX redirect/location
headers, OpenAPI, static assets, cookies, and WebSockets are mount-aware. A
request-time ASGI `root_path` from Posit Connect or a generic proxy is sufficient;
the app does not need to manually call `local_href` or `mounted_redirect`.
Connect's authenticated proxy adds its content prefix to cookie paths but passes
redirect locations through, so the adapter de-scopes only Hedron-owned cookies
before Connect's outer rewrite and still mounts local response headers itself.

Mounted pages expose `window.Hedron.href()`, `.fetch()`, `.eventSource()`,
`.websocketUrl()`, and `.websocket()` for application JavaScript. Python code can
use `app.href_for()`, `app.redirect_for()`, `app.browser_url_for()`, and
`app.external_url_for()`. `app.external_base(request=...)` captures a validated,
immutable base for a background job; `app.deployment_capabilities()` explains
whether that base is browser-only or durable.

Raw trusted HTML, arbitrary JavaScript strings, third-party ASGI response bodies,
third-party cookies, and a stable sharing destination cannot be inferred safely.
Those remain explicit integration points.

## Diagnostics and topology profiles

```bash
hedron-workbench doctor --format json
hedron-workbench doctor app:app --live --mount /s/example/p/8050
hedron-workbench run app:app --topology launcher-kubernetes
```

`doctor --live` binds, discovers when applicable, imports the app after the
handoff, and ASGI-probes generated URLs and cookie paths. Topology profiles cover
local, local Launcher, Kubernetes Launcher, Slurm Launcher, and external reverse
proxy deployments. Remote Launcher profiles select a reachable bind by default;
proxy CIDRs must still be explicitly bounded (wildcard trust remains rejected).

## Non-goals

Flask/Django/WSGI, bundling `rserver-url`, automated Connect publishing, treating
Workbench or Connect login as Hedron identity, or guessing a durable deployment
from an ephemeral session.

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
