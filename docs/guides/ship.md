# Ship a Hedron app

**Canonical adopter checklist** for shipping on the current **1.0.x** train. Capability
maturity lives only on [What’s ready](whats-ready.md). Evaluators:
[Evaluate Hedron](evaluate.md).

Pin `hedron>=1.0.0,<1.1` (and matching adapters/extras) in your lockfile.

| Need | Go here |
|---|---|
| **This checklist** | Adopter ship gate (use this page) |
| Environment / Dockerfile / proxy | [Deployment](deployment.md) (deep dive, not a second checklist) |
| Security defaults, CSRF, headers | [Security](security.md) · [Threat model](threat-model.md) |
| Compatibility pins & charts packaging | [Compatibility](../COMPATIBILITY.md) |
| Kitchen-sink sample | [Reference app](../examples/reference-app.md) · [PRODUCTION_ARCHETYPE](../api/PRODUCTION_ARCHETYPE.md) |
| Support / SLA honesty | [Support](support.md) |
| Enterprise diligence | [Enterprise diligence](enterprise-diligence.md) |

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
8. **Multi-worker / HA** — See [High availability](#high-availability-multi-replica) below.
9. **Hosts** — Flask/Django: same secrets/HTTPS/CSRF hygiene; prefer polling for jobs —
   [Flask](../getting-started/flask.md) · [Django](../getting-started/django.md) ·
   [Deployment host parity](deployment.md#flask-django-parity).
10. **Smoke** — Hit Hello + Refresh (or your primary fragment) and one CSRF form POST behind
    the real proxy.

## Production application constructor

Make production mode and secrets explicit in the application module. A missing secret should
fail startup instead of silently falling back to a development value:

```python
import os

import redis

from hedron import Hedron
from hedron_core.cache import set_cache_backend
from hedron_core.jobs import RedisJobBackend, set_job_backend
from hedron_core.redis_cache import RedisCacheBackend

redis_client = redis.Redis.from_url(
    os.environ["HEDRON_REDIS_URL"],
    decode_responses=True,
)
set_job_backend(RedisJobBackend(redis_client))
set_cache_backend(RedisCacheBackend(redis_client))

app = Hedron(
    title="Operations",
    security="strict",
    production=os.environ.get("HEDRON_ENV") == "production",
    explorer="off",
    session_secret=os.environ["HEDRON_SESSION_SECRET"],
)
```

Build before starting that process:

```bash
pip install "redis>=5,<6"
hedron build
HEDRON_ENV=production uvicorn app:app --host 0.0.0.0 --port 8000
```

The environment variable is an adopter convention read by your application module; Hedron does
not load `HEDRON_SESSION_SECRET` automatically. Every worker must use the same Redis URL and
session secret.

## High availability (multi-replica)

Hedron does **not** ship a first-party shared session store. When you run more than one
worker or replica:

- **Cookie sessions** — Signed cookies work across workers if every process shares the same
  `session_secret`. Sticky sessions still help when you keep in-process state.
- **Shared session backend** — Configure your host stack (Starlette/Flask/Django session
  middleware backed by Redis, or equivalent) when stickiness is unavailable.
- **Durable jobs** — Call `set_job_backend(...)` on **every** worker with the same
  Redis/Celery/RQ config — [Jobs](../api/JOBS.md) · [Celery / RQ](jobs-celery-rq.md).
- **Live status UX** — Prefer **polling** (`Poll` + `job_status_response`). SSE/WebSocket
  helpers are experimental and sensitive to proxy buffering.
- **Reverse proxy** — Forward `/hedron-static/` and `/hedron-assets/` unchanged; set
  `HEDRON_ROOT_PATH` for subpath mounts; disable response buffering for SSE only if you
  intentionally use experimental live helpers.
- **CSRF cookies** — Cookie `Path` follows the mount — keep proxy prefixes aligned with
  [Mount](../api/MOUNT.md).

## CI smoke (adopter)

Minimal FastAPI TestClient pattern: GET seeds CSRF → POST with token + HTMX headers →
assert fragment HTML. See [Test your UI](testing.md) and `hedron.testing` helpers.

## Related

- [Deployment](deployment.md) · [Security](security.md) · [Error codes](error-codes.md)
- [Enterprise diligence](enterprise-diligence.md) · [Support](support.md)
- [What’s ready](whats-ready.md) · [Evaluate Hedron](evaluate.md)
