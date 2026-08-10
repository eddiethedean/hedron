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
| **0.23** | Expand `stable` API tier for narrow CRUD/admin facade (regions/`swap`, Poll/jobs, `CsrfField`/`Form`, beginner chrome, AppScenario asserts) | **Published** (`v0.23.0`; D-053) |
| **0.24** | Live-transport production disposition (`polling_only`) | **Published** (`v0.24.0`; D-053) |
| **0.25** | Production archetype, load budgets, extras quarantine | **Published** (`v0.25.0`; D-053) |
| **0.26** | Production-grade core, FastAPI flagship, and secured/development Explorer | Planned; owning RFC/decision required |
| **0.27** | Production-grade data, Flask/Django adapters, HDJ authoring, and curated extras | Planned; depends on 0.26 contract |
| **0.28** | Production-grade charts and optional native acceleration | Planned; conservative Supported subsets only |
| **0.29** | Production-grade conformance, plugin/simulation/notebook tooling, and Node/Java evaluators | Planned; tooling scope remains explicit |
| **0.30** | Production-grade deny-by-default MCP projection | Planned; independent security evidence required |
| **0.31** | Production-grade Gradio/Hugging Face client interoperability | Planned; bounded allowlisted remote access |
| **0.32** | Whole-fleet production-grade closure | Planned; no unowned Alpha package or ambiguous tool disposition |

## What this means for you

- Pin `hedron` (and extras) in production; `0.x` may still take breaking changes under the
  [compatibility policy](../COMPATIBILITY.md).
- Package maturity is **Beta** for the flagship and most adapters; charts remain **Alpha**.
- No `1.0` phase is scheduled (D-038). A **minimal + expanded (0.23) `stable` API tier** is
  catalogued in [STABILITY.md](../api/STABILITY.md); most other public APIs remain `beta` or
  `experimental`.
- **0.23** (**Published**) expanded that tier for a locked Beginner/CRUD facade only —
  [STABLE_FACADE](../api/STABLE_FACADE.md) — not every What’s ready Supported row.
- **0.24** (**Published**) Accepted **`polling_only`**: live transports stay
  **experimental**; polling is the Supported production story —
  [LIVE_DISPOSITION](../api/LIVE_DISPOSITION.md).
- Trust-program priorities (human AT → CSRF → stable tier → live disposition → archetype):
  [Production-quality maturity](production-quality.md).
- Planned **0.26–0.32** phases apply an evidence-based production-grade contract to the remaining
  package fleet. This is not a blanket feature promotion or a scheduled `1.0`; see the
  [maintainer roadmap](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).

## Honest gaps on the current train (0.25)

- Current **published** PyPI train is **0.25.x** (last `v0.25.1`)
- Notebook preview and MCP are **Experimental** / Alpha — deny-by-default / localhost-oriented
- Specialty extras (TerminalView / joystick / device) are **Experimental** — install via
  `hedron[experimental-ui]` (quarantined from `hedron[extras]`)
- CodeEditor ships a CSP-safe **host stub** (no pinned CodeMirror 6 bundle)
- Identity helpers are **opt-in wiring** (not a managed IdP) — [Authentication](authentication.md)
- Human screen-reader / compensated AT evaluation — protocol Verified; sessions Planned
  (not Supported); `AT-019` is automated Playwright/axe only
- Prior live-browser / load Deferred IDs (`LIVE-011-BROWSER`, `BROWSER-10-001`,
  `PERF-10-001`) are **Superseded** by `DECIDE-024` `polling_only`
- Explorer live traces → owned `0.10.x` Deferred (`EXPLORER-10-001`; **not** re-homed to 0.24)
- Live transports remain **experimental**; polling is Supported — [What’s ready](whats-ready.md)
  · [LIVE_DISPOSITION](../api/LIVE_DISPOSITION.md)

CSRF / SecurityPolicy composition (#36–#38) shipped in **0.22**
([RELEASE_0_22](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_22.md)). Human AT evaluation engineering is
**0.21** (D-052; sessions outstanding). Stable-tier expansion shipped in **0.23**;
live-transport disposition shipped in **0.24**; production archetype shipped in **0.25**
(D-053; **Published** `v0.25.0` — [PRODUCTION_ARCHETYPE](../api/PRODUCTION_ARCHETYPE.md)).

The first-party live sample
([`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction))
addresses FastAPI live learning paths. Flask/Django ship capability-labeled live helpers with
polling as the Supported fallback.
Details: [What's ready today](whats-ready.md) · [Production readiness](production-readiness.md) ·
[Production-quality maturity](production-quality.md).
