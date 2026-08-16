"""FastAPI refreshable-view and command handles (phase 0.43 / RFC-0070)."""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, Literal, TypeVar, cast, overload
from urllib.parse import urlencode

from fastapi.params import Depends as DependsParam
from starlette.requests import Request

from hedron.routing.reverse import ComponentRef
from hedron_core.codes import HED_CMD_0001, HED_TYPE_0005, HED_VIEW_0003, HED_VIEW_0004
from hedron_core.component import NodeLike
from hedron_core.diagnostics import error
from hedron_core.hosts import FragmentHost
from hedron_core.html import html
from hedron_core.htmx.policy import CacheHint, FragmentRegion
from hedron_core.interaction import InteractionResult
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue
from hedron_core.updates import (
    MAX_REFRESH_TARGETS,
    BaseHandleDescriptor,
    BindingPlan,
    BoundValues,
    Patch,
    PatchSet,
    RefreshIntent,
    StructuralBindingAdapter,
    UpdateTarget,
    generated_command_path,
    generated_view_path,
    normalize_logical_id,
    refresh_event_name,
    register_handle_descriptor,
    safe_dom_id,
    validate_explicit_key,
)

BindT = TypeVar("BindT")
ContentT = TypeVar("ContentT")
InputT = TypeVar("InputT")
ResultT = TypeVar("ResultT")

__all__ = [
    "ActionHandle",
    "BoundFragment",
    "FragmentHandle",
    "Refresh",
    "patches",
    "refresh",
]

_ADAPTER = StructuralBindingAdapter()
_REQUEST_NAMES = frozenset({"request", "websocket"})
_UNSET = object()


def _is_injected(parameter: inspect.Parameter) -> bool:
    if parameter.name in _REQUEST_NAMES:
        return True
    annotation = parameter.annotation
    if annotation is Request or (isinstance(annotation, type) and issubclass(annotation, Request)):
        return True
    default = parameter.default
    if isinstance(default, DependsParam):
        return True
    origin = getattr(annotation, "__origin__", None)
    args = getattr(annotation, "__args__", ())
    if origin is not None and args:
        metadata = getattr(annotation, "__metadata__", ())
        if any(isinstance(item, DependsParam) for item in metadata):
            return True
    return False


def binding_plan_for(fn: Callable[..., object]) -> BindingPlan:
    path_params: list[str] = []
    query_params: list[str] = []
    required: list[str] = []
    try:
        signature = inspect.signature(fn)
    except (TypeError, ValueError):
        return BindingPlan()
    for name, parameter in signature.parameters.items():
        if name in {"self", "cls"} or _is_injected(parameter):
            continue
        if parameter.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
            continue
        if parameter.default is inspect.Parameter.empty:
            path_params.append(name)
            required.append(name)
        else:
            query_params.append(name)
    return BindingPlan(
        path_params=tuple(path_params),
        query_params=tuple(query_params),
        required=tuple(required),
    )


def _path_with_query(path: str, query: Mapping[str, str]) -> str:
    if not query:
        return path
    return f"{path}?{urlencode(query)}"


def _bound_url(values: BoundValues) -> str:
    return _path_with_query(values.path, values.query)


def _try_initial_render(
    fn: Callable[..., Any], bound: Mapping[str, object] | None
) -> NodeLike | None:
    try:
        signature = inspect.signature(fn)
    except (TypeError, ValueError):
        return None
    kwargs: dict[str, object] = dict(bound or {})
    for name, parameter in signature.parameters.items():
        if name in kwargs or name in {"self", "cls"}:
            continue
        if _is_injected(parameter):
            return None
        if parameter.default is inspect.Parameter.empty:
            return None
    try:
        result = fn(**kwargs) if kwargs else fn()
    except TypeError:
        return None
    if inspect.iscoroutine(result) or inspect.isasyncgen(result):
        if inspect.iscoroutine(result):
            result.close()
        return None
    return cast(NodeLike, result)


def _try_initial_render_model(
    fn: Callable[..., Any], param_name: str, model: object
) -> NodeLike | None:
    try:
        result = fn(**{param_name: model})
    except TypeError:
        return None
    if inspect.iscoroutine(result) or inspect.isasyncgen(result):
        if inspect.iscoroutine(result):
            result.close()
        return None
    return cast(NodeLike, result)


@dataclass(frozen=False)
class FragmentHandle(Generic[BindT, ContentT]):
    """Callable mounted-view handle returned by ``@app.refreshable``."""

    logical_id: str
    name: str
    path: str
    method: Literal["GET"]
    dom_id: str
    selector: str
    region: FragmentRegion
    ref: ComponentRef
    renderer: Callable[..., ContentT]
    renderer_signature: inspect.Signature
    app_id: str
    host: FragmentHost
    fallback: str | None
    binding_plan: BindingPlan
    descriptor: BaseHandleDescriptor
    include_in_schema: bool = False
    adapter: Any = field(default=None)
    type_meta: Any = None
    _bound: BoundValues | None = None
    __wrapped__: Callable[..., ContentT] | None = None

    @property
    def schema(self) -> object | None:
        meta = self.type_meta
        return None if meta is None else getattr(meta, "schema", None)

    @property
    def parameter_model(self) -> object | None:
        meta = self.type_meta
        return None if meta is None else getattr(meta, "model_type", None)

    @property
    def bound(self) -> bool:
        return not self.binding_plan.required or self._bound is not None

    def __call__(self) -> FragmentHost:
        if self.binding_plan.required and self._bound is None:
            raise error(
                HED_VIEW_0003,
                title="Unbound parameterized handle",
                explanation=f"View {self.logical_id!r} requires bind() before mount.",
                remediation="Call handle.bind(...) with the registered path parameters.",
            )
        bound_map = dict(self._bound.parameters) if self._bound is not None else {}
        meta = self.type_meta
        if meta is not None and getattr(meta, "modeled", False) and meta.param_name:
            try:
                model = meta.adapter.validate(bound_map)
                content = _try_initial_render_model(self.renderer, meta.param_name, model)
            except Exception:  # noqa: BLE001
                content = None
        else:
            content = _try_initial_render(self.renderer, bound_map)
        get_url = _bound_url(self._bound) if self._bound is not None else self.path
        load_on_mount = content is None
        return self.host.materialize(
            content if content is not None else self.host._loading,
            dom_id=self.dom_id,
            get_url=get_url,
            event_name=refresh_event_name(self.dom_id),
            logical_id=self.logical_id,
            fallback=self.fallback,
            load_on_mount=load_on_mount,
        )

    @overload
    def bind(self, value: BindT, /) -> BoundFragment[ContentT]: ...

    @overload
    def bind(self, **parameters: object) -> BoundFragment[ContentT]: ...

    def bind(self, *args: object, **parameters: object) -> BoundFragment[ContentT]:
        adapter = self.adapter or _ADAPTER
        value: object = _UNSET
        if args:
            if len(args) != 1 or parameters:
                raise error(
                    HED_VIEW_0004,
                    title="Ambiguous bind() call",
                    explanation="Pass either a model instance or keyword fields, not both.",
                    remediation="Use bind(model) or bind(**fields).",
                )
            value = args[0]
            if self.type_meta is not None and getattr(self.type_meta, "adapter", None):
                model = self.type_meta.adapter.validate(value)  # type: ignore[union-attr]
                parameters = self.type_meta.adapter.dump(model)
            elif isinstance(value, Mapping):
                parameters = dict(value)
            else:
                raise error(
                    HED_VIEW_0004,
                    title="Unsupported bind() value",
                    explanation="Unmodeled handlers accept keyword fields only.",
                    remediation="Call bind(**fields) or opt into ViewParams.",
                )
        template = self.descriptor.path or self.path
        values = adapter.bind(self.binding_plan, parameters, path=template)
        extra_token = values.instance_token
        nested = FragmentHandle(
            logical_id=self.logical_id,
            name=self.name,
            path=_bound_url(values),
            method="GET",
            dom_id=safe_dom_id(self.logical_id, instance_token=extra_token),
            selector="",
            region=self.region,
            ref=self.ref,
            renderer=self.renderer,
            renderer_signature=self.renderer_signature,
            app_id=self.app_id,
            host=self.host,
            fallback=self.fallback,
            binding_plan=self.binding_plan,
            descriptor=self.descriptor,
            include_in_schema=self.include_in_schema,
            adapter=self.adapter,
            type_meta=self.type_meta,
            _bound=values,
            __wrapped__=self.renderer,
        )
        object.__setattr__(nested, "selector", f"#{nested.dom_id}")
        object.__setattr__(
            nested,
            "region",
            FragmentRegion(id=nested.dom_id, selector=nested.selector, description=self.logical_id),
        )
        return BoundFragment(handle=nested)

    def refresh_button(self, label: str = "Refresh", **kwargs: object) -> Refresh:
        return Refresh(self, label=label, **kwargs)

    def replace(self, content: ContentT, **kwargs: object) -> Patch[ContentT]:
        del kwargs
        if not self.bound:
            raise error(
                HED_VIEW_0003,
                title="Unbound parameterized handle",
                explanation=f"View {self.logical_id!r} must be bound before replace().",
                remediation="Call bind() first.",
            )
        url = _bound_url(self._bound) if self._bound is not None else self.path
        wrapped = self.host.materialize(
            cast(NodeLike, content),
            dom_id=self.dom_id,
            get_url=url,
            event_name=refresh_event_name(self.dom_id),
            logical_id=self.logical_id,
            fallback=self.fallback,
        )
        return Patch(
            target=cast(UpdateTarget, self), content=cast(ContentT, wrapped), swap="outerHTML"
        )

    def update(self, content: ContentT, **kwargs: object) -> Patch[ContentT]:
        del kwargs
        if not self.bound:
            raise error(
                HED_VIEW_0003,
                title="Unbound parameterized handle",
                explanation=f"View {self.logical_id!r} must be bound before update().",
                remediation="Call bind() first.",
            )
        return Patch(target=cast(UpdateTarget, self), content=content, swap="innerHTML")


@dataclass(frozen=True)
class BoundFragment(Generic[ContentT]):
    handle: FragmentHandle[Mapping[str, object], ContentT]

    @property
    def logical_id(self) -> str:
        return self.handle.logical_id

    @property
    def dom_id(self) -> str:
        return self.handle.dom_id

    @property
    def path(self) -> str:
        return self.handle.path

    @property
    def app_id(self) -> str:
        return self.handle.app_id

    @property
    def region(self) -> FragmentRegion:
        return self.handle.region

    @property
    def bound(self) -> bool:
        return True

    @property
    def selector(self) -> str:
        return self.handle.selector

    def __call__(self) -> FragmentHost:
        return self.handle()

    def refresh_button(self, label: str = "Refresh", **kwargs: object) -> Refresh:
        return self.handle.refresh_button(label, **kwargs)

    def replace(self, content: ContentT, **kwargs: object) -> Patch[ContentT]:
        return self.handle.replace(content, **kwargs)

    def update(self, content: ContentT, **kwargs: object) -> Patch[ContentT]:
        return self.handle.update(content, **kwargs)


@dataclass(frozen=False)
class ActionHandle(Generic[InputT, ResultT]):
    """Typed command reference returned by ``@app.command``."""

    logical_id: str
    name: str
    path: str
    method: str
    result_type: object
    handler: Callable[..., ResultT]
    handler_signature: inspect.Signature
    app_id: str
    fallback: str | None
    descriptor: BaseHandleDescriptor
    type_meta: Any = None
    __wrapped__: Callable[..., ResultT] | None = None

    @property
    def schema(self) -> object | None:
        meta = self.type_meta
        return None if meta is None else getattr(meta, "schema", None)

    @property
    def input_model(self) -> object | None:
        meta = self.type_meta
        return None if meta is None else getattr(meta, "model_type", None)

    def form(
        self,
        *,
        value: object | None = None,
        errors: Sequence[object] = (),
        submit_label: str = "Submit",
        controls: Mapping[str, object] | None = None,
        fallback: str | None = None,
        **safe_form_attrs: object,
    ) -> NodeLike:
        from hedron.type_authoring.forms import generate_form

        if self.type_meta is None:
            raise error(
                HED_TYPE_0005,
                title="form() requires a FormBody boundary",
                explanation="Unmodeled commands keep explicit Form(action=handle).",
                remediation="Mark a FormBody parameter or build Form(action=handle) manually.",
            )
        return generate_form(
            self.type_meta,
            action=self,
            value=value,
            errors=errors,
            submit_label=submit_label,
            controls=controls,  # type: ignore[arg-type]
            fallback=fallback or self.fallback,
            **safe_form_attrs,
        )

    @property
    def bound(self) -> bool:
        return True

    @property
    def dom_id(self) -> str:
        return self.logical_id

    @property
    def selector(self) -> str:
        return ""

    @property
    def region(self) -> FragmentRegion:
        return FragmentRegion(id=self.logical_id, selector=f"#{self.logical_id}")

    def button(self, label: str, **kwargs: object) -> NodeLike:
        fallback = str(kwargs.get("fallback") or self.fallback or "")
        attrs: dict[str, object] = {
            "type": "button" if fallback else "submit",
            "hx-swap": kwargs.pop("hx-swap", "none"),
            "data-hedron-command": self.logical_id,
        }
        method = self.method.upper()
        if method == "POST":
            attrs["hx-post"] = self.path
        elif method == "PUT":
            attrs["hx-put"] = self.path
        elif method == "PATCH":
            attrs["hx-patch"] = self.path
        elif method == "DELETE":
            attrs["hx-delete"] = self.path
        elif method in {"GET", "HEAD", "OPTIONS", "TRACE"}:
            raise error(
                HED_CMD_0001,
                title="Command cannot use a safe method",
                explanation="Action handles must not silently downgrade to GET.",
                remediation="Use POST or another unsafe method.",
            )
        if fallback:
            attrs["data-hedron-fallback"] = fallback
        attrs = {key: value for key, value in attrs.items() if value is not None}
        return html.button(label, **cast(dict[str, HtmlAttrValue], attrs))


class Refresh:
    """Native refresh control derived from a fragment handle."""

    def __init__(
        self,
        target: FragmentHandle[Any, Any] | BoundFragment[Any],
        *,
        label: str = "Refresh",
        **kwargs: object,
    ) -> None:
        handle = target.handle if isinstance(target, BoundFragment) else target
        if not handle.bound:
            raise error(
                HED_VIEW_0003,
                title="Unbound parameterized handle",
                explanation=f"View {handle.logical_id!r} must be bound before Refresh.",
                remediation="Call bind() first.",
            )
        self._handle = handle
        self._label = label
        self._kwargs = kwargs

    def render(self) -> NodeLike:
        attrs = {
            "type": "button",
            "hx-get": self._handle.path,
            "hx-target": self._handle.selector,
            "hx-swap": "outerHTML",
            "hx-sync": "this:drop",
        }
        fallback = self._handle.fallback
        if fallback:
            attrs["data-hedron-fallback"] = fallback
        return html.button(self._label, **attrs)

    def __hedron_node__(self) -> NodeLike:
        return self.render()


def refresh(*targets: FragmentHandle[Any, Any] | BoundFragment[Any]) -> RefreshIntent:
    resolved: list[FragmentHandle[Any, Any] | BoundFragment[Any]] = []
    for item in targets:
        handle = item.handle if isinstance(item, BoundFragment) else item
        if not handle.bound:
            raise error(
                HED_VIEW_0003,
                title="Unbound parameterized handle",
                explanation=f"View {handle.logical_id!r} must be bound before refresh().",
                remediation="Call bind() first.",
            )
        resolved.append(item)
    if len(resolved) > MAX_REFRESH_TARGETS:
        raise error(
            HED_VIEW_0004,
            title="Refresh target limit exceeded",
            explanation=(
                f"refresh() received {len(resolved)} targets; max is {MAX_REFRESH_TARGETS}."
            ),
            remediation="Reduce fan-out; refresh is not atomic.",
        )
    return RefreshIntent(targets=cast(tuple[UpdateTarget, ...], tuple(resolved)))


def patches(
    primary: Patch[Any],
    *secondary: Patch[Any],
    toast: NodeLike | str | None = None,
    cache: CacheHint | None = "vary-htmx",
    status_code: int = 200,
) -> PatchSet:
    return PatchSet(
        primary=primary,
        secondary=secondary,
        toast=toast,
        cache=cache,
        status_code=status_code,
    )


def wrap_refreshable_result(handle: FragmentHandle[Any, Any], result: object) -> object:
    if isinstance(result, (InteractionResult, Patch, PatchSet, RefreshIntent)):
        return result
    url = _bound_url(handle._bound) if handle._bound is not None else handle.path
    return handle.host.materialize(
        cast(NodeLike, result),
        dom_id=handle.dom_id,
        get_url=url,
        event_name=refresh_event_name(handle.dom_id),
        logical_id=handle.logical_id,
        fallback=handle.fallback,
    )


def _call_arguments(
    handle: FragmentHandle[Any, Any], args: tuple[Any, ...], kwargs: dict[str, Any]
) -> dict[str, Any]:
    try:
        bound = handle.renderer_signature.bind_partial(*args, **kwargs)
    except TypeError:
        return dict(kwargs)
    return dict(bound.arguments)


def _materialize_request_handle(
    handle: FragmentHandle[Any, Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> FragmentHandle[Any, Any]:
    """Bind GET path/query the same way ``handle.bind`` did on the page.

    FastAPI injects default query values even when the URL omitted them. Using those
    defaults would change the instance token vs ``bind(item_id=...)`` without query.
    """
    plan = handle.binding_plan
    if not plan.path_params and not plan.query_params:
        return handle
    from hedron.routing.router import current_request

    arguments = _call_arguments(handle, args, kwargs)
    values: dict[str, object] = {}
    for name in plan.path_params:
        if name in arguments:
            values[name] = arguments[name]
    request = current_request.get()
    query_names: set[str] = set()
    if request is not None:
        query_names = {str(key) for key in request.query_params}
    for name in plan.query_params:
        if name in query_names and name in arguments:
            values[name] = arguments[name]
    if not values:
        return handle
    return handle.bind(**values).handle


def build_view_handle(
    fn: Callable[..., ContentT],
    *,
    app_id: str,
    path: str | None,
    key: str | None,
    name: str | None,
    host: FragmentHost | None,
    fallback: str | None,
    include_in_schema: bool,
    mount_path: str = "",
) -> FragmentHandle[Mapping[str, object], ContentT]:
    logical = validate_explicit_key(key) if key else normalize_logical_id(name or fn.__name__)
    from hedron.type_authoring import inspect_handler
    from hedron_core.type_schema import attach_type_schema

    compiled = inspect_handler(
        fn,
        kind="view",
        path=path,
        handler_name=name or fn.__name__,
        fallback=fallback,
    )
    plan = compiled.binding_plan if compiled.modeled else binding_plan_for(fn)
    route_path = path or generated_view_path(logical, plan.path_params, mount_path=mount_path)
    if compiled.modeled and path:
        compiled = inspect_handler(
            fn,
            kind="view",
            path=route_path,
            handler_name=name or fn.__name__,
            fallback=fallback,
        )
        plan = compiled.binding_plan
    if fallback is None and (include_in_schema or (path is not None)):
        pass
    if fallback is not None:
        SafeUrl.parse(fallback, purpose=UrlPurpose.NAVIGATION)
    region = FragmentRegion(
        id=safe_dom_id(logical), selector=f"#{safe_dom_id(logical)}", description=fn.__name__
    )
    descriptor = BaseHandleDescriptor(
        kind="view",
        app_id=app_id,
        logical_id=logical,
        name=name or fn.__name__,
        path=route_path,
        method="GET",
        host_tag=(host.props.tag if host is not None else "div"),
        swap="outerHTML",
        fallback=fallback,
        include_in_schema=include_in_schema,
        binding=plan,
        effect="dynamic",
    )
    if compiled.schema is not None:
        descriptor = attach_type_schema(descriptor, compiled.schema)
    register_handle_descriptor(descriptor, key=key)
    handle = FragmentHandle(
        logical_id=logical,
        name=name or fn.__name__,
        path=route_path,
        method="GET",
        dom_id=safe_dom_id(logical),
        selector=region.selector,
        region=region,
        ref=ComponentRef(
            logical_id=logical,
            path=route_path,
            method="GET",
            target=region.selector,
            swap="outerHTML",
        ),
        renderer=fn,
        renderer_signature=inspect.signature(fn),
        app_id=app_id,
        host=host or FragmentHost(),
        fallback=fallback,
        binding_plan=plan,
        descriptor=descriptor,
        include_in_schema=include_in_schema,
        adapter=compiled.adapter,
        type_meta=compiled if compiled.modeled or compiled.schema is not None else None,
        __wrapped__=fn,
    )
    return handle


def build_command_handle(
    fn: Callable[..., ResultT],
    *,
    app_id: str,
    path: str | None,
    method: str,
    name: str | None,
    fallback: str | None,
    include_in_schema: bool,
    mount_path: str = "",
) -> ActionHandle[Mapping[str, object], ResultT]:
    verb = method.upper()
    if verb in {"GET", "HEAD", "OPTIONS", "TRACE"}:
        raise error(
            HED_CMD_0001,
            title="Command cannot use a safe method",
            explanation=f"method={verb!r} would downgrade an unsafe command.",
            remediation="Keep POST (default) or another unsafe method.",
        )
    logical = normalize_logical_id(name or fn.__name__)
    from hedron.type_authoring import inspect_handler
    from hedron_core.type_schema import attach_type_schema

    compiled = inspect_handler(
        fn,
        kind="command",
        path=path,
        handler_name=name or fn.__name__,
        fallback=fallback,
        outcomes=getattr(fn, "__hedron_outcomes__", None),
    )
    plan = compiled.binding_plan if compiled.modeled else binding_plan_for(fn)
    route_path = path or generated_command_path(logical, plan.path_params, mount_path=mount_path)
    if fallback is not None:
        SafeUrl.parse(fallback, purpose=UrlPurpose.NAVIGATION)
    descriptor = BaseHandleDescriptor(
        kind="command",
        app_id=app_id,
        logical_id=logical,
        name=name or fn.__name__,
        path=route_path,
        method=verb,
        fallback=fallback,
        include_in_schema=include_in_schema,
        binding=plan,
        effect="dynamic",
    )
    if compiled.schema is not None:
        descriptor = attach_type_schema(descriptor, compiled.schema)
    register_handle_descriptor(descriptor)
    return ActionHandle(
        logical_id=logical,
        name=name or fn.__name__,
        path=route_path,
        method=verb,
        result_type=inspect.signature(fn).return_annotation,
        handler=fn,
        handler_signature=inspect.signature(fn),
        app_id=app_id,
        fallback=fallback,
        descriptor=descriptor,
        type_meta=compiled if compiled.modeled or compiled.schema is not None else None,
        __wrapped__=fn,
    )


def wrap_endpoint_result(handle: FragmentHandle[Any, Any]) -> Callable[..., Any]:
    from hedron.type_authoring import apply_modeled_signature, reconstruct_kwargs

    @functools.wraps(handle.renderer)
    def wrapped(*args: Any, **kwargs: Any) -> object:
        resolved = _materialize_request_handle(handle, args, kwargs)
        render_kwargs = dict(kwargs)
        meta = handle.type_meta
        if meta is not None and getattr(meta, "modeled", False):
            render_kwargs = reconstruct_kwargs(meta, render_kwargs)
        result = handle.renderer(*args, **render_kwargs)
        if inspect.iscoroutine(result):

            async def _async() -> object:
                return wrap_refreshable_result(resolved, await result)

            return _async()
        return wrap_refreshable_result(resolved, result)

    meta = handle.type_meta
    if meta is not None and getattr(meta, "modeled", False):
        wrapped.__signature__ = apply_modeled_signature(handle.renderer, meta)  # type: ignore[attr-defined]
    else:
        wrapped.__signature__ = handle.renderer_signature  # type: ignore[attr-defined]
    wrapped.__wrapped__ = handle.renderer  # type: ignore[attr-defined]
    wrapped.__module__ = getattr(handle.renderer, "__module__", None) or "hedron.handles"
    wrapped.__name__ = getattr(handle.renderer, "__name__", "refreshable")
    wrapped._hedron_view_logical_id = handle.logical_id  # type: ignore[attr-defined]
    return wrapped
