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

## On the living 0.60 train

| Topic | Disposition |
|---|---|
| Progressive screens / form commands / TaskFlow / DashboardWorkspace | **Available in the verified 0.60 checkout**; PyPI upload remains deferred — [What’s new in 0.60](whats-new-0.60.md) |
| Human screen-reader / compensated AT sessions | Protocol exists; **not Supported** until real sessions |
| Live SSE / WebSocket / streaming as production defaults | Stay **experimental**; polling remains Supported |
| Hedron 1.0 / commercial SLA | **None scheduled** |

## Verified 0.60 — custom theme platform and styling completion

Phase 0.60 is implemented and verified in-tree. Capability-specific Required, Progressive,
Experimental, and Deferred boundaries remain explicit in the [release notes](release-notes.md).

| Topic | Disposition |
|---|---|
| ThemeSpec/ThemePatch, typed colors, profiles, packages, accessibility modes, ThemePicker, and Theme Lab | **Verified in 0.60 checkout**; public PyPI upload deferred |
| Scoped CSS compiler, cascade, tokens, Theme variants, modern color/type/media | **Verified in 0.60 checkout** with bounded fallback behavior |
| Brand, ToastHost, ConnectorFlow, and ScrollRegion zero-application-CSS contracts | **Verified in 0.60 checkout** from the phase gate fixtures |
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
