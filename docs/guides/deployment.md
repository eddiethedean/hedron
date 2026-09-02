# Deployment

Adopter ship checklist (canonical): [Ship a Hedron app](ship.md).
This page is the **deep dive** for environment variables, Docker/proxy sketches, and
host parity — not a second checklist.

## Flask / Django parity

Adapter hosts follow the same secrets, HTTPS, and CSRF hygiene. Differences:

| Concern | Flask (`hedron-flask`) | Django (`hedron-django`) |
|---|---|---|
| App factory | `HedronFlask` / `init_app` or `hedron new --flask` | AppConfig + views / `hedron new --django` |
| CSRF | Hedron cookie + validate on unsafe `respond` / routes | Django CSRF middleware + portable `X-CSRF-Token` |
| Static assets | Mount / serve Hedron static the scaffold configures | Same — keep `/hedron-static/` reachable behind the proxy |
| Production build gates | Use FastAPI flagship patterns when serving Hedron HTML from FastAPI; Flask/Django apps still need HTTPS + secrets | Same — Django `DEBUG=False`, `SECRET_KEY`, HTTPS |
| Live updates | Prefer **polling** (SSE/WS helpers are FastAPI-experimental only) | Prefer **polling** |
| Multi-worker | Sticky sessions or shared session store; shared Redis job backend when using jobs | Same |

### Flask / Django production cookbook (short)

1. Replace scaffold secrets (`HEDRON_SESSION_SECRET` / Django `SECRET_KEY` / Flask `secret_key`).
2. Terminate TLS at the proxy; forward the app path and static mounts unchanged.
3. Keep CSRF enabled; seed tokens on GET; send `X-CSRF-Token` or form fields on POST.
4. Prefer `Poll` + job status HTML over experimental FastAPI-only SSE helpers.
5. Smoke Hello + Refresh (or your primary fragment) and one CSRF POST behind the real proxy.

Quickstarts: [Flask](../getting-started/flask.md) · [Django](../getting-started/django.md) ·
[Adapters API](../api/ADAPTERS.md).

## Environment

| Variable | Role |
|---|---|
| `HEDRON_ENV=production` | Production mode when constructor `production` is omitted |
| `HEDRON_BUILD_DIR` | Build/manifest directory overlay |
| `HEDRON_THEME` | Theme overlay |
| `HEDRON_REDIS_URL` | Optional Redis URL for job backends that use it (not required for pages) |
| `HEDRON_ROOT_PATH` | Optional reverse-proxy root path; scopes session/CSRF cookie `Path` and feeds `resolve_mount_path` |
| `HEDRON_SESSION_SECRET` | **Adopter convention** — read in `app.py` and pass to `Hedron(session_secret=...)`; Hedron does not load it automatically |

See the full [configuration reference](../CONFIGURATION.md).

Posit Workbench / RStudio Server: use `hedron-posit run app:app` so
`HEDRON_ROOT_PATH` is exported before import. See [Posit Workbench](posit-workbench.md).

For durable multi-worker jobs, see [Celery / RQ + Redis](jobs-celery-rq.md).

## Build manifests

In production, Hedron refuses to start without a valid `manifest.json` under the build
directory (`HED-BUILD-0003` if missing) and disables runtime CSS compilation. Jinja
templates are resolved through the application's configured loader; Hedron never
discovers or compiles HDN source. Locally:

```bash
hedron build
HEDRON_ENV=production uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

Fingerprinted assets are served from `/hedron-assets/` (or your configured mount).
Bundled HTMX remains under `/hedron-static/`.

## Dockerfile (FastAPI adopter sketch)

Minimal single-stage image for a scaffolded `hedron new` app (adjust paths as needed).
This is an **adopter starting point** — not a maintained production image.

Hedron does **not** read a session secret from the environment by itself. Pass it into
`Hedron(session_secret=...)` from your process environment (convention below:
`HEDRON_SESSION_SECRET`).

```python title="app.py (secret from env)"
import os

from hedron import Hedron

app = Hedron(
    title="Hedron App",
    security="standard",
    explorer="off",
    session_secret=os.environ["HEDRON_SESSION_SECRET"],
)
```

### Hello scaffold (`hedron new`)

A fresh FastAPI scaffold contains `pyproject.toml`, `app.py`, and an empty
`components/` directory. It does not generate a README:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml app.py ./
COPY components ./components
RUN pip install --no-cache-dir . "uvicorn[standard]" \
    && hedron build
ENV HEDRON_ENV=production
# Inject HEDRON_SESSION_SECRET at runtime through your deployment platform.
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Keep this file list synchronized with your application. If the empty `components/`
directory is not committed by your version-control system, either create it in the image
(`RUN mkdir -p components`) or remove that `COPY` until you add a project component.

### Apps with a `src/` layout

Multi-stage layout when you vendor a fuller `src/` tree:

```dockerfile
FROM python:3.12-slim AS build
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
# If you use uv:
# COPY uv.lock ./
# RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev
RUN pip install --no-cache-dir .
RUN pip install --no-cache-dir "uvicorn[standard]"
RUN hedron build

FROM python:3.12-slim
WORKDIR /app
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /app /app
ENV HEDRON_ENV=production
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Keep `manifest.json` (from `hedron build`) in the runtime image. Inject the session secret
at runtime through your platform secret store; never bake a real secret or a known
placeholder into the image. Compose under
`examples/reference-app/` is **maintainer-experimental** — prefer this sketch or local
`uvicorn` for learning. Monorepo reference Dockerfile:
[`examples/reference-app/Dockerfile`](https://github.com/eddiethedean/hedron/blob/main/examples/reference-app/Dockerfile).

Single-stage sketch when you already vendor a lockfile:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir "hedron>=1.0.0" "uvicorn[standard]" \
 && hedron build
ENV HEDRON_ENV=production
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

If the image builds an application package instead of installing Hedron directly,
use `pip install --no-cache-dir . "uvicorn[standard]"` and ensure `hedron` is a
project dependency.
## Reverse proxy

Terminate TLS at nginx, Caddy, or your cloud load balancer. Forward
`X-Forwarded-Proto` so Secure cookies and redirects see HTTPS. When the app is mounted
under a subpath, configure ASGI `root_path` (uvicorn `--root-path`) or WSGI
`SCRIPT_NAME`, and set `HEDRON_ROOT_PATH` when your deploy samples use it.
Contract details: [Mount / path prefix](../api/MOUNT.md). Adopter one-pager:
[Ship a Hedron app](ship.md).

Disable response buffering for `text/event-stream` **only if** you use experimental SSE
([live interaction](live-interaction.md)). Prefer **polling** (`Poll` +
`job_status_response`) for Supported multi-worker status UX — most reverse proxies need
no special SSE configuration then.

!!! warning "Do not rely on SSE/WebSocket without your own proof"

    Prefer [polling](live-interaction.md) behind load balancers. Live transport APIs ship
    on FastAPI, but full ops/backpressure evidence is incomplete — see
    [What’s ready](whats-ready.md).

### nginx

For an ordinary Hedron application using pages, fragments, and polling, start with:

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Connection "";
}
```

If you deliberately enable experimental SSE, apply streaming settings only to the SSE
route rather than weakening buffering and timeouts for the whole application:

```nginx
location /events/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 3600s;
}
```

### Caddy

The default reverse proxy needs no streaming override:

```caddy
example.com {
    reverse_proxy 127.0.0.1:8000
}
```

For experimental SSE, scope flushing and the extended timeout to the event route:

```caddy
example.com {
    @events path /events/*
    reverse_proxy @events 127.0.0.1:8000 {
        flush_interval -1
        transport http {
            read_timeout 3600s
        }
    }
    reverse_proxy 127.0.0.1:8000
}
```

### AWS ALB

- Idle timeout: raise above your longest SSE/WS session (default 60s is often too low).
- Stickiness: enable target-group stickiness if workers hold in-memory session/channel state.
- HTTP/2: ALB supports it to clients; ensure backends accept long-lived connections without
  response buffering at an extra proxy layer.

### Kubernetes / Ingress notes

- Use **sticky sessions** (session affinity) when workers hold in-memory session or live
  channel state.
- On nginx Ingress, set annotations such as
  `nginx.ingress.kubernetes.io/proxy-buffering: "off"` and raise
  `proxy-read-timeout` for SSE routes.
- Point liveness at `/healthz` and readiness at `/readyz` (see below).
- Keep `HEDRON_ENV=production` and a built `manifest.json` in the image.

## Health and readiness

Expose liveness/readiness on the same ASGI app (see [Observability](observability.md)):

```python
@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> dict[str, str]:
    # Optionally assert build manifest / dependency reachability.
    return {"status": "ready"}
```

Point your orchestrator probes at these paths. Hedron’s production start already fails
closed without a build manifest (`HED-BUILD-0003`).

## Process model

### FastAPI (ASGI)

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2
# or gunicorn -k uvicorn.workers.UvicornWorker ...
```

With multiple workers, use sticky sessions or an external session store. Do not assume
in-process memory is shared. Redis is only required when you configure a job backend that
needs `HEDRON_REDIS_URL`.

Suggested uvicorn production shape:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2 \
  --proxy-headers --forwarded-allow-ips="127.0.0.1"
```

Set `--forwarded-allow-ips` to the actual proxy IP or CIDR visible to the application.
Do not use `*` unless every connection is forced through a trusted proxy that removes
client-supplied forwarding headers; otherwise a direct client can spoof scheme or address
information. In container platforms, the trusted value is often the ingress or sidecar
network rather than `127.0.0.1`.

For SSE-heavy apps, prefer fewer long-lived workers (or a dedicated SSE service) and
sticky sessions so reconnects land on a process that still holds channel state.

### Flask (WSGI)

```bash
waitress-serve --listen=0.0.0.0:8000 "myapp:create_app()"
```

Set Flask `SECRET_KEY` from a secret store. CSRF cookies are issued on safe GETs when
`HedronFlask(auto_csrf_cookie=True)` (default).

### Django (WSGI / ASGI)

Django floor: `>=5.2,<6`.

```bash
gunicorn wsgi:application -b 0.0.0.0:8000
uvicorn asgi:application --host 0.0.0.0 --port 8000
```

Set `SECRET_KEY` and align `CSRF_HEADER_NAME` if clients send `X-CSRF-Token`
([Django quickstart](../getting-started/django.md)).

## Secrets

Store session secrets and credentials in your platform secret store or process
environment. Do not put secrets in `[tool.hedron]`. Adapter demos hardcode secrets for
local use only.

## See also

- [Security](security.md) · [Cookbook](cookbook.md) · [Ship a Hedron app](ship.md)
- [Error codes](error-codes.md) · [Compatibility](../COMPATIBILITY.md)
