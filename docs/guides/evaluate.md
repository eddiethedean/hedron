# Evaluate Hedron

Start here if you are deciding whether Hedron fits. Pick the page that matches your role —
**capability maturity lives only on [What’s ready today](whats-ready.md).**

| Role | Read |
|---|---|
| Product / eng fit | This page (below) · [Why Hedron](why-hedron.md) |
| Capability maturity (authoritative page) | [What’s ready today](whats-ready.md) |
| Security / procurement | [Enterprise diligence](enterprise-diligence.md) |
| Ops / ship checklist | [Ship a Hedron app](ship.md) |
| Maturity vocabulary | [Maturity labels](../getting-started/how-to-read.md) |
| Architecture | [Architecture](../ARCHITECTURE.md) |
| Support / disclosure | [Support](support.md) · [SECURITY](../SECURITY.md) |

**Second-hour path (internal admin):** [Session auth](../examples/session-auth.md) →
[Notes + SQLAlchemy](../examples/notes-sqlalchemy.md) →
[Ship a Hedron app](ship.md). Treat the
[reference app](../examples/reference-app.md) as an optional kitchen sink.

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
| Version | **0.34.x** (Beta; **Published** — pin `hedron>=0.34.0,<0.35`) |
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
- **Charts / sample kit:** pin floors
  `hedron[charts]>=0.34.0,<0.35` and `hedron-sample-kit>=0.1.10,<0.2`
  ([Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor))
- **Pin and expect churn:** notebook / Gradio (Alpha / Experimental). MCP is Beta
  for its Supported inventory (`hedron-mcp` `0.2.0`); mutations remain Experimental.
- **Model demos:** **Supported** capability (fail-closed) via [Model demos](model-demos.md)
  guide snippets — the in-tree evidence app is a stub, not a product demo

Full matrix: [What’s ready](whats-ready.md).

## What not to depend on yet

- Live SSE / WebSocket / streaming as a Supported production default — prefer
  [polling](live-interaction.md); helpers stay under `hedron.experimental`
  ([LIVE_DISPOSITION](../api/LIVE_DISPOSITION.md))
- Specialty extras (CodeEditor host stub, TerminalView, joystick, device bridges) as full
  product UI — Experimental / stub only (`hedron[experimental-ui]` —
  [PRODUCTION_ARCHETYPE](../api/PRODUCTION_ARCHETYPE.md))
- Human screen-reader / compensated AT evaluation as Supported (protocol engineering is on
  the train; sessions are not done yet)
- Broader compatibility-protected `stable` surface beyond the published CRUD/admin facade
  ([STABLE_FACADE](../api/STABLE_FACADE.md); live transports remain experimental)

## When Hedron is a poor fit

- Pure client-rendered SPA with a separate JS build
- “Every Streamlit widget on day one”
- Requirement for a commercial SLA or guaranteed 1.0 stability date
- Need for a first-party IdP / managed SSO product (optional helpers exist; you still own
  identity — [Authentication](authentication.md))

## Try it

1. [What is HTMX?](../getting-started/what-is-htmx.md) — browser / fragment / region mental model
2. [Build your first app](../getting-started/quickstart.md) — Hello → Refresh
3. [HTMX interactions](htmx-interactions.md) → [Minimal form](minimal-form.md)
4. [Try with Codespaces](../examples/try-it.md) (real server in a container — not a playground)
5. [Runnable examples](../examples/runnable.md)

Then: [Ship a Hedron app](ship.md) · [Evidence pack](evidence-pack.md) ·
[Support](support.md).
