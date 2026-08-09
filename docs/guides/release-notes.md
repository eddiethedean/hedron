# Release notes

Adopter-facing summary for the **0.23.x** train. For per-package commit detail, use the
[package changelog index](changelog.md) or
[GitHub Releases](https://github.com/eddiethedean/hedron/releases).

## Current train — 0.23.0 (2026-08-08)

**Published** (`0.23.0`; last published PyPI/git = `v0.23.0`).
Stable-tier expansion (D-053): narrow CRUD/admin Beginner facade promoted to API
`stable` ([STABLE_FACADE](../api/STABLE_FACADE.md)), plus fail-closed HTMX region /
CSRF-proxy / mount hardening on the Beta packages. Human AT **sessions**
(`SR-021` / `PARTICIPANT-021`) remain **Planned** — do not market human AT as
Supported (carryover from 0.21).

Narrative deep-dive: [What's new in 0.23](whats-new-0.23.md) · maturity:
[What's ready today](whats-ready.md).

```bash
pip install -U "hedron>=0.23.0,<0.24"
# or
uv add "hedron>=0.23.0,<0.24"
```

Optional: `pip install "hedron[gradio]>=0.1.0,<0.2"` · `"hedron[notebook]>=0.1.0,<0.2"` · `"hedron[mcp]>=0.1.0,<0.2"`.

## Prior — 0.22.0

CSRF / SecurityPolicy composition (D-051): pluggable CSRF strategies, composable
`SecurityHeadersPolicy`, and `CsrfField` / `Form(hx=Hx(...))`. Narrative:
[What's new in 0.22](whats-new-0.22.md).

## Prior — 0.21.0

Human AT protocol engineering (D-052): protocol packet Verified; PE corpus and
adapter fragment allowlist parity. Session gates (`SR-021` / `PARTICIPANT-021` /
`ARTIFACT-021` / `REMEDIATE-021`) remain Planned. Narrative:
[What's new in 0.21](whats-new-0.21.md).
