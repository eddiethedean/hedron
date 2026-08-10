# Release notes

Adopter-facing summary for the **0.25.x** train. For per-package commit detail, use the
[package changelog index](changelog.md) or
[GitHub Releases](https://github.com/eddiethedean/hedron/releases).

## Prepared patch — 0.25.1 (not yet tagged)

- Restores installable charts with `hedron-charts 0.1.6` and a safe lower bound in
  `hedron[charts]`.
- Fixes session-auth feedback and malformed input handling in adopter recipes.
- Repairs documentation simulator tests and formatting drift.
- Prevents GitHub Release creation when any PyPI package publish fails.
- Expands the adoption and Streamlit migration documentation added after 0.25.0.

The last published release remains `v0.25.0` until the tag workflow completes.

## Current train — 0.25.0 (2026-08-09)

**Published** (`0.25.0`; last published PyPI/git = `v0.25.0`).

**Adopter highlights:** production kitchen-sink reference app, CI critical-path budgets,
experimental UI isolation (`hedron[experimental-ui]`), Matplotlib-default charts path,
SBOM/evidence attach on train tags. Polling remains the Supported live-status story
(from 0.24). Human AT **sessions** remain **Planned** — do not market human AT as
Supported.

Narrative: [What's new in 0.25](whats-new-0.25.md) · maturity:
[What's ready today](whats-ready.md) · ship checklist:
[Ship a Hedron app](ship.md) · pin / Release assets:
[Release summary (adopters)](release-adopters.md).

```bash
pip install -U "hedron>=0.25.0,<0.26"
# or
uv add "hedron>=0.25.0,<0.26"
```

Optional: `pip install "hedron[gradio]>=0.1.0,<0.2"` · `"hedron[notebook]>=0.1.0,<0.2"` · `"hedron[mcp]>=0.1.0,<0.2"`.

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
