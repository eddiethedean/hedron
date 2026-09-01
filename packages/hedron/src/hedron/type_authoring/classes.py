"""Optional class handlers compiled to 0.43 functions."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Generic, TypeVar, cast

from hedron.type_authoring.markers import Refreshes, Updates
from hedron.type_authoring.outcomes import OutcomeMap
from hedron_core.codes import HED_TYPE_0008
from hedron_core.component import NodeLike
from hedron_core.diagnostics import error
from hedron_core.hosts import FragmentHost
from hedron_core.htmx.policy import CacheHint

ParamsT = TypeVar("ParamsT")
DataT = TypeVar("DataT")
InputT = TypeVar("InputT")
ResultT = TypeVar("ResultT")

__all__ = ["CommandHandler", "RefreshableView", "compile_command_class", "compile_view_class"]


class RefreshableView(Generic[ParamsT, DataT]):
    """Optional load/render lifecycle. ``load`` is the DI entrypoint."""

    host: FragmentHost | None = None
    loading: NodeLike | None = None
    empty: NodeLike | None = None
    error: NodeLike | str | None = None
    cache: CacheHint | None = None
    fallback: str | None = None

    def load(self, *args: object, **kwargs: object) -> DataT | Awaitable[DataT]:
        raise error(
            HED_TYPE_0008,
            title="RefreshableView.load is required",
            explanation=f"{type(self).__name__} must implement load().",
            remediation="Implement load as the request/DI entrypoint.",
        )

    def render(self, data: DataT) -> NodeLike:
        raise error(
            HED_TYPE_0008,
            title="RefreshableView.render is required",
            explanation=f"{type(self).__name__} must implement render(data).",
            remediation="Keep render deterministic and free of request I/O.",
        )


class CommandHandler(Generic[InputT, ResultT]):
    """Optional execute/outcome lifecycle. Only ``execute`` may mutate."""

    outcomes: OutcomeMap[ResultT] | None = None
    fallback: str | None = None
    effects: Refreshes | Updates | tuple[Refreshes | Updates, ...] | None = None

    def execute(self, *args: object, **kwargs: object) -> ResultT | Awaitable[ResultT]:
        raise error(
            HED_TYPE_0008,
            title="CommandHandler.execute is required",
            explanation=f"{type(self).__name__} must implement execute().",
            remediation="Put mutations only in execute().",
        )


def _reject_instance(target: object) -> type[object]:
    if inspect.isclass(target):
        return target
    raise error(
        HED_TYPE_0008,
        title="Shared handler instance is not a registration target",
        explanation="Register the class, not a shared instance that could retain request state.",
        remediation="Pass the class (or a per-request factory that returns a fresh instance).",
    )


def _is_subclass(target: object, base: type[object]) -> bool:
    return inspect.isclass(target) and issubclass(target, base)


def _stamp_callable(target: Callable[..., object], **attributes: object) -> None:
    for name, value in attributes.items():
        setattr(target, name, value)


def compile_view_class(
    cls: type[RefreshableView[ParamsT, DataT]],
) -> Callable[..., object]:
    _reject_instance(cast(object, cls))
    if not _is_subclass(cls, RefreshableView):
        raise error(
            HED_TYPE_0008,
            title="Not a RefreshableView",
            explanation=f"{cls!r} does not subclass RefreshableView.",
            remediation="Subclass hedron.RefreshableView.",
        )
    load = cls.load
    render = cls.render
    if load is RefreshableView.__dict__.get("load") or render is RefreshableView.__dict__.get(
        "render"
    ):
        raise error(
            HED_TYPE_0008,
            title="Incomplete RefreshableView",
            explanation="Both load and render must be implemented.",
            remediation="Implement load(...) and render(data).",
        )

    async def endpoint(*args: object, **kwargs: object) -> object:
        instance = cls()
        loaded = load(instance, *args, **kwargs)
        data = (
            await cast(Awaitable[DataT], loaded)
            if inspect.isawaitable(loaded)
            else cast(DataT, loaded)
        )
        empty = cls.empty
        if empty is not None and _is_empty_view_data(data):
            return empty
        result = render(instance, data)
        if inspect.isawaitable(result):
            close = getattr(result, "close", None)
            if callable(close):
                close()
            raise error(
                HED_TYPE_0008,
                title="render must be deterministic",
                explanation="RefreshableView.render cannot be async request I/O.",
                remediation="Keep awaitables in load().",
            )
        return result

    load_sig = inspect.signature(load)
    params = [item for name, item in load_sig.parameters.items() if name != "self"]
    endpoint.__name__ = cls.__name__
    _stamp_callable(
        endpoint,
        __signature__=inspect.Signature(params),
        __wrapped__=load,
        __hedron_handler_class__=cls,
    )
    annotations: dict[str, object] = {}
    for name, param in load_sig.parameters.items():
        if name == "self":
            continue
        if param.annotation is not inspect.Parameter.empty:
            annotations[name] = param.annotation
    endpoint.__annotations__ = annotations
    return endpoint


def compile_command_class(
    cls: type[CommandHandler[InputT, ResultT]],
) -> Callable[..., object]:
    _reject_instance(cast(object, cls))
    if not _is_subclass(cls, CommandHandler):
        raise error(
            HED_TYPE_0008,
            title="Not a CommandHandler",
            explanation=f"{cls!r} does not subclass CommandHandler.",
            remediation="Subclass hedron.CommandHandler.",
        )
    execute = cls.execute
    if execute is CommandHandler.__dict__.get("execute"):
        raise error(
            HED_TYPE_0008,
            title="Incomplete CommandHandler",
            explanation="execute must be implemented.",
            remediation="Implement execute(...).",
        )

    async def endpoint(*args: object, **kwargs: object) -> object:
        instance = cls()
        result = execute(instance, *args, **kwargs)
        return await result if inspect.isawaitable(result) else result

    exec_sig = inspect.signature(execute)
    params = [item for name, item in exec_sig.parameters.items() if name != "self"]
    endpoint.__name__ = cls.__name__
    _stamp_callable(
        endpoint,
        __signature__=inspect.Signature(params),
        __wrapped__=execute,
        __hedron_handler_class__=cls,
    )
    annotations: dict[str, object] = {}
    for name, param in exec_sig.parameters.items():
        if name == "self":
            continue
        if param.annotation is not inspect.Parameter.empty:
            annotations[name] = param.annotation
    ret = exec_sig.return_annotation
    if ret is not inspect.Parameter.empty:
        annotations["return"] = ret
    endpoint.__annotations__ = annotations
    return endpoint


def _is_empty_view_data(data: object) -> bool:
    if data is None:
        return True
    if isinstance(data, (str, bytes)):
        return len(data) == 0
    if isinstance(data, Mapping):
        return len(cast(Mapping[object, object], data)) == 0
    if isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
        return len(cast(Sequence[object], data)) == 0
    return False


def class_config_conflict(
    cls: type[object], *, decorator_fallback: str | None, decorator_path: str | None
) -> None:
    class_fallback = getattr(cls, "fallback", None)
    if (
        decorator_fallback
        and class_fallback
        and decorator_fallback != class_fallback
        and class_fallback is not None
    ):
        raise error(
            HED_TYPE_0008,
            title="Decorator/class fallback conflict",
            explanation="fallback= on the decorator disagrees with the class attribute.",
            remediation="Set fallback in only one place.",
        )
    class_path = getattr(cls, "path", None)
    if decorator_path and class_path and decorator_path != class_path:
        raise error(
            HED_TYPE_0008,
            title="Decorator/class path conflict",
            explanation="path on the decorator disagrees with the class attribute.",
            remediation="Set path in only one place.",
        )
