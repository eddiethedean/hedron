# What’s next

Short public list of **planned** versus **not planned as Supported**. The maintainer
ledger (gate IDs, RFCs) lives on GitHub:
[`docs/ROADMAP.md`](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).
Capability maturity for *this* train: [What’s ready](whats-ready.md).

**On PyPI today:** latest is **0.45.0**. **This repository** is **0.46.0** (in-tree;
Git tag / PyPI deferred — [#334](https://github.com/eddiethedean/hedron/issues/334)).

## Planned after 0.46

| Topic | Disposition |
|---|---|
| First-class maps (`hedron-maps`, MapLibre, offline tiles) | **0.47 Planned** — no runtime or version claim yet |
| `v0.46.0` Git tag and PyPI upload | Deferred until [#334](https://github.com/eddiethedean/hedron/issues/334) closes |
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
| “Published” on this site meaning “on PyPI” | Packet cut in-tree; PyPI is 0.45.0 until the tag |

## Stay on this train

Pin what the index can resolve. Packages are **Beta**. Prefer [What’s ready](whats-ready.md)
and [Support](support.md) over the full roadmap file.
