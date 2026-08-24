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

## On the living 0.62 train

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
| **0.63** | Theme contract completion, interaction profiling, static checks, and component interoperability | Required implementation landed; Progressive bundles/visuals/React island deferred; [phase plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/INTERACTION_TOOLING_063.md) |
| **0.64** | First-party Hedron HTMX extension for lifecycle state, accessibility, cleanup, and traces | Proposed / Stage 0 planned; [phase plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HTMX_HEDRON_EXTENSION_064.md) |

Phase 0.62 remains the current published capability train; 0.63 Required implementation is landed
in-tree with its acceptance packet, while 0.64 remains a planning proposal.
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

Phase 0.64 extends that program with an explicitly declared, locally served `htmx-ext-hedron` asset.
It adds Hedron-specific browser lifecycle and accessibility projection while keeping ordinary HTMX
and full-page/full-fragment behavior as the fallback. It does not introduce a client store,
hydration, a virtual DOM, or a Node requirement.

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
