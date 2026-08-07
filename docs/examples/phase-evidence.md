# Phase evidence (0.15–0.18)

These directories are **capability-phase exit scenarios** for maintainers and evaluators.
They are runnable, but they are not polished product recipes. Prefer the
[reference app](reference-app.md), [CRUD tutorial](crud-tutorial.md), and
[recipes](notes-sqlalchemy.md) when learning.

| Directory | Phase | What it proves |
|---|---|---|
| [`data-app-0.15`](https://github.com/eddiethedean/hedron/tree/main/examples/data-app-0.15) | 0.15 | Data-app surface completeness exit |
| [`data-app-0.16`](https://github.com/eddiethedean/hedron/tree/main/examples/data-app-0.16) | 0.16 | Extras / workbench exit |
| [`dashboard-0.17`](https://github.com/eddiethedean/hedron/tree/main/examples/dashboard-0.17) | 0.17 | Reactive dashboard / agent interface exit |
| [`model-demo-0.18`](https://github.com/eddiethedean/hedron/tree/main/examples/model-demo-0.18) | 0.18 | Model demo / inference workflow exit |

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron && uv sync
uv run uvicorn app:app --app-dir examples/model-demo-0.18 --reload
```

Timeless recipes (not phase-stamped): [Notes + SQLAlchemy](notes-sqlalchemy.md) ·
[Session auth](session-auth.md) · [File upload](file-upload.md).
