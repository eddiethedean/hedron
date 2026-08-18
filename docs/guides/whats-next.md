# What’s next

Short public list of **planned** versus **not planned as Supported**. The maintainer
ledger (gate IDs, RFCs) lives on GitHub:
[`docs/ROADMAP.md`](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).
Capability maturity for *this* train: [What’s ready](whats-ready.md).
Install pins: [Installation](../getting-started/installation.md).

## Planned after 0.49

| Topic | Disposition |
|---|---|
| Explorer architecture (0.50) | **Planned** Stage 0 (D-085 / D-086 / RFC-0077); living train stays 0.49.1 |
| Declarative HTMX authoring primitives | **Planned** with 0.50 ([#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500), [#502](https://github.com/eddiethedean/hedron/issues/502), [#503](https://github.com/eddiethedean/hedron/issues/503)); living train stays 0.49.1 |
| Human screen-reader / compensated AT sessions | Protocol exists; **not Supported** until real sessions |
| Live SSE / WebSocket / streaming as production defaults | Stay **experimental**; polling remains Supported |
| Hedron 1.0 / commercial SLA | **None scheduled** |

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
