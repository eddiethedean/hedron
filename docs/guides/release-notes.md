# Release notes

Adopter-facing summary for the **0.24.x** train. For per-package commit detail, use the
[package changelog index](changelog.md) or
[GitHub Releases](https://github.com/eddiethedean/hedron/releases).

## Current train — 0.24.0 (2026-08-09)

**Published** (`0.24.0`; last published PyPI/git = `v0.24.0`).
Live-transport disposition **`polling_only`** (D-053 / RFC-0056): polling is the Supported
production story; SSE / WebSocket / streaming / preload helpers remain **experimental**
(`hedron.experimental`). Prior Deferred live-ops IDs (`BROWSER-10-001`, `PERF-10-001`,
`LIVE-011-BROWSER`) are **Superseded**. Human AT **sessions** (`SR-021` /
`PARTICIPANT-021`) remain **Planned** — do not market human AT as Supported (carryover
from 0.21).

Narrative deep-dive: [What's new in 0.24](whats-new-0.24.md) · maturity:
[What's ready today](whats-ready.md).

```bash
pip install -U "hedron>=0.24.0,<0.25"
# or
uv add "hedron>=0.24.0,<0.25"
```

Optional: `pip install "hedron[gradio]>=0.1.0,<0.2"` · `"hedron[notebook]>=0.1.0,<0.2"` · `"hedron[mcp]>=0.1.0,<0.2"`.

## Prior — 0.23.0

Stable-tier expansion (D-053): narrow CRUD/admin Beginner facade promoted to API
`stable` ([STABLE_FACADE](../api/STABLE_FACADE.md)), plus fail-closed HTMX region /
CSRF-proxy / mount hardening. Narrative: [What's new in 0.23](whats-new-0.23.md).

## Prior — 0.22.0

CSRF / SecurityPolicy composition (D-051): pluggable CSRF strategies, composable
`SecurityHeadersPolicy`, and `CsrfField` / `Form(hx=Hx(...))`. Narrative:
[What's new in 0.22](whats-new-0.22.md).
