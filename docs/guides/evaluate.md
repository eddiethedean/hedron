# Evaluate Hedron

Short fit check for evaluators. **Capability truth lives only on
[What’s ready today](whats-ready.md)** — use that page for Supported / Deferred detail.

## What it is

Hedron is a typed, server-rendered Python UI layer for **FastAPI + HTMX** (with Flask and
Django adapters). It is not a notebook-style rerun engine, SPA framework, ORM, or IdP.

## Current train

| Item | Value |
|---|---|
| Current train | **0.17.0** (Beta; **Published**) |
| Python | 3.11–3.14 |
| License | MIT |
| Commercial SLA | **None** — community support via GitHub only |
| Scheduled 1.0 | **None** — expect occasional breaking changes on `0.x` |

Pin versions in production. Read [What’s ready](whats-ready.md) before shipping.

## What to use today

See the Supported table on [What’s ready](whats-ready.md). In short: typed pages/fragments,
CSRF profiles, HTMX loops, Flask/Django adapters, optional data/Jinja/dev extras. Charts
are Alpha. Live SSE/WebSocket APIs ship on FastAPI but prefer polling until you have ops
proof.

## What not to depend on yet

See Deferred on [What’s ready](whats-ready.md) — for example full multi-engine live browser
matrix and load/proxy evidence. Prefer Experimental specialty extras only with fail-closed
policies; do not treat them as beachhead Supported UI.

## When Hedron is a poor fit

- Pure client-rendered SPA with a separate JS build
- “Every Streamlit widget on day one”
- Requirement for a commercial SLA or guaranteed 1.0 stability date
- Need for a first-party IdP / managed SSO product (optional `hedron.oidc` /
  `hedron.security` helpers exist, but you still own identity — see
  [Authentication](authentication.md))

## Try it

1. [Installation](../getting-started/installation.md)
2. [Quickstart](../getting-started/quickstart.md)
3. [HTMX interactions](htmx-interactions.md) → [Minimal form](minimal-form.md)
4. [Runnable examples](../examples/runnable.md) / [Try with Codespaces](../examples/try-it.md)

Then: [Why Hedron](why-hedron.md) · [Architecture](../ARCHITECTURE.md) ·
[Production readiness](production-readiness.md) · [Enterprise diligence](enterprise-diligence.md)
