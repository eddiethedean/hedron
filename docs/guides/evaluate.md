# Evaluate Hedron

One page for evaluators and enterprise reviewers. Details live in linked guides.

## What it is

Hedron is a typed, server-rendered Python UI layer for **FastAPI + HTMX** (with Flask and
Django adapters). It is not a notebook-style rerun engine, SPA framework, ORM, or IdP.

## Current train

| Item | Value |
|---|---|
| Published train | **0.10.1** (Beta packages) |
| Python | 3.11–3.14 |
| License | MIT |
| Commercial SLA | **None** — community support via GitHub only |
| Scheduled 1.0 | **None** — expect occasional breaking changes on `0.x` |

Pin versions in production. Read [What’s ready today](whats-ready.md) and
[Production readiness](production-readiness.md) before shipping.

## Support and security

- Support boundaries: [Support](support.md)
- Disclosure and supported lines: [SECURITY.md](../SECURITY.md)
- Threat model and secure defaults: [Security](security.md) · [Threat model](threat-model.md)
- Compatibility / deprecation: [COMPATIBILITY.md](../COMPATIBILITY.md)

## What to use today

- Typed pages/fragments, CSRF profiles, CLI, testing helpers (FastAPI flagship)
- HTMX fragment loops and `InteractionResult`
- Live helpers on FastAPI (SSE, streaming, WebSocket channels, Chat/Dialog, preload) —
  **API Supported**; full live browser matrix and load/proxy evidence remain Deferred
  (see [What’s ready](whats-ready.md) and [What's ready](whats-ready.md))
- Flask / Django adapters on the Supported matrix
- Optional `hedron[data]`, `hedron[jinja]`, `hedron[dev]`; charts are **Alpha**

## What not to depend on yet

See Deferred rows in [What’s ready](whats-ready.md)—including Django QuerySet as a
first-party DataSource and Hedron-owned Django forms (planned **0.11**).

## When Hedron is a poor fit

- Pure client-rendered SPA with a separate JS build
- “Every Streamlit widget on day one”
- Requirement for a commercial SLA or guaranteed 1.0 stability date

## Try it

1. [Installation](../getting-started/installation.md)
2. [Quickstart](../getting-started/quickstart.md)
3. [HTMX interactions](htmx-interactions.md)
4. [Minimal form](minimal-form.md)
5. [Learning path](../getting-started/learning-path.md)
6. [Runnable examples](../examples/runnable.md) / [Try with Codespaces](../examples/try-it.md)

Then: [Why Hedron](why-hedron.md) · [Architecture](../ARCHITECTURE.md) ·
[Public roadmap](roadmap.md)
