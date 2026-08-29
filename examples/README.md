# Examples

Runnable samples for the Hedron monorepo. Prefer these after
[`hedron new`](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/)
on a clean venv — that is the polished first-success path.

## Recipes (prefer these)

| Example | Host | Notes |
|---|---|---|
| [`theme-gallery/`](theme-gallery/) | FastAPI | Visual QA across common interfaces in forced light and dark modes |
| [`showcase/`](showcase/) | FastAPI | Full-feature operations console with real fragment and action routes |
| [`chrome-zero-css/`](chrome-zero-css/) | FastAPI | Data Mover-class chrome from `Theme` + built-ins with no application CSS |
| [`streamlit-migration/`](streamlit-migration/) | FastAPI | Runnable sales-dashboard migration with typed GET filters |
| [`notes-sqlalchemy/`](notes-sqlalchemy/) | FastAPI | SQLite create / list / delete via `@app.view` + `@app.action` |
| [`session-auth/`](session-auth/) | FastAPI | Session login; `/` redirects to `/login` |
| [`file-upload/`](file-upload/) | FastAPI | Multipart upload with size/type checks |
| [`jobs-poll/`](jobs-poll/) | FastAPI | Supported job polling (`Poll` + status) |
| [`package-workflows/`](package-workflows/) | FastAPI | `DataWorkspace` + `ChartInteraction` + generated form (0.46) |
| [`live-interaction/`](live-interaction/) | FastAPI | Polling **Supported**; SSE/WS **experimental** |
| [`fastapi-pydantic/`](fastapi-pydantic/) | FastAPI | Lifetimes, native/expanded binding (0.49) |
| [`htmx-extensions/`](htmx-extensions/) | FastAPI | Declared SSE / head-support / preload (0.48) |
| [`reference-app/`](reference-app/) | FastAPI | Kitchen-sink auth CRUD + DataEditor (learn recipes first) |
| [`flask-reference/`](flask-reference/) | Flask | Home + HTMX refresh fragment (port **8000**) |
| [`django-reference/`](django-reference/) | Django | Waitress WSGI or uvicorn ASGI (manage-less) |
| [`hdj-progressive/`](hdj-progressive/) | CLI render | Prints HTML to stdout — not a web server |
| [`workbench-reference/`](workbench-reference/) | FastAPI | HedronPosit launch path for Posit Workbench |

## Phase evidence (0.15–0.18) — maintainers

Stub exit scenarios, not product tutorials. Docs:
[phase evidence](https://github.com/eddiethedean/hedron/tree/main/examples/phase-evidence).

| Example | Phase | Notes |
|---|---|---|
| [`model-demo-0.18/`](model-demo-0.18/) | 0.18 | Runnable synthetic classifier — also a product recipe |
| [`dashboard-0.17/`](dashboard-0.17/) | 0.17 | Stub UI — dashboard exit |
| [`data-app-0.16/`](data-app-0.16/) | 0.16 | Extras / workbench exit |
| [`data-app-0.15/`](data-app-0.15/) | 0.15 | Data-app surface exit |

## Monorepo run pattern

```bash
uv sync
# then follow each example README
```

Docs gallery demos on Read the Docs are **simulations**, not these servers. Matrix:
[runnable examples](https://hedron.readthedocs.io/en/latest/examples/runnable/).

## Docker

Prefer the adopter Dockerfile sketch in
[Deployment](https://hedron.readthedocs.io/en/latest/guides/deployment/).
`reference-app` compose is **maintainer experimental**.
