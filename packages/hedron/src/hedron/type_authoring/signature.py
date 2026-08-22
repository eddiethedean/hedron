"""Expand modeled fields onto documented FastAPI Path/Query/Form parameters."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from types import UnionType
from typing import Annotated, Any, Union, get_args, get_origin

from fastapi import Cookie, File, Form, Header, HTTPException, Path, Query, status

from hedron.type_authoring.markers import FormBody
from hedron.type_authoring.normalize import CompiledTypeHandler, FieldRecord
from hedron_core.binding_plan import compile_boundary_binding
from hedron_core.codes import HED_TYPE_0003

__all__ = [
    "apply_modeled_signature",
    "compile_injected_depends",
    "formbody_media_types",
    "reconstruct_kwargs",
    "reject_json_formbody",
]

_FORM_MEDIA = {
    "urlencoded": "application/x-www-form-urlencoded",
    "multipart": "multipart/form-data",
}


def _is_bool_annotation(annotation: object) -> bool:
    if annotation is bool:
        return True
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        return bool(args) and _is_bool_annotation(args[0])
    if origin in {Union, UnionType}:
        return any(item is bool for item in get_args(annotation))
    return False


def formbody_media_types(compiled: CompiledTypeHandler) -> tuple[str, ...]:
    """Allowed Content-Type values for a FormBody command, or empty if not FormBody."""
    if not compiled.modeled or not isinstance(compiled.source, FormBody):
        return ()
    allowed = _FORM_MEDIA.get(compiled.form_encoding or "urlencoded")
    if allowed:
        return (allowed,)
    return tuple(_FORM_MEDIA.values())


def reject_json_formbody(
    compiled: CompiledTypeHandler,
    request: object | None,
    *,
    strict_json: bool = False,
) -> None:
    """Refuse non-form bodies as a silent empty FormBody (RFC-0071 / D-076 / #329)."""
    if request is None or not compiled.modeled or not isinstance(compiled.source, FormBody):
        if strict_json and request is not None:
            headers = getattr(request, "headers", None)
            raw = str(headers.get("content-type") or "") if headers is not None else ""
            media = raw.split(";", 1)[0].strip().lower()
            if media and media not in {"application/json", "application/problem+json"}:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=HED_TYPE_0003,
                )
        return
    headers = getattr(request, "headers", None)
    raw = ""
    if headers is not None:
        raw = str(headers.get("content-type") or "")
    media = raw.split(";", 1)[0].strip().lower()
    allowed = _FORM_MEDIA.get(compiled.form_encoding or "")
    if allowed and media == allowed:
        return
    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail=HED_TYPE_0003,
    )


def reconstruct_kwargs(compiled: CompiledTypeHandler, kwargs: dict[str, Any]) -> dict[str, Any]:
    if not compiled.modeled or compiled.param_name is None or compiled.adapter is None:
        return kwargs
    existing = kwargs.get(compiled.param_name)
    if compiled.model_type is not None and isinstance(existing, compiled.model_type):
        return kwargs
    raw: dict[str, Any] = {}
    for field in compiled.fields:
        if field.http_name in kwargs:
            value = kwargs.pop(field.http_name)
        elif field.name in kwargs:
            value = kwargs.pop(field.name)
        else:
            continue
        # FastAPI represents omitted non-nullable fields with ``None`` while
        # explicit null is meaningful for annotations that accept None.
        if value is None and not field.required and type(None) not in get_args(field.annotation):
            continue
        raw[field.name] = value
    kwargs[compiled.param_name] = compiled.adapter.validate(raw)
    return kwargs


def compile_injected_depends(signature: inspect.Signature) -> inspect.Signature:
    """Rewrite DependsOn markers to FastAPI Depends(scope=function|request)."""
    from hedron.type_authoring.depends import DependsOn, as_fastapi_depends

    rewritten: list[inspect.Parameter] = []
    changed = False
    for param in signature.parameters.values():
        marker = param.default
        if isinstance(marker, DependsOn):
            rewritten.append(param.replace(default=as_fastapi_depends(marker)))
            changed = True
            continue
        annotation = param.annotation
        metadata: tuple[object, ...] = ()
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Annotated and args:
            metadata = tuple(args[1:])
        depends_meta = next((item for item in metadata if isinstance(item, DependsOn)), None)
        if depends_meta is not None:
            rewritten.append(param.replace(default=as_fastapi_depends(depends_meta)))
            changed = True
            continue
        rewritten.append(param)
    if not changed:
        return signature
    return signature.replace(parameters=rewritten)


def apply_modeled_signature(
    fn: Callable[..., Any],
    compiled: CompiledTypeHandler,
) -> inspect.Signature:
    original = compile_injected_depends(inspect.signature(fn))
    if not compiled.modeled:
        return original
    plan = compile_boundary_binding(
        source=type(compiled.source).__name__ if compiled.source is not None else "",
        model_identity=compiled.model_type.__name__ if compiled.model_type is not None else "",
        locations=tuple(field.location for field in compiled.fields),
        aliases=tuple(field.http_name for field in compiled.fields if field.alias),
        structural=compiled.binding_plan,
        has_files=any(field.is_file for field in compiled.fields),
        content_type=(
            "application/x-www-form-urlencoded"
            if compiled.form_encoding == "urlencoded"
            else "multipart/form-data"
            if compiled.form_encoding == "multipart"
            else ""
        ),
    )
    if (
        plan.strategy == "native-model"
        and compiled.model_type is not None
        and compiled.param_name is not None
    ):
        marker = _native_marker(plan.field_locations)
        if marker is not None:
            injected: list[inspect.Parameter] = []
            for name, param in original.parameters.items():
                if name == compiled.param_name:
                    injected.append(
                        inspect.Parameter(
                            name,
                            param.kind,
                            default=param.default,
                            annotation=Annotated[compiled.model_type, marker],
                        )
                    )
                else:
                    injected.append(param)
            if any(item.name == compiled.param_name for item in injected):
                compiled.boundary_plan = plan  # type: ignore[attr-defined]
                return inspect.Signature(injected)
    compiled.boundary_plan = plan  # type: ignore[attr-defined]
    injected = []
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


def _native_marker(locations: tuple[str, ...]) -> object | None:
    unique = set(locations)
    if unique == {"query"}:
        return Query()
    if unique == {"header"}:
        return Header()
    if unique == {"cookie"}:
        return Cookie()
    return None


def _fastapi_parameter(field: FieldRecord) -> inspect.Parameter:
    annotation: object = (
        field.annotation if field.annotation is not inspect.Parameter.empty else Any
    )
    param_name = field.http_name
    if field.location == "path":
        return inspect.Parameter(
            param_name,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[annotation, Path()],  # type: ignore[valid-type]
        )
    if field.is_file:
        marker: object = File()
    elif field.location == "query":
        marker = Query()
    elif field.location == "header":
        marker = Header()
    elif field.location == "cookie":
        marker = Cookie()
    else:
        marker = Form()
    if field.required:
        return inspect.Parameter(
            param_name,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[annotation, marker],  # type: ignore[valid-type]
        )
    default: object
    default = None if field.default is inspect.Parameter.empty else field.default
    # An unchecked HTML checkbox omits its field. A true model default would
    # therefore make an omitted checkbox come back as true through FastAPI.
    if field.location == "form" and _is_bool_annotation(annotation) and default is True:
        default = False
    return inspect.Parameter(
        param_name,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        default=default,
        annotation=Annotated[annotation, marker],  # type: ignore[valid-type]
    )
