# Ship to production

One-page adopter checklist for shipping a Hedron app. Capability maturity lives on
[What’s ready](whats-ready.md). Detailed ops notes:
[Deployment](deployment.md) · [Production readiness](production-readiness.md).

Pin `hedron>=0.23.0,<0.24` (and matching adapters/extras) in your lockfile.

## Checklist

1. **Secrets** — Set a strong `session_secret` / `SECRET_KEY` / Flask `secret_key` from the
   environment. Never ship the scaffold placeholder.
2. **Build** — Run `hedron build` and deploy the build directory with the app **before**
   enabling production mode.
3. **Production gate** — Set `HEDRON_ENV=production` (or `Hedron(production=True)`). Fix
   `HED-BUILD-0003` / risk-acceptance codes rather than disabling the gate casually.
4. **Explorer** — `explorer="off"` (or `secured` with real auth). Development Explorer is
   disabled in production.
5. **HTTPS** — Terminate TLS so CSRF/session cookies can be `Secure`.
6. **CSRF** — Keep `standard` or `strict` profiles; seed tokens on GET; send
   `X-CSRF-Token` or form fields on unsafe methods.
7. **Path prefix** — If the app is under a reverse-proxy subpath, set
   `HEDRON_ROOT_PATH` and/or ASGI `root_path` — [Mount API](../api/MOUNT.md).
8. **Multi-worker** — In-memory sessions and job state do **not** span processes. Use sticky
   sessions **or** an external session store; call `set_job_backend(...)` (and cache
   backends) on every worker with the same Redis/Celery/RQ config. Prefer **polling** for
   job status (SSE/WebSocket helpers are experimental).
9. **Hosts** — Flask/Django: same secrets/HTTPS/CSRF hygiene; prefer polling for jobs —
   [Flask](../getting-started/flask.md) · [Django](../getting-started/django.md).
10. **Smoke** — Hit Hello + Refresh (or your primary fragment) and one CSRF form POST behind
    the real proxy.

## Multi-worker sessions (short note)

Starlette/Flask cookie sessions are signed but **not** shared across processes unless you
add a shared session backend (or stickiness). Hedron does not ship a first-party Redis
session store — configure your host stack (or a session middleware backed by Redis) when
you run more than one worker without sticky sessions. Durable **jobs** use
`set_job_backend` ([Jobs](../api/JOBS.md) · [Celery / RQ](jobs-celery-rq.md)).

## CI smoke (adopter)

Minimal FastAPI TestClient pattern: GET seeds CSRF → POST with token + HTMX headers →
assert fragment HTML. See [Test your UI](testing.md) and `hedron.testing` helpers.

## Related

- [Deployment](deployment.md) · [Security](security.md) · [Error codes](error-codes.md)
- [Enterprise diligence](enterprise-diligence.md) · [Support](support.md)
