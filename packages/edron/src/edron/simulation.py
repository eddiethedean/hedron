"""The small public execution boundary used by Edron tooling.

This module deliberately does not define a second component or routing model.
It exposes the already-registered Edron callbacks to tooling such as
``edron-sim`` while keeping the registration tables private to :class:`App`.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol, cast
from urllib.parse import urlencode

from starlette.requests import Request

from edron.dependencies import Dependency
from edron.errors import EdronError
from hedron_core.typing_support import (
    awaitable_value,
    class_namespace,
    dynamic_attribute,
    parameter_default,
)

__all__ = [
    "AppSimulation",
    "SimulationRegion",
    "SimulationRequest",
    "SimulationResponse",
    "SimulationRoute",
    "SimulationError",
]


@dataclass(frozen=True, slots=True)
class SimulationRegion:
    """A serializable fragment target declaration."""

    id: str
    selector: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class SimulationRequest:
    """Deterministic request input for an Edron simulation.

    ``values`` represents path/query/form values passed to the registered
    callback. It is intentionally explicit: the simulator never invents a
    database, identity, clock, or network response.
    """

    method: str = "GET"
    path: str = "/"
    values: Mapping[str, object] = field(default_factory=dict[str, object])
    headers: Mapping[str, str] = field(default_factory=dict[str, str])

    def __post_init__(self) -> None:
        method = self.method.upper().strip()
        path = self.path.strip() or "/"
        if not path.startswith("/"):
            raise ValueError("simulation request paths must begin with '/'")
        if not method:
            raise ValueError("simulation request method must not be empty")
        object.__setattr__(self, "method", method)
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "values", {str(key): value for key, value in self.values.items()})
        object.__setattr__(
            self,
            "headers",
            {str(key).lower(): str(value) for key, value in self.headers.items()},
        )


@dataclass(frozen=True, slots=True)
class SimulationRoute:
    """Metadata for one registered Edron page, fragment, or action."""

    method: str
    path: str
    name: str
    kind: str
    logical_id: str
    regions: tuple[SimulationRegion, ...] = ()

    @property
    def key(self) -> str:
        return f"{self.method.upper()} {self.path}"


@dataclass(frozen=True, slots=True)
class SimulationResponse:
    """The raw value returned by a real Edron callback."""

    route: SimulationRoute
    value: object


class SimulationError(EdronError):
    """Raised when a simulation cannot dispatch a registered route."""


class _SimulationApp(Protocol):
    native: object
    _pages: Mapping[str, object]
    _fragments: Mapping[int, object]
    _actions: Mapping[int, object]


class AppSimulation:
    """Public, deterministic access to an :class:`edron.App`'s callbacks.

    The class is created by :meth:`edron.App.simulation`; applications should
    not construct it directly. It is intentionally an execution boundary, not
    a replacement for the native ASGI application.
    """

    def __init__(self, app: object, *, fixtures: Mapping[str, object] | None = None) -> None:
        self._app = cast(_SimulationApp, app)
        self._fixtures = dict(fixtures or {})
        self._entries: dict[
            str, tuple[SimulationRoute, Callable[..., object], tuple[str, ...]]
        ] = {}
        self._collect_routes()

    @property
    def routes(self) -> tuple[SimulationRoute, ...]:
        """Return routes in deterministic method/path/name order."""
        return tuple(
            entry[0]
            for entry in sorted(
                self._entries.values(),
                key=lambda entry: (entry[0].path, entry[0].method, entry[0].name),
            )
        )

    def route(self, method: str, path: str) -> SimulationRoute:
        """Resolve one route or raise a descriptive simulation error."""
        key = f"{method.upper()} {path or '/'}"
        try:
            return self._entries[key][0]
        except KeyError as exc:
            raise SimulationError(f"no Edron route registered for {key}") from exc

    async def dispatch(
        self,
        route: SimulationRoute | str,
        request: SimulationRequest | None = None,
    ) -> SimulationResponse:
        """Invoke the real Edron callback for ``route``.

        The callback runs with the same request-local Edron frame used by the
        native route adapter. Only explicitly supplied values and fixtures are
        injected; missing values fail closed.
        """
        selected = self._resolve_route(route)
        request = request or SimulationRequest(method=selected.method, path=selected.path)
        if request.method != selected.method or request.path != selected.path:
            raise SimulationError(
                f"simulation request {request.method} {request.path} does not match "
                + f"route {selected.key}"
            )
        _metadata, callback, dependency_names = self._entries[selected.key]
        kwargs = self._callback_kwargs(callback, request.values, dependency_names)

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": request.method,
            "scheme": "http",
            "path": request.path,
            "raw_path": request.path.encode("utf-8"),
            "query_string": urlencode(request.values, doseq=True).encode("utf-8"),
            "root_path": "",
            "headers": [
                (key.encode("latin-1"), value.encode("latin-1"))
                for key, value in request.headers.items()
            ],
            "client": ("edron-sim", 0),
            "server": ("edron-sim", 80),
            "app": self._app.native,
        }

        async def receive() -> dict[str, object]:
            return {"type": "http.request", "body": b"", "more_body": False}

        native_request = Request(scope, receive)
        from hedron.routing.router import current_request

        token = current_request.set(native_request)
        try:
            value = callback(**kwargs)
            pending = awaitable_value(value)
            if pending is not None:
                value = await pending
        except Exception as exc:
            if isinstance(exc, EdronError):
                raise
            raise SimulationError(f"{selected.key} could not be simulated: {exc}") from exc
        finally:
            current_request.reset(token)
        return SimulationResponse(route=selected, value=value)

    def _resolve_route(self, route: SimulationRoute | str) -> SimulationRoute:
        if isinstance(route, SimulationRoute):
            if route.key not in self._entries:
                raise SimulationError(f"route {route.key} does not belong to this app")
            return self._entries[route.key][0]
        if " " in route:
            try:
                return self._entries[route][0]
            except KeyError as exc:
                raise SimulationError(f"no Edron route registered for {route}") from exc
        return self.route("GET", route)

    def _callback_kwargs(
        self,
        callback: Callable[..., object],
        values: Mapping[str, object],
        dependency_names: tuple[str, ...],
    ) -> dict[str, object]:
        try:
            parameters = inspect.signature(callback).parameters
        except (TypeError, ValueError) as exc:
            raise SimulationError(f"cannot inspect simulation callback {callback!r}") from exc
        kwargs = {name: value for name, value in values.items() if name in parameters}
        for index, name in enumerate(dependency_names):
            key = f"__edron_dep_{index}"
            if key in parameters and name in self._fixtures:
                kwargs[key] = self._fixtures[name]
            elif key in parameters and key in self._fixtures:
                kwargs[key] = self._fixtures[key]
        missing = [
            name
            for name, parameter in parameters.items()
            if parameter_default(parameter) is inspect.Parameter.empty
            and parameter.kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            )
            and name not in kwargs
        ]
        if missing:
            raise SimulationError(
                f"{callback.__name__} requires simulation values for: {', '.join(missing)}"
            )
        return kwargs

    def _collect_routes(self) -> None:
        for record in self._app._pages.values():
            page = cast(Mapping[str, object], record)
            route = SimulationRoute(
                method="GET",
                path=str(page.get("path", "/")),
                name=str(page.get("name", "page")),
                kind="page",
                logical_id=str(page.get("name", "page")),
            )
            callback = page.get("native")
            if callable(callback):
                self._add(
                    route,
                    cast(Callable[..., object], cast(object, callback)),
                    page.get("dependencies", ()),
                )

        for kind, registry in (("fragment", self._app._fragments), ("action", self._app._actions)):
            for handle in registry.values():
                callback_value = dynamic_attribute(handle, "renderer") or dynamic_attribute(
                    handle, "handler"
                )
                if not callable(callback_value):
                    continue
                callback_object: object = callback_value
                callback = cast(Callable[..., object], callback_object)
                region = dynamic_attribute(handle, "region")
                regions = ()
                if region is not None:
                    regions = (
                        SimulationRegion(
                            id=str(dynamic_attribute(region, "id", "")),
                            selector=str(dynamic_attribute(region, "selector", "")),
                            description=str(dynamic_attribute(region, "description", "")),
                        ),
                    )
                route = SimulationRoute(
                    method=str(dynamic_attribute(handle, "method", "GET")).upper(),
                    path=str(dynamic_attribute(handle, "path", "/")),
                    name=str(dynamic_attribute(handle, "name", kind)),
                    kind=kind,
                    logical_id=str(
                        dynamic_attribute(
                            handle,
                            "logical_id",
                            dynamic_attribute(handle, "name", kind),
                        )
                    ),
                    regions=regions,
                )
                dependency_names = self._dependencies_for_handle(handle)
                self._add(route, callback, dependency_names)

    def _dependencies_for_handle(self, handle: object) -> tuple[str, ...]:
        for record in self._app._pages.values():
            page = cast(Mapping[str, object], record)
            page_type = page.get("type")
            if page_type is None:
                continue
            for member in class_namespace(page_type).values():
                if dynamic_attribute(member, "_native") is not handle:
                    continue
                page_dependencies = page.get("dependencies", ())
                member_dependencies = dynamic_attribute(member, "dependencies", ())
                dependencies: list[object] = []
                if isinstance(page_dependencies, Sequence):
                    dependencies.extend(page_dependencies)
                if isinstance(member_dependencies, Sequence):
                    dependencies.extend(member_dependencies)
                return tuple(
                    dependency.name or f"__edron_dep_{index}"
                    for index, dependency in enumerate(dependencies)
                    if isinstance(dependency, Dependency)
                )
        return ()

    def _add(
        self,
        route: SimulationRoute,
        callback: Callable[..., object],
        dependencies: object,
    ) -> None:
        if route.key in self._entries:
            raise SimulationError(f"duplicate Edron simulation route {route.key}")
        dependency_names = tuple(
            dependency.name or f"__edron_dep_{index}"
            for index, dependency in enumerate(dependencies)
            if isinstance(dependency, Dependency)
        )
        self._entries[route.key] = (route, callback, dependency_names)
