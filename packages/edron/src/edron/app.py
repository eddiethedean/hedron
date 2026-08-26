from __future__ import annotations

import inspect
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Annotated, Any, get_args, get_origin
from urllib.parse import quote, urlencode, urlsplit, urlunsplit

from pydantic import BaseModel

import hedron
from edron._internal import Frame, frame_context
from edron.dependencies import Dependency
from edron.descriptors import Action, BoundAction, BoundFragment, Fragment
from edron.diagnostics import source_location
from edron.errors import BindingError, RegistrationError
from edron.page import Page

MAX_EXPLANATION_PAGES = 256
MAX_EXPLANATION_SURFACES = 64
MAX_SOURCE_MAP_ENTRIES = 1024


class App:
    """Class-oriented facade over exactly one native :class:`hedron.Hedron` app."""

    def __init__(
        self,
        *,
        title: str,
        theme: Any = None,
        security: Any = "standard",
        session_secret: str | None = None,
        production: bool | None = None,
        build_dir: str | Path | None = None,
        root_path: str | None = None,
        debug: bool = False,
    ) -> None:
        if not isinstance(title, str) or not title.strip():
            raise RegistrationError("App.title must be a non-empty string", code="EDRON_APP_TITLE")
        kwargs: dict[str, Any] = {
            "title": title,
            "security": security,
            "production": production,
            "build_dir": build_dir,
            "root_path": root_path,
            "debug": debug,
        }
        if theme is not None:
            kwargs["theme"] = theme
        if session_secret is not None:
            kwargs["session_secret"] = session_secret
        self.title = title
        self.hedron = hedron.Hedron(**kwargs)
        self._pages: dict[str, Any] = {}
        self._fragments: dict[int, Any] = {}
        self._actions: dict[int, Any] = {}
        self._function_pages: dict[int, type[Page]] = {}
        self._bundles: dict[int, Any] = {}
        self._data_workspaces: dict[str, Any] = {}
        self._sealed = False

    @classmethod
    def from_hedron(cls, app: hedron.Hedron, *, title: str | None = None) -> App:
        if not isinstance(app, hedron.Hedron):
            raise TypeError("from_hedron expects a Hedron instance")
        instance = cls.__new__(cls)
        instance.title = title or getattr(app, "title", "Edron application")
        instance.hedron = app
        instance._pages = {}
        instance._fragments = {}
        instance._actions = {}
        instance._function_pages = {}
        instance._bundles = {}
        instance._data_workspaces = {}
        instance._sealed = False
        return instance

    @property
    def routes(self) -> Any:
        return self.hedron.routes

    @property
    def native(self) -> hedron.Hedron:
        """The exact native app (kept as a property for 0.1 compatibility)."""
        return self.hedron

    def native_surface(self, surface: Any) -> Any:
        """Resolve a registered Edron surface to its exact native projection."""
        return self._native_surface(surface)

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        """Expose the facade as an ordinary ASGI application."""
        await self.hedron(scope, receive, send)

    def _ensure_open(self) -> None:
        if self._sealed:
            raise RegistrationError("the Edron app is sealed", code="EDRON_APP_SEALED")

    @staticmethod
    def _unwrap_annotations(annotation: Any) -> Any:
        if get_origin(annotation) is Annotated:
            return get_args(annotation)[0]
        return annotation

    @staticmethod
    def _dependency_signature(
        signature: inspect.Signature, dependencies: Sequence[Any]
    ) -> inspect.Signature:
        params = list(signature.parameters.values())
        params.extend(
            inspect.Parameter(
                f"__edron_dep_{index}",
                inspect.Parameter.KEYWORD_ONLY,
                annotation=Any,
                default=dependency.native() if isinstance(dependency, Dependency) else dependency,
            )
            for index, dependency in enumerate(dependencies)
        )
        return signature.replace(parameters=params)

    @staticmethod
    def _without_self(signature: inspect.Signature) -> inspect.Signature:
        params = list(signature.parameters.values())
        if params and params[0].name == "self":
            params.pop(0)
        return signature.replace(parameters=params)

    def _page_dependencies(self, page_type: type[Page]) -> list[Dependency[Any]]:
        return [value for value in page_type.__dict__.values() if isinstance(value, Dependency)]

    def _instantiate(self, page_type: type[Page], dependency_values: Mapping[str, Any]) -> Page:
        try:
            instance = page_type()
        except TypeError as exc:
            raise RegistrationError(
                f"{page_type.__name__} must have a no-argument constructor", code="EDRON_PAGE_INIT"
            ) from exc
        for name, value in dependency_values.items():
            setattr(instance, name, value)
        return instance

    @staticmethod
    def _dependency_values(page_type: type[Page], kwargs: dict[str, Any]) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for index, dependency in enumerate(
            value for value in page_type.__dict__.values() if isinstance(value, Dependency)
        ):
            key = f"__edron_dep_{index}"
            if key in kwargs:
                values[dependency.name or key] = kwargs.pop(key)
        return values

    @staticmethod
    def _call_with_kwargs(fn: Callable[..., Any], instance: Page, kwargs: dict[str, Any]) -> Any:
        signature = inspect.signature(fn)
        names = set(signature.parameters) - {"self"}
        return fn(instance, **{key: value for key, value in kwargs.items() if key in names})

    def page(
        self,
        path: str,
        *,
        title: str,
        name: str | None = None,
        show_title: bool = True,
        dependencies: Sequence[Any] = (),
    ) -> Callable[[type[Page]], type[Page]]:
        self._ensure_open()
        if not path.startswith("/"):
            raise RegistrationError("page paths must begin with /", code="EDRON_PAGE_PATH")

        def register(page_type: type[Page]) -> type[Page]:
            self._register_page(
                page_type, path, title, name=name, show_title=show_title, dependencies=dependencies
            )
            return page_type

        return register

    def function_page(
        self,
        path: str,
        *,
        title: str,
        name: str | None = None,
        show_title: bool = True,
        dependencies: Sequence[Any] = (),
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a function as a page with the same fresh-instance semantics.

        This is intentionally explicit and limited to a single render function.  A
        function page cannot grow inherited fragments/actions, which keeps the class
        facade as the composition path for related surfaces.
        """
        self._ensure_open()
        if not path.startswith("/"):
            raise RegistrationError("page paths must begin with /", code="EDRON_PAGE_PATH")

        def register(render_fn: Callable[..., Any]) -> Callable[..., Any]:
            if not callable(render_fn) or inspect.isclass(render_fn):
                raise RegistrationError(
                    "@app.function_page must decorate a function", code="EDRON_PAGE_TYPE"
                )
            signature = inspect.signature(render_fn)
            if any(
                parameter.name in {"self", "page"} for parameter in signature.parameters.values()
            ):
                raise RegistrationError(
                    "function pages receive only declared request parameters",
                    code="EDRON_PAGE_INIT",
                )
            page_name = name or render_fn.__name__
            self_parameter = inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)
            wrapped_signature = signature.replace(
                parameters=[self_parameter, *signature.parameters.values()]
            )
            if inspect.iscoroutinefunction(render_fn):

                async def async_page_render(instance: Page, **kwargs: Any) -> Any:
                    return await render_fn(**kwargs)

                page_render = async_page_render
            else:

                def sync_page_render(instance: Page, **kwargs: Any) -> Any:
                    return render_fn(**kwargs)

                page_render = sync_page_render

            page_render.__name__ = render_fn.__name__
            page_render.__module__ = render_fn.__module__
            page_render.__qualname__ = render_fn.__qualname__
            page_render.__signature__ = wrapped_signature  # type: ignore[attr-defined]
            page_type = type(
                f"{render_fn.__name__.title().replace('_', '')}Page",
                (Page,),
                {"__module__": render_fn.__module__, "render": page_render},
            )
            self._register_page(
                page_type,
                path,
                title,
                name=page_name,
                show_title=show_title,
                dependencies=dependencies,
            )
            self._function_pages[id(render_fn)] = page_type
            self._pages[path]["function"] = render_fn
            self._pages[path]["source"] = source_location(render_fn)
            return render_fn

        return register

    def page_function(self, *args: Any, **kwargs: Any) -> Any:
        """Alias for :meth:`function_page` with the noun-first spelling."""
        return self.function_page(*args, **kwargs)

    def _register_page(
        self,
        page_type: type[Page],
        path: str,
        title: str,
        *,
        name: str | None,
        show_title: bool,
        dependencies: Sequence[Any],
    ) -> None:
        self._ensure_open()
        if not inspect.isclass(page_type) or not issubclass(page_type, Page) or page_type is Page:
            raise RegistrationError(
                "@app.page must decorate a Page subclass",
                code="EDRON_PAGE_TYPE",
                source=source_location(page_type),
            )
        if path in self._pages:
            raise RegistrationError(
                f"page path {path!r} is already registered", code="EDRON_DUPLICATE_PATH"
            )
        if "__init__" in page_type.__dict__:
            raise RegistrationError(
                "Page classes must not define __init__",
                code="EDRON_PAGE_INIT",
                source=source_location(page_type),
            )
        render = page_type.__dict__.get("render")
        if render is None or not callable(render):
            raise RegistrationError(
                f"{page_type.__name__} must define render()",
                code="EDRON_RENDER_MISSING",
                source=source_location(page_type),
            )

        page_dependencies = [
            *self._page_dependencies(page_type),
            *[item for item in dependencies if isinstance(item, Dependency)],
        ]
        page_route_dependencies = list(dependencies)
        render_signature = self._dependency_signature(
            self._without_self(inspect.signature(render)), page_dependencies
        )
        route_name = name or page_type.__name__.lower()

        def endpoint(**kwargs: Any) -> Any:
            dependency_values = self._dependency_values(page_type, kwargs)
            request = self._request()
            frame = Frame(self, None, "page", request=request)
            with frame_context(frame):
                instance = self._instantiate(page_type, dependency_values)
                frame.page = instance
                result = self._call_with_kwargs(render, instance, kwargs)
                if inspect.isawaitable(result):
                    raise RuntimeError("async render requires the async route adapter")
                if result is not None:
                    instance.include(result)
                return hedron_core_page(
                    *instance._resolved_output(), title=title if show_title else None
                )

        endpoint.__name__ = f"edron_{route_name}"
        endpoint.__module__ = page_type.__module__
        endpoint.__signature__ = render_signature  # type: ignore[attr-defined]
        if inspect.iscoroutinefunction(render):

            async def async_endpoint(**kwargs: Any) -> Any:
                dependency_values = self._dependency_values(page_type, kwargs)
                frame = Frame(self, None, "page", request=self._request())
                with frame_context(frame):
                    instance = self._instantiate(page_type, dependency_values)
                    frame.page = instance
                    result = await self._call_with_kwargs(render, instance, kwargs)
                    if result is not None:
                        instance.include(result)
                    return hedron_core_page(
                        *instance._resolved_output(), title=title if show_title else None
                    )

            async_endpoint.__name__ = endpoint.__name__
            async_endpoint.__module__ = endpoint.__module__
            async_endpoint.__signature__ = render_signature  # type: ignore[attr-defined]
            endpoint = async_endpoint
        native_page = self.hedron.page(
            path,
            name=route_name,
            dependencies=[self._native_dependency(x) for x in page_route_dependencies],
        )(endpoint)

        page_record = {
            "type": page_type,
            "path": path,
            "title": title,
            "name": route_name,
            "show_title": show_title,
            "source": source_location(page_type) or source_location(render),
            "native": native_page,
        }
        self._pages[path] = page_record
        for member_name, member in page_type.__dict__.items():
            if isinstance(member, Fragment):
                self._register_fragment(
                    member,
                    page_type,
                    path,
                    member_name,
                    callable_dependencies=[
                        *page_dependencies,
                        *[item for item in member.dependencies if isinstance(item, Dependency)],
                    ],
                    route_dependencies=[*page_route_dependencies, *member.dependencies],
                )
            elif isinstance(member, Action):
                self._register_action(
                    member,
                    page_type,
                    path,
                    member_name,
                    callable_dependencies=[
                        *page_dependencies,
                        *[item for item in member.dependencies if isinstance(item, Dependency)],
                    ],
                    route_dependencies=[*page_route_dependencies, *member.dependencies],
                )

    @staticmethod
    def _native_dependency(value: Any) -> Any:
        return value.native() if isinstance(value, Dependency) else value

    def _register_fragment(
        self,
        definition: Fragment[Any],
        page_type: type[Page],
        page_path: str,
        member_name: str,
        *,
        callable_dependencies: Sequence[Any],
        route_dependencies: Sequence[Any],
    ) -> None:
        route = definition.path or f"{page_path.rstrip('/')}/__edron/{member_name}"
        fn_signature = self._without_self(inspect.signature(definition.fn))
        signature = self._dependency_signature(fn_signature, callable_dependencies)

        def endpoint(**kwargs: Any) -> Any:
            dependency_values = self._dependency_values(page_type, kwargs)
            frame = Frame(self, None, "fragment", request=self._request())
            with frame_context(frame):
                instance = self._instantiate(page_type, dependency_values)
                frame.page = instance
                result = self._call_with_kwargs(definition.fn, instance, kwargs)
                if inspect.isawaitable(result):
                    raise RuntimeError("async fragments require the async route adapter")
                if result is not None:
                    instance.include(result)
                return hedron_core_fragment(*instance._resolved_output())

        endpoint.__name__ = f"edron_fragment_{page_type.__name__}_{member_name}"
        endpoint.__module__ = page_type.__module__
        endpoint.__signature__ = signature  # type: ignore[attr-defined]
        if inspect.iscoroutinefunction(definition.fn):

            async def async_endpoint(**kwargs: Any) -> Any:
                dependency_values = self._dependency_values(page_type, kwargs)
                frame = Frame(self, None, "fragment", request=self._request())
                with frame_context(frame):
                    instance = self._instantiate(page_type, dependency_values)
                    frame.page = instance
                    result = await self._call_with_kwargs(definition.fn, instance, kwargs)
                    if result is not None:
                        instance.include(result)
                    return hedron_core_fragment(*instance._resolved_output())

            async_endpoint.__name__ = endpoint.__name__
            async_endpoint.__module__ = endpoint.__module__
            async_endpoint.__signature__ = signature  # type: ignore[attr-defined]
            endpoint = async_endpoint
        native = self.hedron.refreshable(
            route,
            name=f"{page_type.__name__}_{member_name}",
            fallback=definition.fallback,
            dependencies=[self._native_dependency(x) for x in route_dependencies],
        )(endpoint)
        definition._native = native
        self._fragments[id(definition)] = native

    def _register_action(
        self,
        definition: Action[Any, Any],
        page_type: type[Page],
        page_path: str,
        member_name: str,
        *,
        callable_dependencies: Sequence[Any],
        route_dependencies: Sequence[Any],
    ) -> None:
        route = definition.path or f"{page_path.rstrip('/')}/__edron/{member_name}"
        signature = self._without_self(inspect.signature(definition.fn))
        parameters = list(signature.parameters.values())
        for index, parameter in enumerate(parameters):
            annotation = self._unwrap_annotations(parameter.annotation)
            if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                from hedron.type_authoring import FormBody

                parameters[index] = parameter.replace(annotation=Annotated[annotation, FormBody()])
                break
        signature = self._dependency_signature(
            signature.replace(parameters=parameters), callable_dependencies
        )

        def endpoint(**kwargs: Any) -> Any:
            dependency_values = self._dependency_values(page_type, kwargs)
            frame = Frame(self, None, "action", request=self._request())
            with frame_context(frame):
                instance = self._instantiate(page_type, dependency_values)
                frame.page = instance
                return self._call_with_kwargs(definition.fn, instance, kwargs)

        endpoint.__name__ = f"edron_action_{page_type.__name__}_{member_name}"
        endpoint.__module__ = page_type.__module__
        endpoint.__signature__ = signature  # type: ignore[attr-defined]
        if inspect.iscoroutinefunction(definition.fn):

            async def async_endpoint(**kwargs: Any) -> Any:
                dependency_values = self._dependency_values(page_type, kwargs)
                frame = Frame(self, None, "action", request=self._request())
                with frame_context(frame):
                    instance = self._instantiate(page_type, dependency_values)
                    frame.page = instance
                    return await self._call_with_kwargs(definition.fn, instance, kwargs)

            async_endpoint.__name__ = endpoint.__name__
            async_endpoint.__module__ = endpoint.__module__
            async_endpoint.__signature__ = signature  # type: ignore[attr-defined]
            endpoint = async_endpoint
        native = self.hedron.command(
            route,
            method=definition.method.upper(),
            name=f"{page_type.__name__}_{member_name}",
            fallback=definition.fallback,
            dependencies=[self._native_dependency(x) for x in route_dependencies],
        )(endpoint)
        definition._native = native
        self._actions[id(definition)] = native

    def _request(self) -> Any:
        try:
            from hedron.routing.router import current_request

            return current_request.get()
        except (ImportError, LookupError):
            return None

    def _mount_fragment(self, definition: Fragment[Any], arguments: Mapping[str, Any]) -> None:
        native = self._fragments.get(id(definition))
        if native is None:
            raise BindingError("fragment is not registered on this app", code="EDRON_FRAGMENT_APP")
        try:
            node = native.bind(**dict(arguments))() if arguments else native()
        except Exception as exc:
            raise BindingError(
                f"could not bind fragment {definition.name}", code="EDRON_FRAGMENT_BIND"
            ) from exc
        from edron._internal import require_frame

        require_frame("page", "fragment").buffer.append(node)

    def _native_surface(self, surface: Any) -> Any:
        """Resolve an Edron definition to the exact object registered in Hedron."""
        for record in self._data_workspaces.values():
            if record["workspace"] is surface:
                return record["native"]
        if isinstance(surface, BoundFragment):
            native = self._fragments.get(id(surface.fragment))
            return (
                native.bind(**surface.arguments)
                if native is not None and surface.arguments
                else native
            )
        if isinstance(surface, Fragment):
            return self._fragments.get(id(surface))
        if isinstance(surface, BoundAction):
            native = self._actions.get(id(surface.action))
            return self._bind_action(native, surface.arguments) if native is not None else None
        if isinstance(surface, Action):
            return self._actions.get(id(surface))
        if isinstance(surface, type) and issubclass(surface, Page):
            for record in self._pages.values():
                if record["type"] is surface:
                    return record.get("native")
        candidate: Any = surface
        if hasattr(candidate, "to_bundle"):
            if id(candidate) in self._bundles:
                return self._bundles[id(candidate)]
            return candidate.to_bundle()
        return None

    def source_map(self) -> dict[str, Any]:
        """Return a bounded, redacted map from Edron sources to native projections."""
        entries: list[dict[str, Any]] = []
        truncated = False
        for record in self._pages.values():
            if len(entries) >= MAX_SOURCE_MAP_ENTRIES:
                truncated = True
                break
            page_source = record.get("source")
            entries.append(
                {
                    "kind": "page",
                    "name": record["name"],
                    "path": record["path"],
                    "source": page_source.to_mapping() if page_source is not None else None,
                }
            )
            page_type = record["type"]
            for _member_name, member in page_type.__dict__.items():
                if not isinstance(member, (Fragment, Action)):
                    continue
                if len(entries) >= MAX_SOURCE_MAP_ENTRIES:
                    truncated = True
                    break
                native = member._native
                source = member._source
                entries.append(
                    {
                        "kind": "fragment" if isinstance(member, Fragment) else "action",
                        "name": member.logical_id,
                        "path": getattr(native, "path", None),
                        "native_id": getattr(native, "logical_id", None),
                        "source": source.to_mapping() if source is not None else None,
                        **(
                            {"inherited_from": member._inherited_from}
                            if member._inherited_from
                            else {}
                        ),
                    }
                )
        return {"schema": "edron.source-map/1", "entries": entries, "truncated": truncated}

    def explain(self) -> dict[str, Any]:
        """Explain registered Edron surfaces without executing application callbacks."""
        pages: list[dict[str, Any]] = []
        truncated = False
        for record in self._pages.values():
            if len(pages) >= MAX_EXPLANATION_PAGES:
                truncated = True
                break
            page_type = record["type"]
            surfaces = []
            for member_name, member in page_type.__dict__.items():
                if isinstance(member, Fragment):
                    native = member._native
                    surfaces.append(
                        {
                            "name": member_name,
                            "kind": "fragment",
                            "logical_id": member.logical_id,
                            "method": "GET",
                            "path": getattr(native, "path", None),
                            "source": member._source.to_mapping() if member._source else None,
                        }
                    )
                elif isinstance(member, Action):
                    native = member._native
                    surfaces.append(
                        {
                            "name": member_name,
                            "kind": "action",
                            "logical_id": member.logical_id,
                            "method": member.method.upper(),
                            "path": getattr(native, "path", None),
                            "source": member._source.to_mapping() if member._source else None,
                        }
                    )
            if len(surfaces) > MAX_EXPLANATION_SURFACES:
                surfaces = surfaces[:MAX_EXPLANATION_SURFACES]
                truncated = True
            source = record.get("source")
            pages.append(
                {
                    "name": record["name"],
                    "path": record["path"],
                    "title": record["title"],
                    "class": f"{page_type.__module__}.{page_type.__qualname__}",
                    "source": source.to_mapping() if source else None,
                    "surfaces": surfaces,
                }
            )
        return {
            "schema": "edron.application-explanation/1",
            "title": self.title,
            "pages": pages,
            "data_workspaces": [
                {"save_path": path, **dict(record["workspace"].diagnostics())}
                for path, record in self._data_workspaces.items()
            ],
            "source_map": self.source_map(),
            "native_authority": "hedron",
            "callbacks_executed": False,
            "truncated": truncated,
        }

    def check(self) -> Any:
        """Return a diagnostic report for registered metadata only."""
        from edron.tooling import check_application

        return check_application(self)

    def _resolve_action(self, value: Any) -> Any:
        if isinstance(value, BoundAction):
            native = self._actions.get(id(value.action))
            if native is None:
                return None
            return self._bind_action(native, value.arguments)
        if isinstance(value, Action):
            return self._actions.get(id(value))
        return value

    @staticmethod
    def _bind_action(native: Any, arguments: Mapping[str, Any]) -> Any:
        if not arguments:
            return native
        parts = urlsplit(str(native.path))
        path = parts.path
        query: dict[str, Any] = dict()
        for name, value in arguments.items():
            marker = re.compile(r"\{" + re.escape(name) + r"(?::[^}]+)?\}")
            if marker.search(path):
                path = marker.sub(quote(str(value), safe=""), path)
            else:
                query[name] = value
        encoded = urlencode(query, doseq=True)
        combined_query = "&".join(item for item in (parts.query, encoded) if item)
        return replace(
            native,
            path=urlunsplit((parts.scheme, parts.netloc, path, combined_query, parts.fragment)),
        )

    def _action_button(self, label: str, action: Any, **kwargs: Any) -> Any:
        native = self._resolve_action(action)
        if native is None or not hasattr(native, "button"):
            raise BindingError(
                "button requires a registered Edron action", code="EDRON_ACTION_BIND"
            )
        confirm = kwargs.pop("confirm", None)
        if confirm is not None:
            kwargs["hx-confirm"] = getattr(confirm, "message", confirm)
        variant = kwargs.pop("variant", None)
        size = kwargs.pop("size", None)
        width = kwargs.pop("width", None)
        classes = ["edron-action-button"]
        if variant:
            classes.append(f"edron-action-button--{variant}")
        if size:
            classes.append(f"edron-action-button--{size}")
        if width:
            classes.append(f"edron-action-button--{width}")
        kwargs["class_"] = " ".join(classes)
        return native.button(
            label, **{key: value for key, value in kwargs.items() if value is not None}
        )

    def _action_form(self, action: Any, *, model: Any = None, **kwargs: Any) -> Any:
        native = self._resolve_action(action)
        if native is None or not hasattr(native, "form"):
            raise BindingError("form requires a registered Edron action", code="EDRON_ACTION_BIND")
        if model is not None and getattr(native, "input_model", None) is None:
            raise BindingError(
                "the action does not have a typed form body", code="EDRON_FORM_MODEL"
            )
        return native.form(**kwargs)

    def include(self, feature: Any) -> Any:
        bundle = self.hedron.include_feature(feature)
        self._bundles[id(feature)] = bundle
        return bundle

    def data_workspace(
        self,
        workspace: Any,
        *,
        save_path: str | None = None,
        dependencies: Sequence[Any] = (),
    ) -> Any:
        """Register an explicit native mutation route for an Edron workspace."""
        from starlette.exceptions import HTTPException
        from starlette.requests import Request
        from starlette.responses import JSONResponse

        from edron.data import DataWorkspace, EditIntent

        self._ensure_open()
        if not isinstance(workspace, DataWorkspace):
            raise TypeError("data_workspace expects edron.DataWorkspace")
        if workspace.edit_policy is None:
            raise RegistrationError(
                "cannot register a save route for a read-only workspace",
                code="EDRON_DATA_READ_ONLY",
            )
        path = save_path or f"/__edron/data/{workspace.name}/save"
        if not path.startswith("/"):
            raise RegistrationError(
                "workspace save paths must begin with /", code="EDRON_PAGE_PATH"
            )
        if path in self._data_workspaces:
            raise RegistrationError(
                f"workspace save path {path!r} is already registered",
                code="EDRON_DUPLICATE_PATH",
            )

        async def save(request: Request) -> JSONResponse:
            try:
                payload = await request.json()
                if not isinstance(payload, Mapping):
                    raise ValueError("editor payload must be an object")
                intent = EditIntent.from_mapping(payload)
            except (TypeError, ValueError) as exc:
                raise HTTPException(status_code=422, detail="invalid_data_edit") from exc
            result = workspace.apply(
                intent,
                principal=workspace.principal_from_request(request),
            )
            body = {
                "ok": result.ok,
                "version": result.version,
                "errors": [
                    {"row_key": item.row_key, "field": item.field, "message": item.message}
                    for item in result.errors
                ],
                "conflicts": [
                    {"row_key": item.row_key, "field": item.field, "message": item.message}
                    for item in result.conflicts
                ],
            }
            status = 409 if result.conflicts else 422 if not result.ok else 200
            return JSONResponse(body, status_code=status)

        save.__name__ = f"edron_data_{workspace.name}_save"
        save.__annotations__ = {"request": Request, "return": JSONResponse}
        native = self.hedron.action(
            path,
            name=f"edron-data-{workspace.name}-save",
            dependencies=[self._native_dependency(item) for item in dependencies],
        )(save)
        workspace.save_endpoint = path
        self._data_workspaces[path] = {"workspace": workspace, "native": native}
        return workspace

    def styles(self, name: str, source: str | Path, **kwargs: Any) -> Any:
        return self.hedron.styles(name, source, **kwargs)

    def seal(self) -> None:
        self._sealed = True


def hedron_core_page(*nodes: Any, title: str | None = None) -> Any:
    from hedron_core.builtins.document import Page as NativePage

    return NativePage(*nodes, title=title)


def hedron_core_fragment(*nodes: Any) -> Any:
    from hedron_core.builtins.document import Fragment as NativeFragment

    return NativeFragment(*nodes)
