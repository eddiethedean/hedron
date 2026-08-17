"""Native-model versus expanded-fields FastAPI compilation (0.49)."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Cookie, Header, Query

from hedron.type_authoring.normalize import CompiledTypeHandler
from hedron_core.binding_plan import BoundaryBindingPlan, compile_boundary_binding
from hedron_core.updates import BindingPlan

__all__ = ["boundary_plan_for", "apply_native_or_expanded"]


def boundary_plan_for(
    compiled: CompiledTypeHandler,
    *,
    force_expanded: bool = False,
    portable_adapter: bool = False,
    flask_django: bool = False,
) -> BoundaryBindingPlan:
    locations = tuple(field.location for field in compiled.fields)
    aliases = tuple(field.http_name for field in compiled.fields if field.alias)
    incompatible = any(
        field.alias and field.alias != field.name and field.location == "path"
        for field in compiled.fields
    )
    source = type(compiled.source).__name__ if compiled.source is not None else ""
    identity = compiled.model_type.__name__ if compiled.model_type is not None else ""
    has_files = any(field.is_file for field in compiled.fields)
    content_type = ""
    if compiled.form_encoding == "urlencoded":
        content_type = "application/x-www-form-urlencoded"
    elif compiled.form_encoding == "multipart":
        content_type = "multipart/form-data"
    return compile_boundary_binding(
        source=source,
        model_identity=identity,
        locations=locations,
        aliases=aliases,
        structural=compiled.binding_plan or BindingPlan(),
        has_files=has_files,
        portable_adapter=portable_adapter,
        force_expanded=force_expanded,
        incompatible_aliases=incompatible,
        flask_django=flask_django,
        content_type=content_type,
    )


def apply_native_or_expanded(
    fn: Callable[..., Any],
    compiled: CompiledTypeHandler,
    plan: BoundaryBindingPlan,
) -> inspect.Signature:
    from hedron.type_authoring.signature import apply_modeled_signature

    if (
        plan.strategy != "native-model"
        or compiled.model_type is None
        or compiled.param_name is None
    ):
        return apply_modeled_signature(fn, compiled)
    original = inspect.signature(fn)
    marker = _native_marker(plan)
    if marker is None:
        return apply_modeled_signature(fn, compiled)
    injected: list[inspect.Parameter] = []
    replaced = False
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
            replaced = True
            continue
        injected.append(param)
    if not replaced:
        return apply_modeled_signature(fn, compiled)
    return inspect.Signature(injected)


def _native_marker(plan: BoundaryBindingPlan) -> object | None:
    locations = set(plan.field_locations)
    if locations == {"query"}:
        return Query()
    if locations == {"header"}:
        return Header()
    if locations == {"cookie"}:
        return Cookie()
    return None
