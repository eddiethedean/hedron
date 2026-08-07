# Evaluate Hedron

Short fit check for evaluators. **Capability truth lives only on
[What’s ready today](whats-ready.md)** — use that page for Supported / Experimental / Alpha detail.

## What it is

Hedron is a typed, server-rendered Python UI layer for **FastAPI + HTMX** (with Flask and
Django adapters). It is not a notebook-style rerun engine, SPA framework, ORM, or IdP.
Compare positioning: [Why Hedron](why-hedron.md).

## Version and support

| Item | Value |
|---|---|
| Version | **0.20.0** (Beta; Published — pin for production; last published PyPI = `0.20.0`) |
| Python | 3.11–3.14 |
| License | MIT |
| Commercial SLA | **None** — community support via GitHub only |
| Scheduled 1.0 | **None** — expect occasional breaking changes on `0.x` |

## What to use today

- **Ship:** typed pages/fragments, CSRF profiles, HTMX loops, Flask/Django adapters,
  optional `hedron[data]` / `hedron[jinja]` / `hedron[dev]`, polling job status
- **Prefer polling:** live SSE / WebSocket (`hedron.experimental`)
- **Pin and expect churn:** `hedron[charts]` (Alpha), notebook / MCP / Gradio (Alpha / Experimental)
- **Model demos:** **Supported** capability (fail-closed) on the Beta package train —
  [Model demos](model-demos.md)

Full matrix: [What’s ready](whats-ready.md).

## What not to depend on yet

- Full multi-engine live browser matrix and load/proxy backpressure proof for live transports
- Specialty extras (TerminalView, joystick, device bridges) as production UI —
  Experimental only with fail-closed policies

## When Hedron is a poor fit

- Pure client-rendered SPA with a separate JS build
- “Every Streamlit widget on day one”
- Requirement for a commercial SLA or guaranteed 1.0 stability date
- Need for a first-party IdP / managed SSO product (optional `hedron.oidc` /
  `hedron.security` helpers exist, but you still own identity — see
  [Authentication](authentication.md))

## Try it

1. [Build your first app](../getting-started/quickstart.md) — Hello → Refresh
2. [HTMX interactions](htmx-interactions.md) → [Minimal form](minimal-form.md)
3. [Installation](../getting-started/installation.md) — extras / troubleshooting as needed
4. [Runnable examples](../examples/runnable.md) / [Try with Codespaces](../examples/try-it.md)

Then: [Why Hedron](why-hedron.md) · [Architecture](../ARCHITECTURE.md) ·
[Production readiness](production-readiness.md) · [Enterprise diligence](enterprise-diligence.md)
