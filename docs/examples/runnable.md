# Runnable examples

Clone the repository to run real Hedron servers. The [simulated UI patterns](gallery.md)
in these docs are a **browser simulation**—not a live Hedron process.

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
```

| Example | Framework | Run |
|---|---|---|
| [reference-app](reference-app.md) | FastAPI | `uv run uvicorn app:app --app-dir examples/reference-app --reload` |
| [data-app-0.15](https://github.com/eddiethedean/hedron/tree/main/examples/data-app-0.15) | FastAPI | `uv run uvicorn app:app --app-dir examples/data-app-0.15 --reload` |
| [live-interaction](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction) | FastAPI | `uv run uvicorn app:app --app-dir examples/live-interaction --reload` |
| [flask-reference](https://github.com/eddiethedean/hedron/tree/main/examples/flask-reference) | Flask | See example README |
| [django-reference](https://github.com/eddiethedean/hedron/tree/main/examples/django-reference) | Django | See example README |
| [hdj-progressive](https://github.com/eddiethedean/hedron/tree/main/examples/hdj-progressive) | HDJ | Prints HTML to stdout (not a web server) |

Evaluator shortcuts: [CRUD tutorial](crud-tutorial.md) · [Try with Codespaces / Dev Container](try-it.md) · [Single-file apps](single-file.md).

Quickstarts without cloning: [Single-file apps](single-file.md) ·
[FastAPI](../getting-started/quickstart.md) ·
[Flask](../getting-started/flask.md) · [Django](../getting-started/django.md).
