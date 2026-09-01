# Evaluate Hedron

Start here if you are deciding whether Hedron fits. Pick the page that matches your role —
**adopter maturity summary:** [What’s ready today](whats-ready.md); **full matrices:**
[What’s ready — evidence](whats-ready-evidence.md).

| Role | Read |
|---|---|
| Product / eng fit | This page (below) · [Why Hedron](why-hedron.md) |
| Capability maturity (summary) | [What’s ready today](whats-ready.md) |
| Capability matrices (evidence) | [What’s ready — evidence](whats-ready-evidence.md) |
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
[Ship a Hedron app](ship.md) · [What’s ready](whats-ready.md).

## What it is

Hedron is a server-rendered Python UI layer for **FastAPI + HTMX** (with Flask and
Django adapters). It is not a notebook-style rerun engine, SPA framework, ORM, or IdP.
Compare positioning: [Why Hedron](why-hedron.md).

**Skills you need:** comfort with Python 3.10–3.14 and HTML forms. Basic FastAPI (or
Flask/Django) helps but is not required; [What is HTMX](../getting-started/what-is-htmx.md)
introduces the web concepts as they appear.

## Version and support

| Item | Value |
|---|---|
| Stable version | Verified and published **1.0.5** on the `1.0.x` train |
| Previous train | `v0.67.0` — upgrade and migration baseline |
| Python | 3.10–3.14 |
| License | MIT |
| Commercial SLA | **None** — community support via GitHub only |
| Compatibility | Stable APIs follow the documented 1.x policy |

## PoC checklist

Timebox a spike before a team commitment. Stop early if a go/no-go row fails.

| Day | Prove | Go if… | No-go if… |
|---|---|---|---|
| **1** | [First app](../getting-started/quickstart.md) — Hello → **Refresh status** | Fragment updates without full reload; clean venv installs | FastAPI/Pydantic pin cannot be met; Refresh never updates |
| **2** | [HTMX](htmx-interactions.md) + [Minimal form](minimal-form.md) | Second region works; `CsrfField` POST increments notes count | CSRF 403 with seeded GET; cannot extend the scaffold |
| **3** | One recipe: [Notes + SQLAlchemy](../examples/notes-sqlalchemy.md) or [Session auth](../examples/session-auth.md) | Persist or gate a page the way your app would | Host/auth model fights Hedron’s request/page model |

**Go (internal admin / CRUD):** pins held, golden path works, recipe matches your host,
[What’s ready](whats-ready.md) Supported rows cover your must-haves, and you accept polling
as the conservative live-status default.

**No-go / defer:** need a commercial SLA; need live SSE/WS as Supported; need
human AT evidence as Supported; team will not own FastAPI+HTMX literacy.

## Capability matrix

Use [What’s ready today](whats-ready.md) for the PoC summary, then
[What’s ready — evidence](whats-ready-evidence.md) when you need the full inventory.

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
- Requirement for a commercial SLA
- Need for a first-party IdP / managed SSO product (optional helpers exist; you still own
  identity — [Authentication](authentication.md))

## Try it

1. [Build your first app](../getting-started/quickstart.md) — Hello → Refresh
2. [Minimal form POST](minimal-form.md) — CSRF-safe POST on the same app
3. [What is HTMX?](../getting-started/what-is-htmx.md) — fragment / region mental model
4. [HTMX interactions](htmx-interactions.md) — add a second region
5. [Try with Codespaces](../examples/try-it.md) (real server in a container — not a playground)
6. [Runnable examples](../examples/runnable.md)

Then: [Ship a Hedron app](ship.md) · [Enterprise diligence](enterprise-diligence.md) ·
[Public 1.0 readiness](one-point-zero-readiness.md) ·
[Support](support.md).
