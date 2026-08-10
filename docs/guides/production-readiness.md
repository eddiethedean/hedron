# Production readiness

Ops-oriented narrative for **Hedron 0.25.x**. **Do not start here for the checklist.**

| Need | Canonical page |
|---|---|
| Adopter ship checklist | [Ship a Hedron app](ship.md) |
| Ship landing / links | [Ship a Hedron app](ship.md) |
| Docker / proxy / env deep dive | [Deployment](deployment.md) |
| Capability maturity | [What's ready today](whats-ready.md) |
| Trust-program priorities | [Production-quality maturity](production-quality.md) |
| Kitchen-sink archetype | [Reference app](../examples/reference-app.md) · [PRODUCTION_ARCHETYPE](../api/PRODUCTION_ARCHETYPE.md) |

Also: [Compatibility](../COMPATIBILITY.md) · [Support](support.md).

**Canonical production archetype:** [reference-app example](../examples/reference-app.md)
([PRODUCTION_ARCHETYPE](../api/PRODUCTION_ARCHETYPE.md) — `ARCHETYPE-025`: reverse-proxy
subpath, Redis job/cache, signed cookie sessions, `HEDRON_ENV=production`, CSP, Explorer
off, multi-worker).

## Before you ship

Pin package versions. Breaking changes may still land on `0.x`. There is **no commercial
SLA**. Confirm your intended surfaces against [What's ready](whats-ready.md).

!!! warning "SSE / WebSocket"

    Live helpers are **experimental** (`hedron.experimental`). Do not use SSE or WebSocket
    behind a load balancer without your own buffering, timeout, and backpressure proof.
    Prefer [polling](live-interaction.md) — it is the Supported fallback on every host.

## Ops checklist

1. Real `session_secret` (never the development default)
2. `hedron build` then `HEDRON_ENV=production`
3. `explorer="off"` in production
4. HTTPS + sticky sessions or external session/CSRF/job store for multi-worker
5. Under `HEDRON_ENV=production`, configure durable `set_job_backend` / `set_cache_backend`
   (in-memory backends are refused at app startup)
6. Production also fail-closes on weak/`replace-in-production` secrets, `security="development"`,
   Explorer development mode, open external redirects, and missing CSP unless you set
   `HEDRON_SECURITY_RISK_ACCEPTANCE` to a comma-separated list of explicit risk codes
   (`weak-session-secret`, `security-development`, `explorer-development`,
   `external-redirects`, `missing-csp`)
7. For SSE/WebSocket: confirm reverse-proxy buffering and timeouts ([Performance](performance.md))
8. Pin `hedron` and extras in your lockfile
9. Under a reverse-proxy subpath, set ASGI `root_path` and/or `HEDRON_ROOT_PATH` so session/CSRF
   cookies use the mount cookie path ([Mount API](../api/MOUNT.md); [Deployment](deployment.md))

## Security posture

- Secure defaults: contextual escaping, CSRF, `SafeUrl` / `TrustedHtml`, conservative caches
- Threat model and disclosure: [Security](security.md) · [Threat model](threat-model.md) ·
  [SECURITY.md](../SECURITY.md)
- You own authentication, authorization, and persistence

## Support boundaries

- Community support via GitHub Issues only — **no commercial SLA**
- Supported version lines: see [SECURITY.md](../SECURITY.md)

See [Error codes](error-codes.md) · [Public roadmap](roadmap.md) ·
[Production-quality maturity](production-quality.md) ·
[Enterprise diligence](enterprise-diligence.md).
