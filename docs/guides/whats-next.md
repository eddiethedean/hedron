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

## On the living 0.59 train

| Topic | Disposition |
|---|---|
| Progressive screens / form commands / TaskFlow / DashboardWorkspace | **Published** on PyPI (`v0.59.0`) — [What’s new in 0.59](whats-new-0.59.md) |
| Human screen-reader / compensated AT sessions | Protocol exists; **not Supported** until real sessions |
| Live SSE / WebSocket / streaming as production defaults | Stay **experimental**; polling remains Supported |
| Hedron 1.0 / commercial SLA | **None scheduled** |

## Published 0.59 — modern CSS platform

Phase 0.59 is published. Capability-specific Required, Progressive, Experimental, and Deferred
boundaries remain explicit in the [Modern CSS guide](modern-css-0.59.md).

| Topic | Disposition |
|---|---|
| Scoped CSS compiler, cascade, tokens, Theme variants, modern color/type | **Published in 0.59** — [Modern CSS in 0.59](modern-css-0.59.md) |
| Container-aware layout, print/RTL/preferences, overlays and motion fallbacks | **Published in 0.59** with Required/Progressive/Experimental tiers and tested fallbacks |
| Typed control attributes/sizing, AppShell chrome, pipeline/run presentation | **Published in 0.59** from the [consumer issue fixtures](https://github.com/eddiethedean/user-token-management-app/issues) |
| Free-form CSS-in-Python, mandatory Node, automatic remote fonts | **Not planned**; use finite semantic APIs plus component `styles.css` and explicit local assets |

## Proposed 0.60 — custom themes and styling completion

Phase 0.60 is draft planning, not a Supported or shipped claim.

| Topic | Disposition |
|---|---|
| Typed modern color, canonical ThemeSpec/ThemePatch, registry-derived contracts/profiles, fingerprints, data-only packages | **Proposed for 0.60** — [RFC-0089](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0089-CUSTOM-THEME-PLATFORM.md) |
| Forced-color/contrast modes, extensible recipes, explicit scoped defaults | **Proposed for 0.60**, gated by accessibility and explicit-value proofs |
| Persisted no-flash theme picker and reviewed built-in theme families | **Proposed for 0.60** with server/application authority retained |
| Theme Lab and third-party declared-profile conformance kit | **Proposed for 0.60** through shared read-only validation services |
| Brand, ToastHost, ConnectorFlow, and semantic ScrollRegion gaps | **Proposed for 0.60** through Hedron #627–#630 |
| Runtime visual editor, remote theme marketplace, round-trip token interchange, health score, arbitrary CSS-in-Python | **Not planned for 0.60** |

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
