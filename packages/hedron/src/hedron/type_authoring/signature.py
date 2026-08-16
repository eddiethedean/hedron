"""Expand modeled fields onto documented FastAPI Path/Query/Form parameters."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Annotated, Any

from fastapi import File, Form, HTTPException, Path, Query, status

from hedron.type_authoring.markers import FormBody
from hedron.type_authoring.normalize import CompiledTypeHandler, FieldRecord
from hedron_core.codes import HED_TYPE_0003

__all__ = ["apply_modeled_signature", "reconstruct_kwargs", "reject_json_formbody"]


def reject_json_formbody(compiled: CompiledTypeHandler, request: object | None) -> None:
    """Refuse JSON as a silent empty FormBody (RFC-0071 / D-076)."""
    if request is None or not compiled.modeled or not isinstance(compiled.source, FormBody):
        return
    headers = getattr(request, "headers", None)
    raw = ""
    if headers is not None:
        raw = str(headers.get("content-type") or "")
    media = raw.split(";", 1)[0].strip().lower()
    if media == "application/json" or media.endswith("+json"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=HED_TYPE_0003,
        )


def reconstruct_kwargs(compiled: CompiledTypeHandler, kwargs: dict[str, Any]) -> dict[str, Any]:
    if not compiled.modeled or compiled.param_name is None or compiled.adapter is None:
        return kwargs
    raw = {field.name: kwargs.pop(field.name) for field in compiled.fields if field.name in kwargs}
    kwargs[compiled.param_name] = compiled.adapter.validate(raw)
    return kwargs


def apply_modeled_signature(
    fn: Callable[..., Any],
    compiled: CompiledTypeHandler,
) -> inspect.Signature:
    if not compiled.modeled:
        return inspect.signature(fn)
    original = inspect.signature(fn)
    injected: list[inspect.Parameter] = []
    for name, param in original.parameters.items():
        if name == compiled.param_name:
            continue
        injected.append(param)
    path_params = [
        _fastapi_parameter(field) for field in compiled.fields if field.location == "path"
    ]
    required_rest = [
        _fastapi_parameter(field)
        for field in compiled.fields
        if field.required and field.location != "path"
    ]
    optional = [
        _fastapi_parameter(field)
        for field in compiled.fields
        if not field.required and field.location != "path"
    ]
    return inspect.Signature(path_params + required_rest + injected + optional)


def _fastapi_parameter(field: FieldRecord) -> inspect.Parameter:
    annotation: object = (
        field.annotation if field.annotation is not inspect.Parameter.empty else Any
    )
    if field.location == "path":
        return inspect.Parameter(
            field.name,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[annotation, Path()],  # type: ignore[valid-type]
        )
    if field.is_file:
        marker: object = File()
    elif field.location == "query":
        marker = Query()
    else:
        marker = Form()
    if field.required:
        return inspect.Parameter(
            field.name,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[annotation, marker],  # type: ignore[valid-type]
        )
    default: object
    default = None if field.default is inspect.Parameter.empty else field.default
    return inspect.Parameter(
        field.name,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        default=default,
        annotation=Annotated[annotation, marker],  # type: ignore[valid-type]
    )
