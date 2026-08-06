# Production readiness

Ops-oriented checklist for the **0.15.0** train (implemented; **pending cut** of
`v0.15.0`—last published train is **0.14.x**). **Do not duplicate maturity claims
here** — the authoritative snapshot is [What's ready today](whats-ready.md).

Also: [Compatibility](../COMPATIBILITY.md) · [Support](support.md) ·
[Deployment](deployment.md).

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
6. For SSE/WebSocket: confirm reverse-proxy buffering and timeouts ([Performance](performance.md))
7. Pin `hedron` and extras in your lockfile

## Security posture

- Secure defaults: contextual escaping, CSRF, `SafeUrl` / `TrustedHtml`, conservative caches
- Threat model and disclosure: [Security](security.md) · [Threat model](threat-model.md) ·
  [SECURITY.md](../SECURITY.md)
- You own authentication, authorization, and persistence

## Support boundaries

- Community support via GitHub Issues only — **no commercial SLA**
- Supported version lines: see [SECURITY.md](../SECURITY.md)

See [Error codes](error-codes.md) · [Public roadmap](roadmap.md) ·
[Enterprise diligence](enterprise-diligence.md).
