from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Annotated, Any, Generic, ParamSpec, TypeVar, get_args, get_origin, overload

from fastapi.params import Depends as DependsParam

from edron._internal import require_frame
from edron.errors import BindingError, PhaseError, RegistrationError

P = ParamSpec("P")
R = TypeVar("R")


def _application_parameters(fn: Callable[..., Any]) -> dict[str, inspect.Parameter]:
    parameters = inspect.signature(fn).parameters
    result: dict[str, inspect.Parameter] = {}
    for name, parameter in parameters.items():
        if name in {"self", "cls", "request", "websocket"}:
            continue
        if isinstance(parameter.default, DependsParam):
            continue
        annotation = parameter.annotation
        if get_origin(annotation) is Annotated and any(
            isinstance(item, DependsParam) for item in get_args(annotation)[1:]
        ):
            continue
        result[name] = parameter
    return result


def _validate_action_bind(action: Action[Any, Any], arguments: dict[str, Any]) -> None:
    application_parameters = _application_parameters(action.fn)
    unknown = sorted(set(arguments) - set(application_parameters))
    if unknown:
        raise BindingError(
            f"unknown action argument(s): {', '.join(unknown)}", code="EDRON_ACTION_BIND"
        )
    try:
        inspect.signature(action.fn).bind_partial(**arguments)
    except TypeError as exc:
        raise BindingError(str(exc), code="EDRON_ACTION_BIND") from exc


@dataclass
class BoundFragment(Generic[P]):
    fragment: Fragment[P]
    arguments: dict[str, Any] = field(default_factory=dict)

    @property
    def logical_id(self) -> str:
        return self.fragment.logical_id

    def bind(self, **arguments: Any) -> BoundFragment[P]:
        merged = dict(self.arguments)
        merged.update(arguments)
        return BoundFragment(self.fragment, merged)

    def __call__(self, **arguments: Any) -> None:
        merged = dict(self.arguments)
        merged.update(arguments)
        frame = require_frame("page", "fragment")
        frame.app._mount_fragment(self.fragment, merged)


@dataclass
class Fragment(Generic[P]):
    fn: Callable[..., Any]
    path: str | None = None
    name: str | None = None
    fallback: str | None = None
    dependencies: tuple[Any, ...] = ()
    _owner: type[Any] | None = field(default=None, init=False, repr=False)
    _native: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.name = self.name or self.fn.__name__
        self._signature = inspect.signature(self.fn)

    @property
    def logical_id(self) -> str:
        if self._native is not None:
            return getattr(self._native, "logical_id", self.name or self.fn.__name__)
        return self.name or self.fn.__name__

    def __set_name__(self, owner: type[Any], name: str) -> None:
        self._owner = owner
        if self.name is None or self.name == self.fn.__name__:
            self.name = name

    def __get__(self, instance: Any, owner: type[Any] | None = None) -> Any:
        if instance is None:
            return self
        return BoundFragment(self)

    def bind(self, **arguments: Any) -> BoundFragment[P]:
        return BoundFragment(self, dict(arguments))


@dataclass
class BoundAction(Generic[P, R]):
    action: Action[P, R]
    arguments: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_action_bind(self.action, self.arguments)

    @property
    def logical_id(self) -> str:
        return self.action.logical_id

    def bind(self, **arguments: Any) -> BoundAction[P, R]:
        merged = dict(self.arguments)
        merged.update(arguments)
        _validate_action_bind(self.action, merged)
        return BoundAction(self.action, merged)

    def __call__(self, **_: Any) -> Any:
        raise PhaseError(
            "actions are values used by controls; invoke them through HTTP or a test client",
            code="EDRON_ACTION_CALL",
        )


@dataclass
class Action(Generic[P, R]):
    fn: Callable[..., Any]
    method: str = "post"
    path: str | None = None
    name: str | None = None
    fallback: str | None = None
    idempotency: str = "optional"
    updates: Any = None
    dependencies: tuple[Any, ...] = ()
    _owner: type[Any] | None = field(default=None, init=False, repr=False)
    _native: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.name = self.name or self.fn.__name__
        self._signature = inspect.signature(self.fn)
        if self.method.lower() not in {"post", "put", "patch", "delete"}:
            raise RegistrationError(
                "actions must use an unsafe HTTP method", code="EDRON_ACTION_METHOD"
            )

    @property
    def logical_id(self) -> str:
        if self._native is not None:
            return getattr(self._native, "logical_id", self.name or self.fn.__name__)
        return self.name or self.fn.__name__

    def __set_name__(self, owner: type[Any], name: str) -> None:
        self._owner = owner
        if self.name is None or self.name == self.fn.__name__:
            self.name = name

    def __get__(self, instance: Any, owner: type[Any] | None = None) -> Any:
        if instance is None:
            return self
        return BoundAction(self)

    def bind(self, **arguments: Any) -> BoundAction[P, R]:
        _validate_action_bind(self, arguments)
        return BoundAction(self, dict(arguments))


@overload
def fragment(fn: Callable[..., Any]) -> Fragment[Any]: ...


@overload
def fragment(
    *,
    path: str | None = None,
    name: str | None = None,
    fallback: str | None = None,
    dependencies: tuple[Any, ...] = (),
) -> Callable[[Callable[..., Any]], Fragment[Any]]: ...


def fragment(fn: Callable[..., Any] | None = None, **kwargs: Any) -> Any:
    if fn is not None and callable(fn):
        return Fragment(fn)

    def decorate(wrapped: Callable[..., Any]) -> Fragment[Any]:
        return Fragment(wrapped, **kwargs)

    return decorate


@overload
def action(fn: Callable[..., Any]) -> Action[Any, Any]: ...


@overload
def action(
    *,
    method: str = "post",
    path: str | None = None,
    name: str | None = None,
    fallback: str | None = None,
    idempotency: str = "optional",
    updates: Any = None,
    dependencies: tuple[Any, ...] = (),
) -> Callable[[Callable[..., Any]], Action[Any, Any]]: ...


def action(fn: Callable[..., Any] | None = None, **kwargs: Any) -> Any:
    if fn is not None and callable(fn):
        return Action(fn)

    def decorate(wrapped: Callable[..., Any]) -> Action[Any, Any]:
        return Action(wrapped, **kwargs)

    return decorate
