# Release notes

Adopter-facing summary for the **0.21.x** train. For per-package commit detail, use the
[package changelog index](changelog.md) or
[GitHub Releases](https://github.com/eddiethedean/hedron/releases).

## Current train — 0.21.0 (2026-08-08)

**Published** (`0.21.0`; last published PyPI/git = `v0.21.0`).
Human AT engineering train (D-052): protocol packet Verified, PE corpus, fragment allowlist
parity, DataEditor Escape/403 hardening. **`SR-021` / `PARTICIPANT-021` remain Planned** —
do not market human AT as Supported. CSRF composition → 0.22.

Narrative deep-dive: [What's new in 0.21](whats-new-0.21.md) · maturity:
[What's ready today](whats-ready.md).

```bash
pip install -U "hedron>=0.21.0,<0.22"
# or
uv add "hedron>=0.21.0,<0.22"
```

Optional: `pip install "hedron[gradio]>=0.1.0,<0.2"` · `"hedron[notebook]>=0.1.0,<0.2"` · `"hedron[mcp]>=0.1.0,<0.2"`.
