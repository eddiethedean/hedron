---
description: Choose a verified Edron example by outcome and difficulty.
---

# Edron examples

Every example on this page targets Edron 1.0 and uses the same native Hedron runtime.

| Outcome | Start with | Difficulty | Time | What it proves |
|---|---|---:|---:|---|
| First complete page | [Edron quick start](../getting-started/edron-quickstart.md) | Beginner | 5 min | Scaffold, page composition, reload |
| Dashboard | `edron new sales --template dashboard` | Beginner | 10 min | Metrics, layout, charts |
| CRUD application | `edron new inventory --template crud` | Intermediate | 20 min | Typed inputs, actions, data workspace |
| Durable task UI | `edron new worker-ui --template task` | Intermediate | 20 min | Job flow and polling status |
| Streamlit assessment | [Migration guide](../guides/streamlit-migration.md) | Intermediate | 30 min | Static, review-first migration |

## Verify a scaffold

```bash
uvx --from "edron>=1.0.0,<1.1" edron new inventory --template crud
cd inventory
uv sync
uv run edron check app.py
uv run edron run app:app --reload
```

Before deployment, replace scaffold secrets, connect application-owned persistence and
authorization, choose shared state/job backends for multiple workers, and run
`edron doctor app:app --profile container`.

For lower-level host and component examples, continue to the
[Hedron example catalog](index.md).
