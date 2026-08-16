"""Optional class handlers compiled to 0.43 functions."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any, Generic, TypeVar

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

    def load(self, *args: Any, **kwargs: Any) -> DataT:
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

    def execute(self, *args: Any, **kwargs: Any) -> ResultT:
        raise error(
            HED_TYPE_0008,
            title="CommandHandler.execute is required",
            explanation=f"{type(self).__name__} must implement execute().",
            remediation="Put mutations only in execute().",
        )


def _reject_instance(target: object) -> type[Any]:
    if inspect.isclass(target):
        return target
    raise error(
        HED_TYPE_0008,
        title="Shared handler instance is not a registration target",
        explanation="Register the class, not a shared instance that could retain request state.",
        remediation="Pass the class (or a per-request factory that returns a fresh instance).",
    )


def compile_view_class(cls: type[RefreshableView[Any, Any]]) -> Callable[..., Any]:
    view_cls = _reject_instance(cls)
    if not issubclass(view_cls, RefreshableView):
        raise error(
            HED_TYPE_0008,
            title="Not a RefreshableView",
            explanation=f"{view_cls!r} does not subclass RefreshableView.",
            remediation="Subclass hedron.RefreshableView.",
        )
    load = view_cls.load
    render = view_cls.render
    if load is RefreshableView.load or render is RefreshableView.render:
        raise error(
            HED_TYPE_0008,
            title="Incomplete RefreshableView",
            explanation="Both load and render must be implemented.",
            remediation="Implement load(...) and render(data).",
        )

    async def endpoint(*args: Any, **kwargs: Any) -> Any:
        instance = view_cls()
        data = load(instance, *args, **kwargs)
        if inspect.isawaitable(data):
            data = await data
        result = render(instance, data)
        if inspect.isawaitable(result):
            raise error(
                HED_TYPE_0008,
                title="render must be deterministic",
                explanation="RefreshableView.render cannot be async request I/O.",
                remediation="Keep awaitables in load().",
            )
        return result

    load_sig = inspect.signature(load)
    params = [item for name, item in load_sig.parameters.items() if name != "self"]
    endpoint.__signature__ = inspect.Signature(params)  # type: ignore[attr-defined]
    endpoint.__name__ = getattr(view_cls, "__name__", "refreshable_view")
    endpoint.__wrapped__ = load  # type: ignore[attr-defined]
    endpoint.__hedron_handler_class__ = view_cls  # type: ignore[attr-defined]
    annotations: dict[str, Any] = {}
    for name, param in load_sig.parameters.items():
        if name == "self":
            continue
        if param.annotation is not inspect.Parameter.empty:
            annotations[name] = param.annotation
    endpoint.__annotations__ = annotations
    return endpoint


def compile_command_class(cls: type[CommandHandler[Any, Any]]) -> Callable[..., Any]:
    command_cls = _reject_instance(cls)
    if not issubclass(command_cls, CommandHandler):
        raise error(
            HED_TYPE_0008,
            title="Not a CommandHandler",
            explanation=f"{command_cls!r} does not subclass CommandHandler.",
            remediation="Subclass hedron.CommandHandler.",
        )
    execute = command_cls.execute
    if execute is CommandHandler.execute:
        raise error(
            HED_TYPE_0008,
            title="Incomplete CommandHandler",
            explanation="execute must be implemented.",
            remediation="Implement execute(...).",
        )

    async def endpoint(*args: Any, **kwargs: Any) -> Any:
        instance = command_cls()
        result = execute(instance, *args, **kwargs)
        if inspect.isawaitable(result):
            result = await result
        return result

    exec_sig = inspect.signature(execute)
    params = [item for name, item in exec_sig.parameters.items() if name != "self"]
    endpoint.__signature__ = inspect.Signature(params)  # type: ignore[attr-defined]
    endpoint.__name__ = getattr(command_cls, "__name__", "command_handler")
    endpoint.__wrapped__ = execute  # type: ignore[attr-defined]
    endpoint.__hedron_handler_class__ = command_cls  # type: ignore[attr-defined]
    annotations: dict[str, Any] = {}
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


def class_config_conflict(
    cls: type[Any], *, decorator_fallback: str | None, decorator_path: str | None
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
