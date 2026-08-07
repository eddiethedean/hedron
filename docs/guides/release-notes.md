# Release notes

Adopter-facing summary for the **0.20.x** train. For per-package commit detail, use the
[package changelog index](changelog.md) or
[GitHub Releases](https://github.com/eddiethedean/hedron/releases).

## Current train — 0.20.0 (2026-08-07)

**Ready to cut / Implemented on `main`** (`0.20.0`; last published PyPI/git = `v0.18.0`).
Production security floor and adapter parity: HTMX browser presets, Python `js:` reject,
mount-path helpers, production startup gates, Flask/Django fragment regions / CSP headers /
Flask-Login AuthSignal, `hedron new --flask/--django`, adapter wheel smoke (D-051).
CSRF composition → 0.22; human AT → 0.21.

Narrative deep-dive: [What's new in 0.20](whats-new-0.20.md) · maturity:
[What's ready today](whats-ready.md).

```bash
pip install -U "hedron>=0.20.0,<0.21"
# or
uv add "hedron>=0.20.0,<0.21"
```

Optional: `pip install "hedron[gradio]>=0.1.0,<0.2"` · `"hedron[notebook]>=0.1.0,<0.2"` · `"hedron[mcp]>=0.1.0,<0.2"`.

## Earlier trains

| Train | Summary | Narrative |
|---|---|---|
| **0.18** | Model demos / inference workflows | [What's new in 0.18](whats-new-0.18.md) |
| **0.17** | Reactive dashboards / agent interfaces | [What's new in 0.17](whats-new-0.17.md) |
| **0.16** | Curated extras / workbenches | [What's new in 0.16](whats-new-0.16.md) |
| **0.15** | Data-app surface completeness | [What's new in 0.15](whats-new-0.15.md) |
| **0.14** | Portable runtimes / acceleration | [What's new in 0.14](whats-new-0.14.md) |
| **0.13–0.10** | Async/observability → live interaction | Archive links in nav / [changelog](changelog.md) |

Upgrade paths: [Upgrade guide](upgrade.md) (0.8 → 0.19).
