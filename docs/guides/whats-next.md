# What’s next

Short public list of **planned** versus **not planned as Supported**. The maintainer
ledger (gate IDs, RFCs) lives on GitHub:
[`docs/ROADMAP.md`](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).
Capability maturity for *this* train: [What’s ready](whats-ready.md).
Install pins: [Installation](../getting-started/installation.md).

## Planned after 0.51

| Topic | Disposition |
|---|---|
| Curated extras depth / experimental-UI (0.51) | **Published `v0.51.0` on PyPI** (RFC-0078 / D-087 / D-088; [#507](https://github.com/eddiethedean/hedron/issues/507)); in-tree **`v0.51.2`** ready to cut |
| Conformance kit and Node/Java runtime (0.52) | **Planned** Stage 0 refine vs in-tree `v0.51.2`; owning RFC required; Posit lifecycle [#508](https://github.com/eddiethedean/hedron/issues/508)–[#513](https://github.com/eddiethedean/hedron/issues/513) |
| Application DX contracts (0.53) | **Planned**; owning RFC required; [#514](https://github.com/eddiethedean/hedron/issues/514)–[#521](https://github.com/eddiethedean/hedron/issues/521) |
| Notebook / simulation / sample-kit refresh (0.54) | **Planned**; owning RFC required |
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
