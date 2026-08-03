"""OpenAPI post-processing for Hedron HTML routes."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from hedron_core.registry import get_registry

__all__ = ["install_openapi", "operation_id_for"]


def operation_id_for(kind: str, name: str, path: str, method: str) -> str:
    cleaned_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "") or "root"
    return f"hedron_{kind}_{name}_{method.lower()}_{cleaned_path}"


def install_openapi(app: FastAPI) -> None:
    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema is not None:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        registry = get_registry()
        route_by_op = {r.operation_id: r for r in registry.routes()}
        for path_item in schema.get("paths", {}).values():
            if not isinstance(path_item, dict):
                continue
            for operation in path_item.values():
                if not isinstance(operation, dict):
                    continue
                op_id = operation.get("operationId")
                meta = route_by_op.get(op_id) if isinstance(op_id, str) else None
                if meta is None:
                    continue
                operation.setdefault("x-hedron-kind", meta.kind)
                operation.setdefault("x-hedron-logical-id", meta.logical_id)
                if meta.htmx_inference:
                    operation.setdefault("x-hedron-htmx", dict(meta.htmx_inference))
                responses = operation.setdefault("responses", {})
                ok = responses.setdefault("200", {})
                content = ok.setdefault("content", {})
                content.setdefault("text/html", {"schema": {"type": "string"}})
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi  # type: ignore[method-assign]
