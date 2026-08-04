# Production readiness

One-page evaluator summary for the published **0.10.0** train. Details:
[What's ready today](whats-ready.md) · [Compatibility](../COMPATIBILITY.md) ·
[Support](support.md).

## What you can ship today (Beta)

- Typed pages/fragments, FastAPI routing, CSRF profiles, CLI, testing helpers
- HTMX fragment loops and `InteractionResult`
- Live helpers on FastAPI (SSE, streaming, WebSocket channels, Chat/Dialog, preload)
- Flask / Django adapters on the Supported matrix
- Optional HDJ (`hedron[jinja]`), DataTable/DataEditor (`hedron[data]`), Explorer (`hedron[dev]`)

Pin package versions. Breaking changes may still land on `0.x`.

## What remains volatile or incomplete

| Area | Status |
|---|---|
| `hedron-charts` | Alpha |
| First-party live-transport sample app | Deferred (`EXAMPLES-10-001`) |
| Django QuerySet DataSource / Hedron Django forms | Planned **0.11** |
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
5. Pin `hedron` and extras in your lockfile

See [Deployment](deployment.md) · [Error codes](error-codes.md) · [Public roadmap](roadmap.md).
