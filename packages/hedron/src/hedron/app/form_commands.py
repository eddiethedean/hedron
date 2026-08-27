"""Form-command facade: inject ``FormBody`` and lower to ``@app.command``."""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable, Mapping, Sequence
from typing import (
    Annotated,
    Any,
    Literal,
    ParamSpec,
    TypeAlias,
    TypeGuard,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)

from pydantic import BaseModel

from hedron.handles import ActionHandle, BoundFragment, FragmentHandle, refresh
from hedron.type_authoring.markers import Control, FormBody, Refreshes, Updates
from hedron_core.codes import HED_FORMCMD_0001, HED_FORMCMD_0002, HED_FORMCMD_0003, HED_SEC_0001
from hedron_core.component import NodeLike
from hedron_core.diagnostics import error
from hedron_core.htmx_contract import is_local_path
from hedron_core.interaction import InteractionResult, OobUpdate

__all__ = [
    "FormEncoding",
    "SafeLocalPath",
    "Update",
    "discover_form_model",
    "form_command",
    "inject_form_body",
]

P = ParamSpec("P")
R = TypeVar("R")

FormEncoding = Literal["urlencoded", "multipart", "auto"]
SafeLocalPath: TypeAlias = str
Update: TypeAlias = FragmentHandle[Any, Any] | BoundFragment[Any]

_FORM_COMMAND_CONTROLS: dict[str, Mapping[str, Control | NodeLike]] = {}

_FASTAPI_BODY_MARKERS = frozenset({"Body", "Form", "File", "Header", "Cookie", "Query", "Path"})


def discover_form_model(
    fn: Callable[..., object],
) -> tuple[str, type[BaseModel], tuple[object, ...]]:
    """Find exactly one direct Pydantic model parameter that is not a Depends injection."""
    try:
        signature = inspect.signature(fn)
    except (TypeError, ValueError) as exc:
        raise error(
            HED_FORMCMD_0001,
            title="Uninspectable form_command handler",
            explanation="form_command requires a concrete callable signature.",
            remediation="Use a plain function or method with annotated parameters.",
        ) from exc
    hints = _resolve_hints(fn)
    candidates: list[tuple[str, type[BaseModel], tuple[object, ...]]] = []
    for name, parameter in signature.parameters.items():
        if name in {"self", "cls"}:
            continue
        if _is_injected(parameter, hints.get(name, parameter.annotation)):
            continue
        if parameter.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
            continue
        annotation = hints.get(name, parameter.annotation)
        base, metadata = _split_annotated(annotation)
        if _has_competing_fastapi_marker(metadata):
            raise error(
                HED_FORMCMD_0001,
                title="Ambiguous form model boundary",
                explanation=(
                    f"Parameter {name!r} carries FastAPI body/form markers that compete "
                    "with form_command model discovery."
                ),
                remediation="Remove Body/Form/File markers; form_command injects FormBody.",
            )
        if not _is_model(base):
            if annotation is inspect.Parameter.empty:
                raise error(
                    HED_FORMCMD_0001,
                    title="Missing form model",
                    explanation=f"Parameter {name!r} has no type annotation.",
                    remediation="Annotate exactly one Pydantic BaseModel parameter.",
                )
            raise error(
                HED_FORMCMD_0001,
                title="Ambiguous form model boundary",
                explanation=(
                    f"Parameter {name!r} is not an injected dependency and not a BaseModel."
                ),
                remediation="Keep only one BaseModel form parameter; mark others Depends(...).",
            )
        candidates.append((name, base, metadata))
    if not candidates:
        raise error(
            HED_FORMCMD_0001,
            title="Missing form model",
            explanation="form_command requires exactly one Pydantic BaseModel parameter.",
            remediation="Add one BaseModel parameter (other params must be Depends/request).",
        )
    if len(candidates) > 1:
        names = ", ".join(repr(item[0]) for item in candidates)
        raise error(
            HED_FORMCMD_0001,
            title="Ambiguous form model",
            explanation=f"Multiple candidate form models: {names}.",
            remediation="Keep exactly one BaseModel parameter; inject the rest with Depends.",
        )
    return candidates[0]


def inject_form_body(
    fn: Callable[..., object],
    *,
    encoding: FormEncoding = "urlencoded",
) -> Callable[..., object]:
    """Rewrite the discovered model parameter to ``Annotated[Model, FormBody(...)]``."""
    if encoding not in {"urlencoded", "multipart", "auto"}:
        raise error(
            HED_FORMCMD_0002,
            title="Unsupported form encoding",
            explanation=f"encoding={encoding!r} is outside the closed inventory.",
            remediation="Use 'urlencoded', 'multipart', or 'auto'.",
        )
    name, model, metadata = discover_form_model(fn)
    existing_body = [item for item in metadata if isinstance(item, FormBody)]
    if len(existing_body) > 1:
        raise error(
            HED_FORMCMD_0001,
            title="Ambiguous form model boundary",
            explanation=f"Parameter {name!r} carries multiple FormBody markers.",
            remediation="Use a single FormBody marker or omit it for form_command injection.",
        )
    if existing_body and existing_body[0].encoding != encoding:
        raise error(
            HED_FORMCMD_0003,
            title="FormBody encoding conflict",
            explanation=(
                f"Parameter {name!r} FormBody(encoding={existing_body[0].encoding!r}) "
                f"conflicts with form_command(encoding={encoding!r})."
            ),
            remediation="Align encodings or omit FormBody on the parameter.",
        )
    marker = existing_body[0] if existing_body else FormBody(encoding=encoding)
    rest = tuple(item for item in metadata if not isinstance(item, FormBody))
    new_annotation = Annotated[model, marker, *rest]
    signature = inspect.signature(fn)
    params = []
    for parameter in signature.parameters.values():
        if parameter.name == name:
            params.append(parameter.replace(annotation=new_annotation))
        else:
            params.append(parameter)
    annotated = fn
    annotated.__signature__ = signature.replace(parameters=params)  # type: ignore[attr-defined]
    annotations = dict(getattr(annotated, "__annotations__", {}) or {})
    annotations[name] = new_annotation
    annotated.__annotations__ = annotations
    return annotated


def form_command(
    app: object,
    path: str,
    *,
    name: str | None = None,
    refreshes: Sequence[FragmentHandle[Any, Any]] = (),
    updates: Sequence[Update] = (),
    success: NodeLike | str | None = None,
    outcomes: object | None = None,
    fallback: SafeLocalPath,
    encoding: FormEncoding = "urlencoded",
    controls: Mapping[str, Control | NodeLike] | None = None,
    dependencies: Sequence[object] | None = None,
) -> Callable[[Callable[P, R]], ActionHandle[Any, Any]]:
    """Decorator factory that discovers a form model and registers via ``app.command``."""
    if not is_local_path(str(fallback)):
        raise error(
            HED_SEC_0001,
            title="Unsafe fallback path",
            explanation=f"fallback={fallback!r} is not a safe local path.",
            remediation="Use a path starting with '/' and no scheme/host (same as redirect_local).",
        )

    def decorator(fn: Callable[P, R]) -> ActionHandle[Any, Any]:
        _reject_effect_conflicts(
            fn,
            refreshes=refreshes,
            updates=updates,
            success=success,
            outcomes=outcomes,
        )
        annotated = inject_form_body(fn, encoding=encoding)
        effect_markers: list[object] = []
        if refreshes:
            effect_markers.append(Refreshes(*refreshes))
        if updates:
            effect_markers.append(Updates(*updates))
        if effect_markers:
            payload: object = (
                tuple(effect_markers) if len(effect_markers) > 1 else effect_markers[0]
            )
            setattr(annotated, "__hedron_effects__", payload)  # noqa: B010
        if outcomes is not None and getattr(annotated, "__hedron_outcomes__", None) is None:
            setattr(annotated, "__hedron_outcomes__", outcomes)  # noqa: B010

        register = app.command(  # type: ignore[attr-defined]
            path,
            name=name,
            fallback=fallback,
            dependencies=dependencies,
            outcomes=outcomes,
            _emit_legacy_warning=False,
        )
        handle = register(annotated)
        if controls:
            _FORM_COMMAND_CONTROLS[handle.logical_id] = dict(controls)
            handle = _with_default_form_controls(handle, controls)
        if refreshes or success is not None:
            handle = _attach_success_effect(handle, refreshes=refreshes, success=success)
        return handle

    return decorator


def _attach_success_effect(
    handle: ActionHandle[Any, Any],
    *,
    refreshes: Sequence[FragmentHandle[Any, Any]],
    success: NodeLike | str | None,
) -> ActionHandle[Any, Any]:
    if refreshes:
        intent: object = refresh(*refreshes)
        if success is not None:
            intent = intent.toast(success)  # type: ignore[union-attr]
        return handle.effect(intent)  # type: ignore[arg-type]
    if success is not None:
        return handle.effect(
            InteractionResult(
                content=None,
                swap="none",
                oob=(
                    OobUpdate(
                        content=success,
                        element_id="hedron-toast",
                        swap="innerHTML",
                    ),
                ),
            )
        )
    return handle


def _with_default_form_controls(
    handle: ActionHandle[Any, Any],
    controls: Mapping[str, Control | NodeLike],
) -> ActionHandle[Any, Any]:
    original = handle.form

    @functools.wraps(original)
    def form(
        *,
        value: object | None = None,
        errors: Sequence[object] = (),
        submit_label: str = "Submit",
        controls: Mapping[str, NodeLike | Control] | None = None,
        fallback: str | None = None,
        enhance: str = "native",
        **safe_form_attrs: object,
    ) -> NodeLike:
        merged: dict[str, Control | NodeLike] = dict(
            _FORM_COMMAND_CONTROLS.get(handle.logical_id) or controls or {}
        )
        if controls:
            merged.update(controls)
        return original(
            value=value,
            errors=errors,
            submit_label=submit_label,
            controls=merged or None,
            fallback=fallback,
            enhance=enhance,
            **safe_form_attrs,
        )

    handle.form = form  # type: ignore[method-assign]
    return handle


def _reject_effect_conflicts(
    fn: Callable[..., object],
    *,
    refreshes: Sequence[object],
    updates: Sequence[object],
    success: object,
    outcomes: object | None,
) -> None:
    existing_outcomes = getattr(fn, "__hedron_outcomes__", None)
    if outcomes is not None and existing_outcomes is not None and outcomes is not existing_outcomes:
        raise error(
            HED_FORMCMD_0003,
            title="Decorator outcome conflict",
            explanation="Handler already declares outcomes that conflict with form_command.",
            remediation="Pass outcomes in one place only.",
        )
    existing_effects = getattr(fn, "__hedron_effects__", None)
    if existing_effects is not None and (refreshes or updates or success is not None):
        raise error(
            HED_FORMCMD_0003,
            title="Decorator effect conflict",
            explanation="Handler already declares effects that conflict with form_command.",
            remediation="Use either form_command refreshes/updates/success or handler effects.",
        )
    hints = _resolve_hints(fn)
    return_ann = hints.get("return", inspect.signature(fn).return_annotation)
    _, metadata = _split_annotated(return_ann)
    if any(isinstance(item, (Refreshes, Updates)) for item in metadata) and (
        refreshes or updates or success is not None
    ):
        raise error(
            HED_FORMCMD_0003,
            title="Decorator effect conflict",
            explanation="Return-annotation Refreshes/Updates conflict with form_command effects.",
            remediation="Declare effects on form_command or the return annotation, not both.",
        )


def _resolve_hints(fn: Callable[..., object]) -> dict[str, object]:
    try:
        return get_type_hints(fn, include_extras=True)
    except (NameError, TypeError, AttributeError, RecursionError):
        return dict(getattr(fn, "__annotations__", {}) or {})


def _split_annotated(annotation: object) -> tuple[object, tuple[object, ...]]:
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        return args[0], tuple(args[1:])
    return annotation, ()


def _is_model(annotation: object) -> TypeGuard[type[BaseModel]]:
    return isinstance(annotation, type) and issubclass(annotation, BaseModel)


def _is_injected(parameter: inspect.Parameter, annotation: object) -> bool:
    from fastapi.params import Depends as DependsParam
    from starlette.requests import Request

    if parameter.name in {"request", "websocket"}:
        return True
    if annotation is Request or (isinstance(annotation, type) and issubclass(annotation, Request)):
        return True
    if isinstance(parameter.default, DependsParam):
        return True
    from hedron.type_authoring.depends import DependsOn

    if isinstance(parameter.default, DependsOn):
        return True
    _, metadata = _split_annotated(annotation)
    if any(isinstance(item, DependsParam) for item in metadata):
        return True
    return any(isinstance(item, DependsOn) for item in metadata)


def _has_competing_fastapi_marker(metadata: Sequence[object]) -> bool:
    for item in metadata:
        if isinstance(item, FormBody):
            continue
        cls_name = type(item).__name__
        if cls_name in _FASTAPI_BODY_MARKERS:
            return True
        module = getattr(type(item), "__module__", "")
        if module.startswith("fastapi.") and cls_name in _FASTAPI_BODY_MARKERS:
            return True
    return False
