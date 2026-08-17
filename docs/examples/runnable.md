# Runnable examples

Clone the repository to run real Hedron servers. The [simulated UI patterns](gallery.md)
in these docs are a **browser simulation**—not a live Hedron process.

Each recipe page below also has a **Try it (simulated)** Demo/Code tab so you can click
through the interaction before starting uvicorn.

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
```

## Recipes (prefer these)

| Example | Framework | Simulated demo | Run |
|---|---|---|---|
| [streamlit-migration](https://github.com/eddiethedean/hedron/tree/main/examples/streamlit-migration) | FastAPI | — | `uv run uvicorn app:app --app-dir examples/streamlit-migration --reload` |
| [reference-app](reference-app.md) | FastAPI | [Try it](reference-app.md#auth-gate) | `uv run uvicorn app:app --app-dir examples/reference-app --reload` |
| [notes-sqlalchemy](notes-sqlalchemy.md) | FastAPI | [Try it](notes-sqlalchemy.md#try-it-simulated) | `uv run uvicorn app:app --app-dir examples/notes-sqlalchemy --reload` |
| [session-auth](session-auth.md) | FastAPI | [Try it](session-auth.md#try-it-simulated) | `uv run uvicorn app:app --app-dir examples/session-auth --reload` |
| [file-upload](file-upload.md) | FastAPI | [Try it](file-upload.md#try-it-simulated) | `uv run uvicorn app:app --app-dir examples/file-upload --reload` |
| [jobs-poll](jobs-poll.md) | FastAPI | [Try it](jobs-poll.md#try-it-simulated) | `uv run uvicorn app:app --app-dir examples/jobs-poll --reload` |
| [package-workflows](https://github.com/eddiethedean/hedron/tree/main/examples/package-workflows) | FastAPI | — | `uv run uvicorn app:app --app-dir examples/package-workflows --reload` |
| [live-interaction](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction) | FastAPI | [Live poll](../guides/live-interaction.md#try-it-simulated) | `uv run uvicorn app:app --app-dir examples/live-interaction --reload` |
| [flask-reference](https://github.com/eddiethedean/hedron/tree/main/examples/flask-reference) | Flask | — | See example README |
| [django-reference](https://github.com/eddiethedean/hedron/tree/main/examples/django-reference) | Django | — | See example README |
| [hdj-progressive](https://github.com/eddiethedean/hedron/tree/main/examples/hdj-progressive) | HDJ | — | Prints HTML to stdout (not a web server) |
| [workbench-reference](https://github.com/eddiethedean/hedron/tree/main/examples/workbench-reference) | FastAPI | — | `hedron-workbench run app_facade:app` from `examples/workbench-reference` |

## Phase evidence (0.15–0.18)

Capability-phase exit scenarios — not polished product demos. See
[Phase evidence](phase-evidence.md).

| Example | Run |
|---|---|
| model-demo-0.18 | `uv run uvicorn app:app --app-dir examples/model-demo-0.18 --reload` |
| dashboard-0.17 | `uv run uvicorn app:app --app-dir examples/dashboard-0.17 --reload` |
| data-app-0.16 | `uv run uvicorn app:app --app-dir examples/data-app-0.16 --reload` |
| data-app-0.15 | `uv run uvicorn app:app --app-dir examples/data-app-0.15 --reload` |

Evaluator shortcuts: [CRUD tutorial](crud-tutorial.md) ·
[Try with Codespaces / Dev Container](try-it.md) · [Single-file apps](single-file.md).

Quickstarts without cloning: [Single-file apps](single-file.md) ·
[FastAPI](../getting-started/quickstart.md) ·
[Flask](../getting-started/flask.md) · [Django](../getting-started/django.md).
