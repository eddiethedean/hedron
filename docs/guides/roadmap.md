# Roadmap (public)

Capability phases for adopters. The full phase tables, gates, and RFC ownership live
in the [maintainer roadmap](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).

| Phase | Theme | Status |
|---|---|---|
| **0.10** | Live interaction on FastAPI (SSE, streaming, WebSockets, Chat/Dialog, preload) | Published (`v0.10.x`) |
| **0.11** | Native Flask/Django depth; bounded QuerySet integration | **Published** (`v0.11.0`) |
| **0.12** | Data and visualization scale | **Published** (`v0.12.0`) |
| **0.13** | Advanced async, observability, job durability, diagnostics | **Published** (`v0.13.0`) |
| **0.14** | Portable runtimes and acceleration | **Published** (`v0.14.0`) |
| **0.15** | Data-app surface completeness (OIDC/session helpers; HTMX testing; `region`/`swap`; maps/media) | **Implemented** (`v0.15.0`, pending cut) |
| **0.16** | Curated extras and analysis workbenches (incl. CodeEditor and specialty NiceGUI-shaped extras) | **Implemented** (`v0.16.0`, pending cut) |
| **0.17** | Reactive dashboards and agent interfaces | Planned |
| **0.18** | Model demos and inference workflows | Planned |
| **0.19** | Accessibility engineering; progressive enhancement | Planned |
| **0.20** | Production security floor and adapter parity | Planned (new) |

## What this means for you

- Pin `hedron` (and extras) in production; `0.x` may still take breaking changes under the
  [compatibility policy](../COMPATIBILITY.md).
- Package maturity is **Beta** for the flagship and most adapters; charts remain **Alpha**.
- No `1.0` phase is scheduled (D-038). A **minimal `stable` API tier** is catalogued in
  [STABILITY.md](../api/STABILITY.md); most other public APIs remain `beta` or `experimental`.

## Honest gaps on the current train (0.16 pending cut)

- Last **published** PyPI train remains **0.14.x** until `v0.16.0` (or stepped `v0.15.0`) is tagged
- Specialty extras (TerminalView / joystick / device) are **Experimental** — fail-closed
- Identity helpers are **opt-in wiring** (not a managed IdP) — [Authentication](authentication.md)
- Full multi-engine adapter live browser matrix → owned `0.11.x` Deferred (`LIVE-011-BROWSER`)
- Full multi-engine FastAPI live browser matrix / some Explorer live traces → owned `0.10.x` Deferred
- Live transports remain **experimental**; polling is Supported — [What’s ready](whats-ready.md)

Tracked follow-ups for host security, adapter DX, and claim honesty are owned by
phases **0.13+** (see the [issue ownership table](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md#open-github-issue-ownership-013)
in the maintainer roadmap).

The first-party live sample
([`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction))
addresses FastAPI live learning paths. Flask/Django ship capability-labeled live helpers with
polling as the Supported fallback.
Details: [What's ready today](whats-ready.md) · [Production readiness](production-readiness.md).
