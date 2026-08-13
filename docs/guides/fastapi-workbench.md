# FastAPI Workbench (plain FastAPI)

Deploy plain FastAPI applications behind Posit Workbench / RStudio Server without
installing Hedron.

**Package:** `fastapi-workbench` `1.0.0` (independent semver) · import `fastapi_workbench`
**Requires:** Python 3.11–3.14, FastAPI/Starlette ASGI app

Supported Workbench floor is **2025.05.1** (linux/amd64). Current verified lane is
Workbench **2026.07.0**.

## Install

```bash
pip install "fastapi-workbench>=1.0.0,<2.0" "fastapi" "uvicorn[standard]"
# or
uv add "fastapi-workbench>=1.0.0,<2.0" "fastapi" "uvicorn[standard]"
```

## Launch on Workbench

```bash
fastapi-workbench run myapp:app
fastapi-workbench run myapp:create_app --factory
fastapi-workbench check --format json
```

Discovery exports `FASTAPI_WORKBENCH_ROOT_PATH` before import so cookie paths and
OpenAPI URLs are mount-correct at construction time.

## Explicit wrapper

```python
from fastapi_workbench import WorkbenchConfig, workbenchify

app = workbenchify(my_app, config=WorkbenchConfig(mode="on", mount="/s/example/p/8050"))
```

Installing or importing this package never monkey-patches your application.
`RS_SERVER_URL` requests discovery only — it does not grant trust.

## Hedron apps

Hedron applications should use [`hedron-workbench`](posit-workbench.md) 0.30+,
which depends on this package and adds `HedronWorkbench`, `HEDRON_ROOT_PATH`, and
Hedron URL/CSRF integration.

## Reference

- [RFC-0063](../rfcs/RFC-0063-FASTAPI-WORKBENCH-EXTRACTION.md)
- [Example app](https://github.com/eddiethedean/hedron/tree/main/examples/fastapi-workbench-reference)
- REALWB-030 Docker smoke runs this app via `fastapi-workbench run` alongside the
  hedron-workbench reference (`examples/workbench-reference/app_facade.py`).
