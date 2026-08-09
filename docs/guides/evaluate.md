# Evaluate Hedron

Start here if you are deciding whether Hedron fits. Pick the page that matches your role —
**capability maturity lives only on [What’s ready today](whats-ready.md).**

| Role | Read |
|---|---|
| Product / eng fit | This page (below) · [Why Hedron](why-hedron.md) |
| Capability maturity (SSOT) | [What’s ready today](whats-ready.md) |
| Security / procurement | [Enterprise diligence](enterprise-diligence.md) |
| Ops / ship checklist | [Ship to production](ship-to-production.md) |
| Architecture | [Architecture](../ARCHITECTURE.md) |

Maintainer trust-program depth (not required for a PoC):
[Production-quality maturity](production-quality.md) ·
[Production readiness](production-readiness.md).

## What it is

Hedron is a typed, server-rendered Python UI layer for **FastAPI + HTMX** (with Flask and
Django adapters). It is not a notebook-style rerun engine, SPA framework, ORM, or IdP.
Compare positioning: [Why Hedron](why-hedron.md).

**Skills you need:** comfort with Python 3.11+, basic FastAPI (or Flask/Django), and
HTML forms. HTMX is introduced in
[What is HTMX](../getting-started/what-is-htmx.md) — you do not need a SPA background.

## Version and support

| Item | Value |
|---|---|
| Version | **0.24.0** (Beta; **Published** — pin `hedron>=0.24.0,<0.25`) |
| Python | 3.11–3.14 |
| License | MIT |
| Commercial SLA | **None** — community support via GitHub only |
| Scheduled 1.0 | **None** — expect occasional breaking changes on `0.x` |

## PoC checklist

Timebox a spike before a team commitment. Stop early if a go/no-go row fails.

| Day | Prove | Go if… | No-go if… |
|---|---|---|---|
| **1** | [First app](../getting-started/quickstart.md) — Hello → **Refresh status** | Fragment updates without full reload; clean venv installs | FastAPI/Pydantic pin cannot be met; Refresh never updates |
| **2** | [HTMX](htmx-interactions.md) + [Minimal form](minimal-form.md) | Second region works; `CsrfField` POST increments notes count | CSRF 403 with seeded GET; cannot extend the scaffold |
| **3** | One recipe: [Notes + SQLAlchemy](../examples/notes-sqlalchemy.md) or [Session auth](../examples/session-auth.md) | Persist or gate a page the way your app would | Host/auth model fights Hedron’s request/page model |

**Go (internal admin / CRUD):** pins held, golden path works, recipe matches your host,
[What’s ready](whats-ready.md) Supported rows cover your must-haves, you accept Beta API
churn and polling for live status.

**No-go / defer:** need SLA or scheduled 1.0; need live SSE/WS as Supported; need
human AT evidence as Supported; team will not own FastAPI+HTMX literacy.

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
  (0.24 Accepted **`polling_only`** — those ops IDs are **Superseded**; live helpers stay
  experimental — D-053)
- Specialty extras (CodeEditor host stub, TerminalView, joystick, device bridges) as full
  product UI — Experimental / stub only (quarantine XOR path **0.25**, packet refine
  complete — [PRODUCTION_ARCHETYPE](../api/PRODUCTION_ARCHETYPE.md))
- Human screen-reader / compensated AT evaluation (owned by **0.21**, D-052: protocol Verified;
  sessions Planned — not Supported)
- Broader compatibility-protected `stable` surface beyond the 0.23 CRUD/admin facade
  ([STABLE_FACADE](../api/STABLE_FACADE.md) is Published; live transports remain experimental
  under 0.24 `polling_only`)

## When Hedron is a poor fit

- Pure client-rendered SPA with a separate JS build
- “Every Streamlit widget on day one”
- Requirement for a commercial SLA or guaranteed 1.0 stability date
- Need for a first-party IdP / managed SSO product (optional helpers exist; you still own
  identity — [Authentication](authentication.md))

## Try it

1. [Build your first app](../getting-started/quickstart.md) — Hello → Refresh
2. [What is HTMX](../getting-started/what-is-htmx.md) → [HTMX interactions](htmx-interactions.md)
   → [Minimal form](minimal-form.md)
3. [Try with Codespaces](../examples/try-it.md) (real server in a container — not a playground)
4. [Runnable examples](../examples/runnable.md)

Then: [Ship to production](ship-to-production.md) · [Evidence pack](evidence-pack.md) ·
[Support](support.md).
