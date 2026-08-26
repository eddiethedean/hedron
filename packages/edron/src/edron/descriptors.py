from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, ParamSpec, TypeVar, overload

from edron._internal import require_frame
from edron.errors import PhaseError, RegistrationError

P = ParamSpec("P")
R = TypeVar("R")


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

    @property
    def logical_id(self) -> str:
        return self.action.logical_id

    def bind(self, **arguments: Any) -> BoundAction[P, R]:
        merged = dict(self.arguments)
        merged.update(arguments)
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
