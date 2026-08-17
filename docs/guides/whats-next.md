# What’s next

Short public list of **planned** versus **not planned as Supported**. The maintainer
ledger (gate IDs, RFCs) lives on GitHub:
[`docs/ROADMAP.md`](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).
Capability maturity for *this* train: [What’s ready](whats-ready.md).

**Published in-tree `v0.48.0`.** Pin `hedron>=0.48.0,<0.49`. Tag/PyPI deferred; PyPI still `0.46.0`.

## Planned after 0.48

| Topic | Disposition |
|---|---|
| FastAPI/Pydantic convergence | **0.49 Planned** (D-081 / RFC-0076) — requires Verified 0.48 and a tracking issue before Stage 1; no 0.49 runtime |
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
