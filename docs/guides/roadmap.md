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
| **0.15** | Data-app surface completeness (OIDC/session helpers; HTMX testing; `region`/`swap`; maps/media) | **Published** (`v0.15.0`) |
| **0.16** | Curated extras and analysis workbenches (incl. CodeEditor host stub and specialty NiceGUI-shaped extras) | **Published** (`v0.16.0`) |
| **0.17** | Reactive dashboards and agent interfaces; shell/AppShell; InteractionResult→Response; `#15`/`#24` completions (RFCs 0040–0044) | **Published** (`v0.17.0`) |
| **0.18** | Model demos and inference workflows | **Published** (`v0.18.0`) |
| **0.19** | Accessibility engineering; progressive enhancement; landmark attrs/types; Page PE scripts | **Published** (`v0.19.0`; D-050) |
| **0.20** | Production security floor and adapter parity (HTMX/eval, mount/prod gates, Flask/Django regions/CSP/scaffolds) | **Published** (`v0.20.0`; D-051) |
| **0.21** | Human assistive-technology / compensated evaluation (D-052) | **Published** (`v0.21.0` engineering; PROTOCOL Verified; SR/PARTICIPANT Planned — not Supported) |
| **0.22** | CSRF and SecurityPolicy composition (`CsrfField`, pluggable CSRF, composable headers) | **Published** (`v0.22.0`; D-051) |
| **0.23** | Expand `stable` API tier for narrow CRUD/admin facade (regions/`swap`, Poll/jobs, `CsrfField`/`Form`, beginner chrome, AppScenario asserts) | Planned (D-053; packet refine complete) |
| **0.24** | Live-transport production disposition (prove ops or polling-only) | Planned (D-053) |
| **0.25** | Production archetype, load budgets, extras quarantine | Planned (D-053) |

## What this means for you

- Pin `hedron` (and extras) in production; `0.x` may still take breaking changes under the
  [compatibility policy](../COMPATIBILITY.md).
- Package maturity is **Beta** for the flagship and most adapters; charts remain **Alpha**.
- No `1.0` phase is scheduled (D-038). A **minimal `stable` API tier** is catalogued in
  [STABILITY.md](../api/STABILITY.md); most other public APIs remain `beta` or `experimental`.
- **0.23** (Planned) expands that tier for a locked Beginner/CRUD facade only —
  [STABLE_FACADE](../api/STABLE_FACADE.md) — not every What’s ready Supported row; live
  transports stay for **0.24**.
- Trust-program priorities (human AT → CSRF → stable tier → live disposition → archetype):
  [Production-quality maturity](production-quality.md).

## Honest gaps on the current train (0.22)

- Current **published** PyPI train is **0.22.x** (`v0.22.0`)
- Notebook preview and MCP are **Experimental** / Alpha — deny-by-default / localhost-oriented
- Specialty extras (TerminalView / joystick / device) are **Experimental** — fail-closed
- CodeEditor ships a CSP-safe **host stub** (no pinned CodeMirror 6 bundle)
- Identity helpers are **opt-in wiring** (not a managed IdP) — [Authentication](authentication.md)
- Human screen-reader / compensated AT evaluation — protocol Verified; sessions Planned
  (not Supported); `AT-019` is automated Playwright/axe only
- Full multi-engine adapter live browser matrix → owned `0.11.x` Deferred (`LIVE-011-BROWSER`)
- Full multi-engine FastAPI live browser matrix / some Explorer live traces → owned `0.10.x` Deferred
- Live transports remain **experimental**; polling is Supported — [What’s ready](whats-ready.md)

CSRF / SecurityPolicy composition (#36–#38) shipped in **0.22**
([RELEASE_0_22](../acceptance/RELEASE_0_22.md)). Human AT evaluation engineering is
**0.21** (D-052; sessions outstanding). Stable-tier expansion, live-transport disposition, and
production archetype work are **0.23–0.25** (D-053). Earlier ops honesty items remain under
phases **0.13+** as listed in
the ownership table until 0.24 re-homes them.

The first-party live sample
([`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction))
addresses FastAPI live learning paths. Flask/Django ship capability-labeled live helpers with
polling as the Supported fallback.
Details: [What's ready today](whats-ready.md) · [Production readiness](production-readiness.md) ·
[Production-quality maturity](production-quality.md).
