# fastapi-workbench

Generic Posit Workbench / RStudio Server deployment adapter for FastAPI and other
Starlette-compatible ASGI applications.

Installing or importing this package does **not** wrap your application.
`RS_SERVER_URL` is discovery-only and never grants trust.

**Package maturity:** Stable independent `1.x` · pin `>=1.0.1,<2.0`

Supported Workbench floor is **2025.05.1**; current verified lane is **2026.07.0**.

## Install

```bash
pip install "fastapi-workbench>=1.0.1,<2.0"
# or
uv add "fastapi-workbench>=1.0.1,<2.0"
```

## Quick start

```bash
fastapi-workbench run myapp.main:app
fastapi-workbench check myapp.main:app --discover
fastapi-workbench doctor myapp.main:app --live
```

Wrap an existing ASGI app:

```python
from fastapi_workbench import workbenchify

app = workbenchify(my_asgi_app, owned_cookie_names=("session",))
```

## Configuration

Environment variables use the `FASTAPI_WORKBENCH_*` prefix (for example
`FASTAPI_WORKBENCH_MOUNT`, `FASTAPI_WORKBENCH_MODE`). See `fastapi-workbench check
--help` for the full CLI surface.
