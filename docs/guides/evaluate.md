# Evaluate Hedron

Start here if you are deciding whether Hedron fits. Pick the page that matches your role —
**capability maturity lives only on [What’s ready today](whats-ready.md).**

| Role | Read |
|---|---|
| Product / eng fit | This page (below) · [Why Hedron](why-hedron.md) |
| Capability maturity (SSOT) | [What’s ready today](whats-ready.md) |
| Security / procurement | [Enterprise diligence](enterprise-diligence.md) |
| Ops / ship checklist | [Production readiness](production-readiness.md) |
| Architecture | [Architecture](../ARCHITECTURE.md) |

## What it is

Hedron is a typed, server-rendered Python UI layer for **FastAPI + HTMX** (with Flask and
Django adapters). It is not a notebook-style rerun engine, SPA framework, ORM, or IdP.
Compare positioning: [Why Hedron](why-hedron.md).

## Version and support

| Item | Value |
|---|---|
| Version | **0.20.0** (Beta; **Published** — pin `hedron>=0.20.0,<0.21`) |
| Python | 3.11–3.14 |
| License | MIT |
| Commercial SLA | **None** — community support via GitHub only |
| Scheduled 1.0 | **None** — expect occasional breaking changes on `0.x` |

## What to use today

- **Ship:** typed pages/fragments, CSRF profiles, HTMX loops, Flask/Django adapters,
  optional `hedron[data]` / `hedron[jinja]` / `hedron[dev]`, polling job status
- **Prefer polling:** live SSE / WebSocket (`hedron.experimental`)
- **Pin and expect churn:** `hedron[charts]` (Alpha), notebook / MCP / Gradio (Alpha / Experimental)
- **Model demos:** **Supported** capability (fail-closed) via [Model demos](model-demos.md)
  guide snippets — the in-tree evidence app is a stub, not a product demo

Full matrix: [What’s ready](whats-ready.md).

## What not to depend on yet

- Full multi-engine live browser matrix and load/proxy backpressure proof for live transports
- Specialty extras (CodeEditor host stub, TerminalView, joystick, device bridges) as full
  product UI — Experimental / stub only
- Human screen-reader / compensated AT evaluation (owned by **0.21**, D-052 engineering-complete /
  sessions outstanding)

## When Hedron is a poor fit

- Pure client-rendered SPA with a separate JS build
- “Every Streamlit widget on day one”
- Requirement for a commercial SLA or guaranteed 1.0 stability date
- Need for a first-party IdP / managed SSO product (optional helpers exist; you still own
  identity — [Authentication](authentication.md))

## Try it

1. [Build your first app](../getting-started/quickstart.md) — Hello → Refresh
2. [HTMX interactions](htmx-interactions.md) → [Minimal form](minimal-form.md)
3. [Try with Codespaces](../examples/try-it.md) (real server in a container — not a playground)
4. [Runnable examples](../examples/runnable.md)

Then: [Evidence pack](evidence-pack.md) · [Support](support.md).
