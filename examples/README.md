# Examples

Runnable samples for the Hedron monorepo. Prefer these after
[`hedron new`](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/)
on a clean venv — that is the polished first-success path.

| Example | Host | Start here? | Notes |
|---|---|---|---|
| [`reference-app/`](reference-app/) | FastAPI | Yes (full app) | Auth CRUD + DataEditor; charts are **Alpha** |
| [`data-app-0.15/`](data-app-0.15/) | FastAPI | 0.15 surface demo | region/fragment/swap, controls, Map, media stubs |
| [`live-interaction/`](live-interaction/) | FastAPI | After polling guide | Polling **Supported**; SSE/WS/stream/preload **experimental** |
| [`flask-reference/`](flask-reference/) | Flask | Adapter adopters | Home + fragment slice |
| [`django-reference/`](django-reference/) | Django | Adapter adopters | Waitress WSGI or uvicorn ASGI |
| [`hdj-progressive/`](hdj-progressive/) | CLI render | HDJ learners | Needs `hedron[jinja]` / workspace sync |

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
