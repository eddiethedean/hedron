# Deployment

## Production checklist

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

See the full [configuration reference](../CONFIGURATION.md).

## Build manifests

In production, Hedron refuses to start without a valid `manifest.json` under the build
directory and disables runtime HDN/CSS compilation. Locally:

```bash
hedron build
HEDRON_ENV=production uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

Fingerprinted assets are served from `/hedron-assets/` (or your configured mount).
Bundled HTMX remains under `/hedron-static/`.

## Process model

Hedron is a FastAPI/Starlette ASGI app. Run it with uvicorn, gunicorn+uvicorn workers,
or your platform’s ASGI runner:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2
```

Terminate TLS at your reverse proxy. Forward `X-Forwarded-Proto` so request schemes
(and Secure cookies) reflect HTTPS.

## Secrets

Store session secrets and credentials in your platform secret store or process
environment. Do not put secrets in `[tool.hedron]`.

## See also

- [Security](security.md)
- [Project workflow](project-workflow.md) (0.4+)
- [STATUS](../STATUS.md)
