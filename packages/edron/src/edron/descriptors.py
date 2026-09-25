from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Annotated, Generic, ParamSpec, TypeVar, cast, overload

from fastapi.params import Depends as DependsParam

from edron._internal import require_frame
from edron.diagnostics import SourceLocation, source_location
from edron.errors import BindingError, PhaseError, RegistrationError
from hedron_core.typing_support import (
    parameter_annotation,
    parameter_default,
    type_arguments,
    type_origin,
)

P = ParamSpec("P")
R = TypeVar("R")


def _application_parameters(fn: Callable[..., object]) -> dict[str, inspect.Parameter]:
    parameters = inspect.signature(fn).parameters
    result: dict[str, inspect.Parameter] = {}
    for name, parameter in parameters.items():
        if name in {"self", "cls", "request", "websocket"}:
            continue
        if isinstance(parameter_default(parameter), DependsParam):
            continue
        annotation = parameter_annotation(parameter)
        args = type_arguments(annotation)
        if type_origin(annotation) is Annotated and any(
            isinstance(item, DependsParam) for item in args[1:]
        ):
            continue
        result[name] = parameter
    return result


def _validate_action_bind(action: Action[object, object], arguments: dict[str, object]) -> None:
    application_parameters = _application_parameters(action.fn)
    unknown = sorted(set(arguments) - set(application_parameters))
    if unknown:
        raise BindingError(
            f"unknown action argument(s): {', '.join(unknown)}", code="EDRON_ACTION_BIND"
        )
    try:
        _ignored = inspect.signature(action.fn).bind_partial(**arguments)
    except TypeError as exc:
        raise BindingError(str(exc), code="EDRON_ACTION_BIND") from exc


@dataclass
class BoundFragment(Generic[P]):
    fragment: Fragment[P]
    arguments: dict[str, object] = field(default_factory=lambda: dict[str, object]())

    @property
    def logical_id(self) -> str:
        return self.fragment.logical_id

    def bind(self, **arguments: object) -> BoundFragment[P]:
        merged = dict(self.arguments)
        merged.update(arguments)
        return BoundFragment(self.fragment, merged)

    def __call__(self, **arguments: object) -> None:
        merged = dict(self.arguments)
        merged.update(arguments)
        frame = require_frame("page", "fragment")
        frame.app._mount_fragment(self.fragment, merged)


@dataclass
class Fragment(Generic[P]):
    fn: Callable[..., object]
    path: str | None = None
    name: str | None = None
    fallback: str | None = None
    dependencies: tuple[object, ...] = ()
    _owner: type[object] | None = field(default=None, init=False, repr=False)
    _native: object = field(default=None, init=False, repr=False)
    _source: SourceLocation | None = field(default=None, init=False, repr=False)
    _inherited_from: str | None = field(default=None, init=False, repr=False)
    _signature: inspect.Signature = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.name = self.name or self.fn.__name__
        self._signature = inspect.signature(self.fn)
        self._source = source_location(self.fn)

    @property
    def logical_id(self) -> str:
        if self._native is not None:
            return getattr(self._native, "logical_id", self.name or self.fn.__name__)
        return self.name or self.fn.__name__

    def __set_name__(self, owner: type[object], name: str) -> None:
        self._owner = owner
        if self.name is None or self.name == self.fn.__name__:
            self.name = name

    def __get__(self, instance: object, owner: type[object] | None = None) -> object:
        if instance is None:
            return self
        return BoundFragment(self)

    def bind(self, **arguments: object) -> BoundFragment[P]:
        return BoundFragment(self, dict(arguments))


@dataclass
class BoundAction(Generic[P, R]):
    action: Action[P, R]
    arguments: dict[str, object] = field(default_factory=lambda: dict[str, object]())

    def __post_init__(self) -> None:
        _validate_action_bind(self.action, self.arguments)

    @property
    def logical_id(self) -> str:
        return self.action.logical_id

    def bind(self, **arguments: object) -> BoundAction[P, R]:
        merged = dict(self.arguments)
        merged.update(arguments)
        _validate_action_bind(self.action, merged)
        return BoundAction(self.action, merged)

    def __call__(self, **_: object) -> object:
        raise PhaseError(
            "actions are values used by controls; invoke them through HTTP or a test client",
            code="EDRON_ACTION_CALL",
        )


@dataclass
class Action(Generic[P, R]):
    fn: Callable[..., object]
    method: str = "post"
    path: str | None = None
    name: str | None = None
    fallback: str | None = None
    idempotency: str = "optional"
    updates: object = None
    dependencies: tuple[object, ...] = ()
    _owner: type[object] | None = field(default=None, init=False, repr=False)
    _native: object = field(default=None, init=False, repr=False)
    _source: SourceLocation | None = field(default=None, init=False, repr=False)
    _inherited_from: str | None = field(default=None, init=False, repr=False)
    _signature: inspect.Signature = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.name = self.name or self.fn.__name__
        self._signature = inspect.signature(self.fn)
        self._source = source_location(self.fn)
        if self.method.lower() not in {"post", "put", "patch", "delete"}:
            raise RegistrationError(
                "actions must use an unsafe HTTP method", code="EDRON_ACTION_METHOD"
            )

    @property
    def logical_id(self) -> str:
        if self._native is not None:
            return getattr(self._native, "logical_id", self.name or self.fn.__name__)
        return self.name or self.fn.__name__

    def __set_name__(self, owner: type[object], name: str) -> None:
        self._owner = owner
        if self.name is None or self.name == self.fn.__name__:
            self.name = name

    def __get__(self, instance: object, owner: type[object] | None = None) -> object:
        if instance is None:
            return self
        return BoundAction(self)

    def bind(self, **arguments: object) -> BoundAction[P, R]:
        _validate_action_bind(self, arguments)
        return BoundAction(self, dict(arguments))


@overload
def fragment(fn: Callable[..., object]) -> Fragment[object]: ...


@overload
def fragment(
    *,
    path: str | None = None,
    name: str | None = None,
    fallback: str | None = None,
    dependencies: tuple[object, ...] = (),
) -> Callable[[Callable[..., object]], Fragment[object]]: ...


def fragment(fn: Callable[..., object] | None = None, **kwargs: object) -> object:
    if fn is not None and callable(fn):
        return Fragment(fn)

    def decorate(wrapped: Callable[..., object]) -> Fragment[object]:
        return Fragment(wrapped, **kwargs)

    return decorate


@overload
def action(fn: Callable[..., object]) -> Action[object, object]: ...


@overload
def action(
    *,
    method: str = "post",
    path: str | None = None,
    name: str | None = None,
    fallback: str | None = None,
    idempotency: str = "optional",
    updates: object = None,
    dependencies: tuple[object, ...] = (),
) -> Callable[[Callable[..., object]], Action[object, object]]: ...


def action(fn: Callable[..., object] | None = None, **kwargs: object) -> object:
    if fn is not None and callable(fn):
        return Action[object, object](fn)

    def decorate(wrapped: Callable[..., object]) -> Action[object, object]:
        return Action[object, object](wrapped, **kwargs)

    return decorate


def inherit(
    surface: Fragment[P] | Action[P, object], *, name: str | None = None, path: str | None = None
) -> object:
    """Opt in to exposing one descriptor on a subclass.

    Decorated surfaces are never inherited implicitly.  Assigning ``inherit(Base.view)``
    creates a fresh descriptor owned by the subclass, so routes and native handles remain
    app-scoped and a base class cannot accidentally expose a surface.
    """
    raw_surface: object = surface
    if not isinstance(cast(object, raw_surface), (Fragment, Action)):
        raise RegistrationError(
            "inherit expects a Fragment or Action descriptor", code="EDRON_PAGE_TYPE"
        )
    overrides: dict[str, object] = {"name": name or surface.name}
    if path is not None:
        overrides["path"] = path
    cloned = type(surface)(
        surface.fn,
        **{
            field_name: getattr(surface, field_name)
            for field_name in (
                ("path", "fallback", "dependencies")
                if isinstance(surface, Fragment)
                else ("method", "path", "fallback", "idempotency", "updates", "dependencies")
            )
        },
        **overrides,
    )
    cast(object, cloned)._inherited_from = surface.logical_id
    return cloned


expose = inherit
