# Deployment

## Production checklist (FastAPI flagship)

1. Set a strong `session_secret` (never the development default). Prefer `security="strict"` when CSP without inline styles is acceptable.
2. Run `hedron build` and deploy the build directory with your app (**before** enabling production mode).
3. Set `HEDRON_ENV=production` or `Hedron(production=True)`.
4. Keep `explorer="off"` (or `secured` with real auth). Development Explorer is disabled in production.
5. Serve behind HTTPS so CSRF cookies can be `Secure`.

## Environment

| Variable | Role |
|---|---|
| `HEDRON_ENV=production` | Production mode when constructor `production` is omitted |
| `HEDRON_BUILD_DIR` | Build/manifest directory overlay |
| `HEDRON_THEME` | Theme overlay |
| `HEDRON_REDIS_URL` | Optional Redis URL for job backends that use it (not required for pages) |
| `HEDRON_ROOT_PATH` | Optional reverse-proxy root path hint for reference/deploy samples |

See the full [configuration reference](../CONFIGURATION.md).

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

## Dockerfile (FastAPI)

Install the **application** dependencies (not only Hedron), build the manifest, then
run under production mode:

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

Adjust module path (`app:app`), copy layout, and Python version to match your project.
Keep `manifest.json` (from `hedron build`) in the runtime image. For a monorepo
reference layout, see [`examples/reference-app/Dockerfile`](https://github.com/eddiethedean/hedron/blob/main/examples/reference-app/Dockerfile).

Single-stage sketch when you already vendor a lockfile:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir ".[standard]" "uvicorn[standard]" \
 && hedron build
ENV HEDRON_ENV=production
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Reverse proxy

Terminate TLS at nginx, Caddy, or your cloud load balancer. Forward
`X-Forwarded-Proto` so Secure cookies and redirects see HTTPS. When the app is mounted
under a subpath, configure ASGI `root_path` (uvicorn `--root-path`) or WSGI
`SCRIPT_NAME`, and set `HEDRON_ROOT_PATH` when your deploy samples use it.

Disable response buffering for `text/event-stream` if you use SSE
([live interaction](live-interaction.md)).

## Process model

### FastAPI (ASGI)

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2
# or gunicorn -k uvicorn.workers.UvicornWorker ...
```

With multiple workers, use sticky sessions or an external session store. Do not assume
in-process memory is shared. Redis is only required when you configure a job backend that
needs `HEDRON_REDIS_URL`.

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

- [Security](security.md) · [Cookbook](cookbook.md) · [Production readiness](production-readiness.md)
- [Error codes](error-codes.md) · [Compatibility](../COMPATIBILITY.md)
