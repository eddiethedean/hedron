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
| **0.25** | Production archetype, load budgets, extras quarantine | **Published** (`v0.25.0`+; last `v0.25.2`; D-053) |
| **0.26** | Production-grade core, FastAPI flagship, and secured/development Explorer | **Published** (`v0.26.0`; D-054) |
| **0.27** | Production-grade data, Flask/Django adapters, HDJ authoring, and curated extras | **Published** (`v0.27.0`; D-055) |
| **0.28** | Production-grade charts and optional native acceleration | **Published** (`v0.28.2`; D-056 / RFC-0059) |
| **0.29** | Production-grade `hedron-workbench` Posit Workbench deployment adapter | **Published** (`v0.29.0`; D-057 / RFC-0062; [#134](https://github.com/eddiethedean/hedron/issues/134)) |
| **0.30** | Standalone `fastapi-workbench` 1.0.0 for plain FastAPI Workbench; `hedron-workbench` depends on it | **Published** (`v0.30.0`; D-058 / RFC-0063; [#135](https://github.com/eddiethedean/hedron/issues/135)) |
| **0.31** | Production-grade conformance/plugin/simulation/notebook tooling, Node/Java evaluators, and a reviewable Streamlit AST migration assistant | **Published** (`v0.31.0`; D-059 / RFC-0064 / RFC-0061; [#87](https://github.com/eddiethedean/hedron/issues/87), [#88](https://github.com/eddiethedean/hedron/issues/88)) |
| **0.32** | Production-grade deny-by-default MCP projection | **Published** (`v0.32.0` / `hedron-mcp` `0.2.0` Beta; D-060 / RFC-0065; [#89](https://github.com/eddiethedean/hedron/issues/89)) |
| **0.33** | Unified `hedron-posit` facade for ordinary Hedron, Posit Workbench, and Posit Connect | **Published** (`v0.33.0` / `hedron-posit` `0.33.0` Beta; D-061 / RFC-0066; [#167](https://github.com/eddiethedean/hedron/issues/167)). Supported cookie bridge dropped after Stage 0. |
| **0.34** | Production-grade Gradio/Hugging Face client interoperability | **Published** (`v0.34.0` / `hedron-gradio` `0.2.0` Beta; D-062 / RFC-0067; [#90](https://github.com/eddiethedean/hedron/issues/90)) |
| **0.35** | Whole-fleet production-grade closure | **Published** (`v0.35.0`; D-063 / RFC-0068; [#91](https://github.com/eddiethedean/hedron/issues/91)) |
| **0.36** | Web Component ABI, state ownership, `hedron-elements`, SSR fallback, and HTMX lifecycle | **Published** (`v0.36.0`; D-064; [#92](https://github.com/eddiethedean/hedron/issues/92)) |
| **0.37** | Async interaction state, form-associated elements, gestures/overlays, semantic primitives, and high-severity remediations #230–#237 / #244 | **Published** (`v0.37.0`; D-065; [#93](https://github.com/eddiethedean/hedron/issues/93)) |
| **0.38** | High-fidelity typed charts: `hedron-chart`, modular D3, SVG/Canvas, visual system, interactions, a11y, export, and hard performance/security gates | Planned Stage 0 (D-066 / RFC-0069) |
| **0.39** | Optimistic mutations and rich data, chart integration, map, media, and editor elements | Planned ([#94](https://github.com/eddiethedean/hedron/issues/94)) |
| **0.40** | React migration matrix, temporary-island boundary, third-party authoring, and interoperability | Planned ([#95](https://github.com/eddiethedean/hedron/issues/95)) |
| **0.41** | Typed browser composition, bounded draft state, and navigation | Planned ([#96](https://github.com/eddiethedean/hedron/issues/96)) |
| **0.42** | Production-grade Web Component platform | Planned; locked Supported inventory only ([#97](https://github.com/eddiethedean/hedron/issues/97)) |

The maintainer roadmap also locks the 2026-08-14 open medium/low remediation snapshot into these
future regression gates: 8 issues in 0.38, 27 in 0.39, 6 in 0.40, 14 in 0.41, and 32 in 0.42.
See the [issue ownership index](../ROADMAP.md#open-mediumlow-remediation-ownership-2026-08-14-snapshot)
for the exact set and phase rationale.

### Cross-cutting default presentation plan (0.33+)

Phases 0.33–0.42 also carry the
[default presentation quality plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/DEFAULT_PRESENTATION_033_PLUS.md): a
framework-owned visual gallery and responsive geometry contract in 0.33, a refreshed polished
`default_styles=True` experience in 0.34, a whole-fleet presentation audit in 0.35, then shared
element, form, chart, data, authoring, navigation, accessibility, performance, and upgrade evidence
through 0.42. This improves Hedron's out-of-box
appearance without copying an application brand, owning authentication policy, or removing
`default_styles=False` for custom canvases. **It does not own phase 0.33 release gates** and must
not delay `hedron-posit` Stage 0 / RFC Accept / Stage 1.

## What this means for you

- Pin `hedron` (and extras) in production; `0.x` may still take breaking changes under the
  [compatibility policy](../COMPATIBILITY.md).
- Package maturity is **Beta** for the flagship, adapters, charts, and native Supported inventories.
- No Hedron `1.0` phase is scheduled (D-038). `fastapi-workbench` 1.0.0 in phase 0.30 is an
  independently versioned package release, not Hedron 1.0. A **minimal + expanded (0.23) `stable` API tier** is
  catalogued in [STABILITY.md](../api/STABILITY.md); most other public APIs remain `beta` or
  `experimental`.
- **0.23** (**Published**) expanded that tier for a locked Beginner/CRUD facade only —
  [STABLE_FACADE](../api/STABLE_FACADE.md) — not every What’s ready Supported row.
- **0.24** (**Published**) Accepted **`polling_only`**: live transports stay
  **experimental**; polling is the Supported production story —
  [LIVE_DISPOSITION](../api/LIVE_DISPOSITION.md).
- Trust-program priorities (human AT → CSRF → stable tier → live disposition → archetype):
  [Production-quality maturity](production-quality.md).
- Planned **0.26–0.35** phases apply an evidence-based production-grade contract to the remaining
  package fleet. **Published 0.36–0.37** and Planned **0.38–0.42** then establish a
  standards-based Web Component platform while preserving SSR, native forms/navigation, HTMX,
  and no-Node Python consumption. Neither program is a blanket feature promotion or a scheduled
  `1.0`; see the
  [maintainer roadmap](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).

## Honest gaps on the current train (0.37.x)

- Current **published** PyPI train is **0.37.x** (last `v0.37.0`)
- Production-grade label applies to declared `hedron-core` / `hedron` /
  `hedron-explorer` (0.26), `hedron-data` / `hedron-flask` / `hedron-django` /
  `hedron-jinja` / `hedron-extras` (0.27), `hedron-charts` / `hedron-native`
  (0.28), and Workbench packages (`hedron-workbench` / `fastapi-workbench` on 0.29–0.30)
  Supported inventories — not every Beta symbol
- Alpha `hedron-elements` ships on the 0.37 train (incubator until 0.42)
- Notebook preview is tooling-grade / localhost-only (0.31); MCP is Beta for the declared
  Supported inventory (`hedron-mcp` `0.2.0`; phase 0.32 / RFC-0065); mutations remain Experimental
- Specialty extras (TerminalView / joystick / device) are **Experimental** — install via
  `hedron[experimental-ui]` (quarantined from `hedron[extras]`)
- CodeEditor ships a CSP-safe **host stub** (no pinned CodeMirror 6 bundle)
- Identity helpers are **opt-in wiring** (not a managed IdP) — [Authentication](authentication.md)
- Human screen-reader / compensated AT evaluation — protocol Verified; sessions Planned
  (not Supported); tracked by [#86](https://github.com/eddiethedean/hedron/issues/86);
  `AT-019` is automated Playwright/axe only
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
