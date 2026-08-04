# Release notes

Train-level summary for the published **0.10.x** line. Package changelogs remain the
detailed record; this page is the adopter-facing index.

## Current train — 0.10.1 (2026-08-04)

Security and correctness patch on the 0.10 capability train.

**Highlights (all packages on `0.10.1`):**

- Fail-closed caching (`vary_on` for default private `cache_data` scopes)
- Safer redirects (reject credentialed URLs in `redirect_external`)
- Hardened live-transport headers (SSE / stream / preload control-character checks)
- Job SSE and poll status share authz (403/404) and sanitize bad `Last-Event-ID`

Narrative: [What’s new in 0.10.1](whats-new-0.10.1.md) · maturity:
[What’s ready today](whats-ready.md).

Install: `pip install -U "hedron>=0.10.1"` (or `uv add "hedron>=0.10.1"`).

## 0.10.0 — live interaction phase

Official SSE helpers, focused streaming, WebSocket page/session channels, navigation
preload, Chat/Dialog surfaces, and bundled HTMX SSE/head-support extensions.

Narrative: [What’s new in 0.10](whats-new-0.10.md) · [Upgrade (0.8 → 0.10)](upgrade.md).

## Package changelogs (GitHub)

- [hedron](https://github.com/eddiethedean/hedron/blob/main/packages/hedron/CHANGELOG.md)
- [hedron-core](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-core/CHANGELOG.md)
- [hedron-data](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-data/CHANGELOG.md)
- [hedron-charts](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-charts/CHANGELOG.md)
- [hedron-flask](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-flask/CHANGELOG.md)
- [hedron-django](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-django/CHANGELOG.md)
- [hedron-jinja](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-jinja/CHANGELOG.md)
- [hedron-explorer](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-explorer/CHANGELOG.md)

GitHub Releases: [eddiethedean/hedron/releases](https://github.com/eddiethedean/hedron/releases).
