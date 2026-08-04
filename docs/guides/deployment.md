# Deployment

## Production checklist (FastAPI flagship)

1. Set a strong `session_secret` (never the development default). Prefer `security="strict"` when CSP without inline styles is acceptable.
2. Set `HEDRON_ENV=production` or `Hedron(production=True)`.
3. Run `hedron build` (0.4+) and deploy the build directory with your app.
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
directory and disables runtime CSS and legacy HDN-source compilation. Locally:

```bash
hedron build
HEDRON_ENV=production uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

Fingerprinted assets are served from `/hedron-assets/` (or your configured mount).
Bundled HTMX remains under `/hedron-static/`.

## Process model

### FastAPI (ASGI)

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2
# or gunicorn -k uvicorn.workers.UvicornWorker ...
```

### Flask (WSGI)

Use Waitress (Supported matrix) or gunicorn:

```bash
waitress-serve --listen=0.0.0.0:8000 "myapp:create_app()"
```

Set Flask `SECRET_KEY` from a secret store. CSRF cookies are issued on safe GETs when
`HedronFlask(auto_csrf_cookie=True)` (default).

### Django (WSGI / ASGI)

Django floor: `>=5.2,<6`. Example:

```bash
gunicorn wsgi:application -b 0.0.0.0:8000
uvicorn asgi:application --host 0.0.0.0 --port 8000
```

Set `SECRET_KEY` and align `CSRF_HEADER_NAME` if clients send `X-CSRF-Token`
([Django quickstart](../getting-started/django.md)).

Terminate TLS at your reverse proxy. Forward `X-Forwarded-Proto` so request schemes
(and Secure cookies) reflect HTTPS. Configure ASGI `root_path` / WSGI `SCRIPT_NAME` when
mounted under a subpath.

## Secrets

Store session secrets and credentials in your platform secret store or process
environment. Do not put secrets in `[tool.hedron]`. Adapter demos hardcode secrets for
local use only.

## See also

- [Security](security.md)
- [Project workflow](project-workflow.md)
- [STATUS](../STATUS.md)
- [Compatibility](../COMPATIBILITY.md)
