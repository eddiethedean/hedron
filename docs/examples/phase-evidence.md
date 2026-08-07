# Phase evidence (0.15–0.18)

These directories are **capability-phase exit scenarios** for maintainers and evaluators.
They are runnable stubs that prove a release gate — **not** polished product recipes.
Prefer [recipes](recipes/index.md), the [CRUD tutorial](crud-tutorial.md), and
[Build your first app](../getting-started/quickstart.md) when learning.

| Directory | Phase | What it proves | Adopter note |
|---|---|---|---|
| [`data-app-0.15`](https://github.com/eddiethedean/hedron/tree/main/examples/data-app-0.15) | 0.15 | Data-app surface exit | Incomplete assets; not a gallery demo |
| [`data-app-0.16`](https://github.com/eddiethedean/hedron/tree/main/examples/data-app-0.16) | 0.16 | Extras / workbench exit | Raw routes — not idiomatic `@page` teaching |
| [`dashboard-0.17`](https://github.com/eddiethedean/hedron/tree/main/examples/dashboard-0.17) | 0.17 | Dashboard / agent interface exit | **Stub UI** — bindings declared; not an interactive dashboard |
| [`model-demo-0.18`](https://github.com/eddiethedean/hedron/tree/main/examples/model-demo-0.18) | 0.18 | Model demo / inference exit | **Stub UI** — setup + text dump; not a full classify form |

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron && uv sync
uv run uvicorn app:app --app-dir examples/model-demo-0.18 --reload
```

Timeless recipes: [Recipes overview](recipes/index.md).
