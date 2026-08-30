"""The small public execution boundary used by Edron tooling.

This module deliberately does not define a second component or routing model.
It exposes the already-registered Edron callbacks to tooling such as
``edron-sim`` while keeping the registration tables private to :class:`App`.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlencode

from starlette.requests import Request

from edron.dependencies import Dependency
from edron.errors import EdronError

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
    values: Mapping[str, Any] = field(default_factory=dict[str, Any])
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
    value: Any


class SimulationError(EdronError):
    """Raised when a simulation cannot dispatch a registered route."""


class AppSimulation:
    """Public, deterministic access to an :class:`edron.App`'s callbacks.

    The class is created by :meth:`edron.App.simulation`; applications should
    not construct it directly. It is intentionally an execution boundary, not
    a replacement for the native ASGI application.
    """

    def __init__(self, app: Any, *, fixtures: Mapping[str, Any] | None = None) -> None:
        self._app = app
        self._fixtures = dict(fixtures or {})
        self._entries: dict[str, tuple[SimulationRoute, Callable[..., Any], tuple[str, ...]]] = {}
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
                f"route {selected.key}"
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

        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": b"", "more_body": False}

        native_request = Request(scope, receive)
        from hedron.routing.router import current_request

        token = current_request.set(native_request)
        try:
            value = callback(**kwargs)
            if inspect.isawaitable(value):
                value = await value
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
        callback: Callable[..., Any],
        values: Mapping[str, Any],
        dependency_names: tuple[str, ...],
    ) -> dict[str, Any]:
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
            if parameter.default is inspect.Parameter.empty
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
            route = SimulationRoute(
                method="GET",
                path=str(record["path"]),
                name=str(record["name"]),
                kind="page",
                logical_id=str(record["name"]),
            )
            self._add(route, record["native"], record.get("dependencies", ()))

        for kind, registry in (("fragment", self._app._fragments), ("action", self._app._actions)):
            for handle in registry.values():
                callback = getattr(handle, "renderer", None) or getattr(handle, "handler", None)
                if not callable(callback):
                    continue
                region = getattr(handle, "region", None)
                regions = ()
                if region is not None:
                    regions = (
                        SimulationRegion(
                            id=str(region.id),
                            selector=str(region.selector),
                            description=str(region.description),
                        ),
                    )
                route = SimulationRoute(
                    method=str(getattr(handle, "method", "GET")).upper(),
                    path=str(getattr(handle, "path", "/")),
                    name=str(getattr(handle, "name", kind)),
                    kind=kind,
                    logical_id=str(getattr(handle, "logical_id", getattr(handle, "name", kind))),
                    regions=regions,
                )
                dependency_names = self._dependencies_for_handle(handle)
                self._add(route, callback, dependency_names)

    def _dependencies_for_handle(self, handle: Any) -> tuple[str, ...]:
        for record in self._app._pages.values():
            page_type = record["type"]
            for member in page_type.__dict__.values():
                if getattr(member, "_native", None) is not handle:
                    continue
                dependencies = [
                    *record.get("dependencies", ()),
                    *getattr(member, "dependencies", ()),
                ]
                return tuple(
                    dependency.name or f"__edron_dep_{index}"
                    for index, dependency in enumerate(dependencies)
                    if isinstance(dependency, Dependency)
                )
        return ()

    def _add(
        self,
        route: SimulationRoute,
        callback: Callable[..., Any],
        dependencies: Any,
    ) -> None:
        if route.key in self._entries:
            raise SimulationError(f"duplicate Edron simulation route {route.key}")
        dependency_names = tuple(
            dependency.name or f"__edron_dep_{index}"
            for index, dependency in enumerate(dependencies)
            if isinstance(dependency, Dependency)
        )
        self._entries[route.key] = (route, callback, dependency_names)
