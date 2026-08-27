# What’s next

Short public list of **planned** versus **not planned as Supported**. Adopters: stay on
this page. The long maintainer ledger (gate IDs, RFCs, phase archaeology) lives on GitHub
only:
[`docs/ROADMAP.md`](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md) —
it is **not** an adoption guide.

Capability maturity for *this* train: [What’s ready](whats-ready.md) ·
[evidence](whats-ready-evidence.md).
Install pins: [Current release](current-release.md) ·
[Installation](../getting-started/installation.md).

## Stable 0.66.2 and Beta 0.67.0

| Topic | Disposition |
|---|---|
| Progressive screens / form commands / TaskFlow / DashboardWorkspace | **Available in published 0.60.2** — [What’s new in 0.60](whats-new-0.60.md) |
| Human screen-reader / compensated AT sessions | Protocol exists; **not Supported** until real sessions |
| Live SSE / WebSocket / streaming as production defaults | Stay **experimental**; polling remains Supported |
| Hedron 1.0 / commercial SLA | **None scheduled** |

## Proposed phases after 0.60

| Phase | Focus | Status |
|---|---|---|
| **0.61** | Unified action state and server-first async boundaries | **Verified and published in 0.61.0**; [phase plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/ACTION_STATE_ASYNC_061.md) |
| **0.62** | Responsive navigation, bounded optimistic UX, and localized failure isolation | **Published** as `v0.62.0`; dashboard fan-out omitted; [phase plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/NAVIGATION_OPTIMISM_062.md) |
| **0.63** | Theme contract completion, interaction profiling, static checks, and component interoperability | **Published** as `v0.64.0`; Progressive bundles/visuals/React island deferred; [phase plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/INTERACTION_TOOLING_063.md) |
| **0.64** | Bounded presentation contracts and first-party HTMX lifecycle interoperability | Published `v0.64.0`; 18 enhancement issues completed, 4 remain open for deferred follow-up; [phase inventory](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md#phase-064-enhancement-inventory); [refined phase plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HTMX_HEDRON_EXTENSION_064.md) |
| **0.65** | Integrated styling platform and first-class application CSS | **Proposed; not a current release**; four bounded open-issue slices plus public hooks, app assets, tokens, diagnostics, ejection, and touched-surface fallbacks; [phase plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/APPLICATION_STYLING_065.md) · [refined scope](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/application-styling-scope-065.md) |
| **0.66** | HDJ parity, registry integration, and open-issue closure | **Stable** as `v0.66.2`; [phase plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HDJ_PARITY_066.md) |
| **0.67** | Alpine browser-local enhancement and unified interaction preview | **Beta** as `v0.67.0`; [phase plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/ALPINE_INTEGRATION_067.md) |

Phase 0.66 is the current stable capability train and is published on PyPI as `v0.66.2`.
Phase 0.67 is the Beta preview train (`v0.67.0`) and does not change the stable Supported surface.
For 0.62, canonical navigation, fallback, localized failure, identity safety, and a small approved
optimistic core are the proposed Required cut; prefetch, transitions, bulk actions, and dashboard
fan-out remain optional Progressive work.
Their shared purpose is to make Hedron's existing forms, actions, jobs, fragments, Web Components,
optimistic mutations, and Explorer feel like one interaction platform while preserving server
authority, progressive enhancement, and no-Node Python consumption. See the [implementation
plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/REACTIVE_INTERACTION_PLATFORM_061_063.md)
and [acceptance rules](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/REACTIVE_INTERACTION_PHASES_061_063.md).
Every phase has an independent entry gate, workstreams, compatibility/rollback rules, budget
categories, and release plan.

Phase 0.64 extends that program with bounded presentation contracts and an explicitly declared,
locally served `htmx-ext-hedron` asset. It adds theme scales, public parts/states, responsive and
inclusive presentation, safe custom-component styling, and Hedron-specific browser lifecycle
projection while keeping ordinary HTMX and full-page/full-fragment behavior as the fallback. It
does not introduce a client store, hydration, a virtual DOM, arbitrary CSS/script execution, or a
Node requirement.

Phase 0.65 continues the same styling authority instead of creating a second CSS language. It makes
local application CSS a declared asset, adds an explicit application cascade layer and namespaced
tokens, stabilizes public component hooks, and provides explain/check/eject workflows. Its four
open issues are required inputs; unsupported surfaces retain explicit fallbacks and honest maturity
labels.

## Verified 0.60 — custom theme platform and styling completion

Phase 0.61 is implemented and verified in-tree. Capability-specific Required, Progressive,
Experimental, and Deferred boundaries remain explicit in the [release notes](release-notes.md).

| Topic | Disposition |
|---|---|
| ThemeSpec/ThemePatch, color handling, profiles, packages, accessibility modes, ThemePicker, and Theme Lab | **Verified and published in 0.60.2** |
| Scoped CSS compiler, cascade, tokens, Theme variants, modern color/type/media | **Verified in 0.62 checkout** with bounded fallback behavior |
| Brand, ToastHost, ConnectorFlow, and ScrollRegion zero-application-CSS contracts | **Verified in 0.62 checkout** from the phase gate fixtures |
| Free-form CSS-in-Python, mandatory Node, automatic remote fonts | **Not planned**; use finite semantic APIs plus component `styles.css` and explicit local assets |

## Deferred and excluded

The runtime visual editor, remote theme marketplace, round-trip token interchange, aggregate health
score, and arbitrary CSS-in-Python remain outside 0.60. Human assistive-technology sign-off remains
open and is not represented as completed evidence.

## Not a current production default

| Topic | Use instead |
|---|---|
| SSE / WebSocket job status | [Polling](live-interaction.md) |
| Plotly / Altair as Supported charts | First-party `hedron[charts]` |
| Portable `csrf_token` on stock Django POST | `csrfmiddlewaretoken` |
| Ambient `HEDRON_SESSION_SECRET` loading | Pass `session_secret=` into `Hedron` — [Secrets and workers](secrets-and-workers.md) |
| Multi-worker in-memory jobs | Shared Redis / Celery / RQ + sticky sessions or a shared session store |

## Stay on this train

Pin what the index can resolve. Packages are **Beta**. Prefer [What’s ready](whats-ready.md)
and [Support](support.md) over the full roadmap file.
