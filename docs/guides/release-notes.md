# Release notes

Adopter-facing summary for the **0.26.x** train. For per-package commit detail, use the
[package changelog index](changelog.md) or
[GitHub Releases](https://github.com/eddiethedean/hedron/releases).

## Current train — 0.26.0 (2026-08-10)

**Published** (`0.26.0`; last published PyPI/git = `v0.26.0`).

**Adopter highlights:** production-grade graduation for `hedron-core`, `hedron`, and
`hedron-explorer` on the declared Supported CRUD/admin inventory (D-054 / RFC-0057):
machine-readable inventory, `v0.25.2` upgrade fixtures, secured Explorer evidence,
FastAPI multi-worker archetype proof, and REVIEW-026 security disposition. Polling
remains the Supported live-status story (from 0.24). Human AT **sessions** remain
**Planned** — do not market human AT as Supported. Pin `hedron>=0.26.0,<0.27`. Charts
extra: `hedron[charts]>=0.26.0,<0.27`.

Narrative: [What's new in 0.26](whats-new-0.26.md) · maturity:
[What's ready today](whats-ready.md) · ship checklist:
[Ship a Hedron app](ship.md) · pin / Release assets:
[Release summary (adopters)](release-adopters.md).

```bash
pip install -U "hedron>=0.26.0,<0.27"
# or
uv add "hedron>=0.26.0,<0.27"
```

Optional: `pip install "hedron[gradio]>=0.1.0,<0.2"` · `"hedron[notebook]>=0.1.0,<0.2"` · `"hedron[mcp]>=0.1.0,<0.2"`.

## Prior — 0.25.2 (2026-08-10)

**Published** (`0.25.2`). CSRF / HTMX adapter fixes, trust-boundary hardening, Redis
job/status CAS, fail-closed adapter prepare / SSE framing.

## Prior — 0.25.1 (2026-08-09)

**Published** (`0.25.1`). Restores installable charts with `hedron-charts 0.1.6`, recipe
fixes for session-auth / SQLAlchemy notes, release-publish hardening, and expanded
adoption / Streamlit migration docs.

## Prior — 0.25.0 (2026-08-09)

**Published** (`0.25.0`). Production kitchen-sink reference app, CI critical-path budgets,
experimental UI isolation (`hedron[experimental-ui]`), Matplotlib-default charts path,
SBOM/evidence attach on train tags.

## Prior — 0.24.0

Live-transport disposition **`polling_only`**: polling is the Supported production story;
SSE / WebSocket / streaming / preload helpers remain **experimental**
(`hedron.experimental`). Prior Deferred live-ops IDs (`BROWSER-10-001`, `PERF-10-001`,
`LIVE-011-BROWSER`) are **Superseded**. Narrative:
[What's new in 0.24](whats-new-0.24.md).

## Prior — 0.23.0

Stable-tier expansion (D-053): narrow CRUD/admin Beginner facade promoted to API
`stable` ([STABLE_FACADE](../api/STABLE_FACADE.md)), plus fail-closed HTMX region /
CSRF-proxy / mount hardening. Narrative: [What's new in 0.23](whats-new-0.23.md).

## Prior — 0.22.0

CSRF / SecurityPolicy composition (D-051): pluggable CSRF strategies, composable
`SecurityHeadersPolicy`, and `CsrfField` / `Form(hx=Hx(...))`. Narrative:
[What's new in 0.22](whats-new-0.22.md).

## Prior — 0.21.0

Human AT protocol engineering on the train; compensated screen-reader sessions remain
Planned. `@action` / component fragment-region parity. Narrative:
[What's new in 0.21](whats-new-0.21.md).
