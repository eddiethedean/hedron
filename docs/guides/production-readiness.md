# Production readiness

One-page evaluator summary for the published **0.10.1** train. Authoritative maturity
snapshot: [What's ready today](whats-ready.md). Also:
[Compatibility](../COMPATIBILITY.md) · [Support](support.md).

## What you can ship today (Beta)

Pin package versions. Breaking changes may still land on `0.x`. There is **no commercial
SLA**.

**Ship with ordinary ops diligence:**

- Typed pages/fragments, FastAPI routing, CSRF profiles, CLI, testing helpers
- HTMX fragment loops and `InteractionResult`
- Flask / Django adapters on the Supported matrix (routing/HTMX; not full Django forms depth)
- Optional HDJ (`hedron[jinja]`), DataTable/DataEditor (`hedron[data]`), Explorer (`hedron[dev]`) for local diagnostics

**API shipped — ops evidence incomplete (read Deferred rows on
[What's ready](whats-ready.md) before relying on these behind load balancers):**

- Live helpers on FastAPI (SSE, streaming, WebSocket channels, Chat/Dialog, preload)
- Full multi-engine live browser matrix, load/proxy backpressure proof, and some Explorer
  live traces remain Deferred (`BROWSER-10-001`, `PERF-10-001`, `EXPLORER-10-001`)
- Prefer polling when you need a Supported fallback without that evidence

## What remains volatile or incomplete

| Area | Status |
|---|---|
| `hedron-charts` | Alpha |
| First-party live-transport sample app | Shipped: [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction) (poll + stream + SSE + Job SSE + WS + preload). Browser matrix / load-proxy evidence remain Deferred |
| Django QuerySet DataSource / Hedron Django forms | Planned **0.11** |
| Live browser matrix / proxy load evidence | Deferred on `0.10.x` |
| Public API catalog level | `beta` (no scheduled `1.0`) |

## Security posture

- Secure defaults: contextual escaping, CSRF, `SafeUrl` / `TrustedHtml`, conservative caches
- Threat model and disclosure: [Security](security.md) · [Threat model](threat-model.md) ·
  [SECURITY.md](../SECURITY.md)
- You own authentication, authorization, and persistence

## Support boundaries

- Community support via GitHub Issues only — **no commercial SLA**
- Supported version lines: see [SECURITY.md](../SECURITY.md)
- Escalate security privately via GitHub security advisories / maintainer contact

## Ops checklist

1. Real `session_secret` (never the development default)
2. `hedron build` then `HEDRON_ENV=production`
3. `explorer="off"` in production
4. HTTPS + sticky sessions or external session store for multi-worker
5. For SSE/WebSocket: confirm reverse-proxy buffering and timeouts (evidence for
   backpressure is still Deferred — see [Performance](performance.md) and STATUS)
6. Pin `hedron` and extras in your lockfile

See [Deployment](deployment.md) · [Error codes](error-codes.md) · [Public roadmap](roadmap.md).
