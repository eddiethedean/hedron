# Examples

Runnable samples for the Hedron monorepo. Prefer these after
[`hedron new`](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/)
on a clean venv — that is the polished first-success path.

## Recipes (prefer these)

| Example | Host | Notes |
|---|---|---|
| [`reference-app/`](reference-app/) | FastAPI | Auth CRUD + DataEditor; charts are **Alpha** |
| [`notes-sqlalchemy/`](notes-sqlalchemy/) | FastAPI | SQLite notes + CSRF |
| [`session-auth/`](session-auth/) | FastAPI | Session login gate |
| [`file-upload/`](file-upload/) | FastAPI | Multipart upload with size/type checks |
| [`live-interaction/`](live-interaction/) | FastAPI | Polling **Supported**; SSE/WS **experimental** |
| [`flask-reference/`](flask-reference/) | Flask | Home + fragment slice |
| [`django-reference/`](django-reference/) | Django | Waitress WSGI or uvicorn ASGI |
| [`hdj-progressive/`](hdj-progressive/) | CLI render | Needs `hedron[jinja]` / workspace sync |

## Phase evidence (0.15–0.18)

| Example | Phase | Notes |
|---|---|---|
| [`model-demo-0.18/`](model-demo-0.18/) | 0.18 | ModelDemo / InferencePolicy exit |
| [`dashboard-0.17/`](dashboard-0.17/) | 0.17 | Dashboard / agent interface exit |
| [`data-app-0.16/`](data-app-0.16/) | 0.16 | Extras / workbench exit |
| [`data-app-0.15/`](data-app-0.15/) | 0.15 | Data-app surface exit |

Docs: [phase evidence](https://hedron.readthedocs.io/en/latest/examples/phase-evidence/).

## Monorepo run pattern

```bash
uv sync
# then follow each example README
```

Docs gallery demos on Read the Docs are **simulations**, not these servers. Matrix:
[runnable examples](https://hedron.readthedocs.io/en/latest/examples/runnable/).

## Docker

`reference-app` compose/Dockerfile paths are **maintainer experimental** — prefer local
`uvicorn` for adopters. Production packaging:
[Deployment](https://hedron.readthedocs.io/en/latest/guides/deployment/).
