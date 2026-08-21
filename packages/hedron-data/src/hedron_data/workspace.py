"""Opt-in DataWorkspace compiling to ordinary handles and a FeatureBundle."""

from __future__ import annotations

import contextlib
import inspect
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, Literal, Protocol, Self, TypeVar, cast

from pydantic import BaseModel, Field, TypeAdapter, create_model

from hedron_core.bundles import (
    MAX_WORKSPACE_FIELDS,
    FeatureBundle,
    FeatureConflictError,
    FeatureRequirement,
)
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.codes import HED_BUNDLE_0005, HED_BUNDLE_0007
from hedron_core.diagnostics import DiagnosticSeverity, make_diagnostic
from hedron_core.models import Model
from hedron_core.typing_aliases import JsonValue
from hedron_data.columns import Column
from hedron_data.sources import (
    HARD_MAX_PAGE_SIZE,
    CellUpdate,
    DataChanges,
    DataEditorSource,
    DataQuery,
)
from hedron_data.table import DataTable

if TYPE_CHECKING:
    from hedron.handles import ActionHandle, FragmentHandle

ModelT = TypeVar("ModelT", bound=BaseModel)
AuthzHook = Callable[..., bool]
_LIST_RESERVED = frozenset({"offset", "limit", "sort", "q"})
RowMapping = dict[str, JsonValue]

__all__ = ["DataWorkspace", "DataWorkspacePolicy", "FeatureOverrides"]

ScreenLayout = Literal["stack", "grid", "plain"]


@dataclass(frozen=True, slots=True)
class FeatureOverrides:
    """Additive named-surface overrides for DataWorkspace screen composition."""

    list_override: Callable[..., object] | None = None
    detail_override: Callable[..., object] | None = None
    create_override: Callable[..., object] | None = None
    edit_override: Callable[..., object] | None = None
    form_overrides: Mapping[str, object] | None = None


class _WorkspaceApp(Protocol):
    """Minimal host surface used by workspace factories (Hedron.refreshable/command)."""

    def refreshable(
        self,
        path: str,
        *,
        name: str | None = None,
    ) -> Callable[[Callable[..., object]], FragmentHandle[Any, Any]]: ...

    def command(
        self,
        path: str,
        *,
        name: str | None = None,
        fallback: str | None = None,
    ) -> Callable[[Callable[..., object]], ActionHandle[Any, Any]]: ...

    def screen(
        self,
        path: str,
        *,
        title: str,
        name: str | None = None,
        layout: str = "stack",
    ) -> Callable[[Callable[..., object]], object]: ...

    def page(
        self,
        path: str,
        *,
        name: str | None = None,
    ) -> Callable[[Callable[..., object]], object]: ...


def _error(code: str, title: str, explanation: str, remediation: str) -> FeatureConflictError:
    return FeatureConflictError(
        make_diagnostic(
            code,
            severity=DiagnosticSeverity.ERROR,
            title=title,
            explanation=explanation,
            remediation=remediation,
        )
    )


def _payload_mapping(data: object) -> RowMapping:
    dumped = getattr(data, "model_dump", None)
    if callable(dumped):
        return cast(RowMapping, dumped())
    return cast(RowMapping, dict(cast(Mapping[str, object], data)))


@dataclass(frozen=True, slots=True)
class DataWorkspacePolicy:
    """Explicit read/create/edit/delete/auth/optimism; mutation defaults deny."""

    can_read: AuthzHook | None = None
    can_create: AuthzHook | None = None
    can_edit: AuthzHook | None = None
    delete: Literal["disabled"] | AuthzHook = "disabled"
    optimism: Literal["server_confirmed", "collection_edit"] = "server_confirmed"


class DataWorkspace(Generic[ModelT]):
    """Opt-in typed list/detail/create/edit feature over an authorized source."""

    def __init__(
        self,
        name: str,
        *,
        model: type[ModelT],
        source: DataEditorSource[RowMapping],
        policy: DataWorkspacePolicy,
        create_model: type[BaseModel] | None = None,
        edit_model: type[BaseModel] | None = None,
        key_field: str = "id",
        provider: str = "hedron-data",
        provider_version: str = "0.47.0",
        columns: Sequence[Column | str] = (),
        form_overrides: Mapping[str, object] | None = None,
        list_override: Callable[..., object] | None = None,
        detail_override: Callable[..., object] | None = None,
        create_override: Callable[..., object] | None = None,
        edit_override: Callable[..., object] | None = None,
    ) -> None:
        fields = getattr(model, "model_fields", {}) or {}
        if len(fields) > MAX_WORKSPACE_FIELDS:
            raise _error(
                HED_BUNDLE_0005,
                "Workspace field bound exceeded",
                f"Model {model.__name__} has {len(fields)} fields; max is {MAX_WORKSPACE_FIELDS}.",
                "Split the model or drop unused fields.",
            )
        if not callable(getattr(source, "fetch", None)) or not callable(
            getattr(source, "apply", None)
        ):
            raise _error(
                HED_BUNDLE_0007,
                "DataWorkspace requires an explicit DataEditorSource",
                "A workspace never discovers ORM managers or ambient sources.",
                "Pass InMemoryDataSource, DjangoQuerySetDataSource, or SQLAlchemyDataSource.",
            )
        self.name = name
        self.model = model
        self.source = source
        self.policy = policy
        self.create_model = create_model or model
        self.edit_model = edit_model or model
        self.key_field = key_field
        self.provider = provider
        self.provider_version = provider_version
        self.columns = tuple(columns)
        self.form_overrides = dict(form_overrides or {})
        self.list_override = list_override
        self.detail_override = detail_override
        self.create_override = create_override
        self.edit_override = edit_override
        self.list_view: FragmentHandle[Any, Any] | None = None
        self.detail_view: FragmentHandle[Any, Any] | None = None
        self.create_command: ActionHandle[Any, Any] | None = None
        self.edit_command: ActionHandle[Any, Any] | None = None
        self.screen: object | None = None
        self._screen_meta: dict[str, str] | None = None
        # Empty search_fields is deny-by-default on InMemoryDataSource; do not
        # rewrite it to all model fields (that would enable secret column search).

    def with_screen(
        self,
        *,
        path: str,
        title: str,
        name: str | None = None,
        layout: ScreenLayout = "stack",
        overrides: FeatureOverrides | None = None,
    ) -> Self:
        """Opt into complete page composition; metadata is used at materialization.

        Returns ``self`` after storing screen metadata. When the workspace is
        included on a FastAPI ``Hedron`` host, ``to_bundle()`` also registers a
        screen/page at ``path`` when the host exposes ``app.screen``.
        """
        if not path or not str(path).startswith("/"):
            raise _error(
                HED_BUNDLE_0007,
                "Invalid workspace screen path",
                f"path={path!r} must be an absolute local path.",
                "Pass path='/orders' (or similar).",
            )
        if not title or not str(title).strip():
            raise _error(
                HED_BUNDLE_0007,
                "Workspace screen title required",
                "title must be an explicit non-empty string.",
                "Pass title=... to with_screen.",
            )
        if layout not in {"stack", "grid", "plain"}:
            raise _error(
                HED_BUNDLE_0007,
                "Unsupported workspace screen layout",
                f"layout={layout!r} is outside the closed inventory.",
                "Use stack, grid, or plain.",
            )
        if overrides is not None:
            if overrides.list_override is not None:
                self.list_override = overrides.list_override
            if overrides.detail_override is not None:
                self.detail_override = overrides.detail_override
            if overrides.create_override is not None:
                self.create_override = overrides.create_override
            if overrides.edit_override is not None:
                self.edit_override = overrides.edit_override
            if overrides.form_overrides is not None:
                self.form_overrides = dict(overrides.form_overrides)
        self._screen_meta = {
            "path": path,
            "title": title,
            "name": name or self.name,
            "layout": layout,
        }
        return self

    def _request_kwargs(self) -> dict[str, object]:
        kwargs: dict[str, object] = {}
        try:
            from hedron.routing.router import current_request
        except ImportError:
            return kwargs
        request = current_request.get()
        kwargs["request"] = request
        if request is None:
            return kwargs
        scope = cast(object, getattr(request, "scope", None))
        # Prefer scope["user"] — Request.user asserts AuthenticationMiddleware.
        if isinstance(scope, Mapping) and "user" in scope:
            user_attr = scope.get("user")
            if user_attr is not None and user_attr not in (False, ""):
                kwargs["user"] = user_attr
                kwargs["principal"] = user_attr
        if isinstance(scope, Mapping) and "session" in scope:
            session = cast(object, request.session)
            if isinstance(session, Mapping):
                session_map = cast(Mapping[str, object], session)
                for key in ("user", "username", "principal", "sub", "user_id", "_user_id"):
                    value = session_map.get(key)
                    if value:
                        kwargs["user"] = value
                        kwargs["principal"] = value
                        break
        return kwargs

    def _allowed(self, hook: AuthzHook | None, **kwargs: object) -> bool:
        if hook is None:
            return False
        merged = {**self._request_kwargs(), **kwargs}
        try:
            signature = inspect.signature(hook)
        except (TypeError, ValueError):
            try:
                return bool(hook(**merged))
            except TypeError:
                try:
                    return bool(hook())
                except TypeError:
                    return False
        if any(
            param.kind is inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values()
        ):
            return bool(hook(**merged))
        accepted: dict[str, object] = {}
        for name, param in signature.parameters.items():
            if name in merged and param.kind in {
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            }:
                accepted[name] = merged[name]
        try:
            signature.bind(**accepted)
        except TypeError:
            return False
        return bool(hook(**accepted))

    def _column_objects(self) -> tuple[Column, ...] | None:
        if not self.columns:
            return None
        out: list[Column] = []
        for item in self.columns:
            if isinstance(item, Column):
                out.append(item)
            else:
                out.append(Column(name=str(item)))
        return tuple(out)

    def _column_names(self) -> tuple[str, ...]:
        columns = self._column_objects()
        if columns is None:
            return tuple(getattr(self.model, "model_fields", {}) or {})
        names = [item.name for item in columns]
        if self.key_field not in names:
            names.insert(0, self.key_field)
        return tuple(names)

    def _attach_form_overrides(self, handle: object) -> None:
        overrides = dict(self.form_overrides)
        original = getattr(handle, "form", None)
        if not overrides or not callable(original):
            return

        def form(*, controls: Mapping[str, object] | None = None, **kwargs: object) -> object:
            merged = {**overrides, **dict(controls or {})}
            return original(controls=merged, **kwargs)

        target = cast(Any, handle)
        target.form = form

    def _identity_model(self) -> type[BaseModel]:
        fields: dict[str, Any] = {self.key_field: (str, ...)}
        return create_model(f"{self.name.title()}Identity", **fields)

    def _list_query_model(self) -> type[BaseModel]:
        fields: dict[str, Any] = {
            "offset": (int, Field(default=0, ge=0)),
            "limit": (int, Field(default=25, ge=1, le=HARD_MAX_PAGE_SIZE)),
            "sort": (str | None, None),
            "q": (str | None, None),
        }
        for name in self._column_names():
            if name not in _LIST_RESERVED:
                fields[name] = (str | None, None)
        return create_model(f"{self.name.title()}ListQuery", **fields)

    def _data_query_from_list_params(self, params: BaseModel | None) -> DataQuery:
        from hedron_data.sources import DEFAULT_MAX_PAGE_SIZE

        model_fields = getattr(self.model, "model_fields", {}) or {}
        names = self._column_names()
        allow = frozenset(names)
        offset = int(getattr(params, "offset", 0) or 0) if params is not None else 0
        limit = int(getattr(params, "limit", 25) or 25) if params is not None else 25
        search = getattr(params, "q", None) if params is not None else None
        if search == "":
            search = None
        sort: tuple[tuple[str, str], ...] = ()
        raw_sort = getattr(params, "sort", None) if params is not None else None
        if raw_sort:
            name, _sep, direction = str(raw_sort).partition(":")
            direction = direction or "asc"
            if direction not in {"asc", "desc"} or name not in allow:
                raise ValueError("invalid_sort")
            sort = ((name, direction),)
        filters: dict[str, Any] = {}
        if params is not None:
            for name in names:
                if name in _LIST_RESERVED:
                    continue
                finfo = model_fields.get(name)
                if finfo is None:
                    continue
                raw = getattr(params, name, None)
                if raw is None or raw == "":
                    continue
                try:
                    filters[name] = TypeAdapter(finfo.annotation).validate_python(raw)
                except (TypeError, ValueError):
                    raise ValueError(f"invalid_filter:{name}") from None
        return DataQuery(
            offset=offset,
            limit=limit,
            sort=sort,
            filters=filters,
            search=str(search) if search is not None else None,
            projection=names or None,
            allowlisted_sort_fields=allow,
            allowlisted_filter_fields=allow,
            allowlisted_projection_fields=allow,
        ).validated(max_page_size=DEFAULT_MAX_PAGE_SIZE)

    def to_bundle(self) -> FeatureBundle:
        workspace = self

        def list_factory(app: _WorkspaceApp) -> FragmentHandle[Any, Any]:
            from typing import Annotated

            from starlette.exceptions import HTTPException

            from hedron import ViewParams

            if workspace.list_override is not None:
                handle = app.refreshable(f"/{workspace.name}", name=f"{workspace.name}-list")(
                    workspace.list_override
                )
                workspace.list_view = handle
                return handle

            list_query = workspace._list_query_model()
            list_defaults = list_query()

            @app.refreshable(f"/{workspace.name}", name=f"{workspace.name}-list")
            def list_view(
                # Runtime pydantic model from create_model; not a static type expression.
                params: Annotated[list_query, ViewParams(source="query")] = list_defaults,  # type: ignore[valid-type]
            ) -> object:
                if not workspace._allowed(workspace.policy.can_read):
                    raise HTTPException(status_code=403, detail="forbidden")
                try:
                    query = workspace._data_query_from_list_params(cast(BaseModel, params))
                except ValueError:
                    raise HTTPException(status_code=422, detail="invalid_query") from None
                page = workspace.source.fetch(query)
                # DataTable.row_model expects hedron Model; workspace uses BaseModel.
                return DataTable(
                    page=page,
                    caption=workspace.name,
                    columns=workspace._column_objects(),
                    row_model=cast(type[Model], workspace.model),
                )

            workspace.list_view = list_view
            return list_view

        def detail_factory(app: _WorkspaceApp) -> FragmentHandle[Any, Any]:
            from typing import Annotated

            from starlette.exceptions import HTTPException

            from hedron import ViewParams

            identity = workspace._identity_model()
            if workspace.detail_override is not None:
                handle = app.refreshable(
                    f"/{workspace.name}/{{{workspace.key_field}}}",
                    name=f"{workspace.name}-detail",
                )(workspace.detail_override)
                workspace.detail_view = handle
                return handle

            @app.refreshable(
                f"/{workspace.name}/{{{workspace.key_field}}}",
                name=f"{workspace.name}-detail",
            )
            def detail_view(
                # Runtime pydantic model from create_model; not a static type expression.
                params: Annotated[identity, ViewParams()],  # type: ignore[valid-type]
            ) -> object:
                key = str(getattr(cast(BaseModel, params), workspace.key_field))
                page = workspace.source.fetch(
                    DataQuery(filters={workspace.key_field: key}, limit=1)
                )
                if not page.rows:
                    raise HTTPException(status_code=404, detail="not_found")
                row = page.rows[0]
                if not workspace._allowed(workspace.policy.can_read, row=row):
                    raise HTTPException(status_code=403, detail="forbidden")
                from hedron import Text

                return Text(str(row.get(workspace.key_field, key)))

            workspace.detail_view = detail_view
            return detail_view

        def create_factory(app: _WorkspaceApp) -> ActionHandle[Any, Any]:
            from typing import Annotated

            from starlette.exceptions import HTTPException

            from hedron import FormBody, Text, refresh

            if workspace.create_override is not None:
                handle = app.command(
                    f"/{workspace.name}/create",
                    name=f"{workspace.name}-create",
                    fallback=f"/{workspace.name}",
                )(workspace.create_override)
                workspace.create_command = handle
                workspace._attach_form_overrides(handle)
                return handle

            @app.command(
                f"/{workspace.name}/create",
                name=f"{workspace.name}-create",
                fallback=f"/{workspace.name}",
            )
            def create_command(
                # Instance attribute holds a runtime model type for FormBody binding.
                data: Annotated[workspace.create_model, FormBody()],  # type: ignore[valid-type]
            ) -> object:
                payload = _payload_mapping(cast(object, data))
                if not workspace._allowed(workspace.policy.can_create, data=payload):
                    raise HTTPException(status_code=403, detail="forbidden")
                result = workspace.source.apply(DataChanges(inserts=(payload,)))
                if result.conflicts:
                    raise HTTPException(status_code=409, detail="conflict")
                if not result.ok:
                    raise HTTPException(status_code=422, detail="validation")
                if workspace.list_view is not None:
                    return refresh(workspace.list_view)
                return Text("created")

            workspace.create_command = create_command
            workspace._attach_form_overrides(create_command)
            return create_command

        def edit_factory(app: _WorkspaceApp) -> ActionHandle[Any, Any]:
            from typing import Annotated

            from starlette.exceptions import HTTPException

            from hedron import FormBody, Text, refresh

            if workspace.edit_override is not None:
                handle = app.command(
                    f"/{workspace.name}/edit",
                    name=f"{workspace.name}-edit",
                    fallback=f"/{workspace.name}",
                )(workspace.edit_override)
                workspace.edit_command = handle
                workspace._attach_form_overrides(handle)
                return handle

            if workspace.key_field not in getattr(workspace.edit_model, "model_fields", {}):
                edit_fields: dict[str, Any] = {workspace.key_field: (str, ...)}
                EditModel = create_model(
                    f"{workspace.name.title()}Edit",
                    __base__=workspace.edit_model,
                    **edit_fields,
                )
            else:
                EditModel = workspace.edit_model

            @app.command(
                f"/{workspace.name}/edit",
                name=f"{workspace.name}-edit",
                fallback=f"/{workspace.name}",
            )
            def edit_command(
                # EditModel is a runtime type (create_model or edit_model attribute).
                data: Annotated[EditModel, FormBody()],  # type: ignore[valid-type]
            ) -> object:
                payload = _payload_mapping(cast(object, data))
                if not workspace._allowed(workspace.policy.can_edit, data=payload, row=payload):
                    raise HTTPException(status_code=403, detail="forbidden")
                key = str(payload.get(workspace.key_field, ""))
                updates = tuple(
                    CellUpdate(row_key=key, field=field, value=value)
                    for field, value in payload.items()
                    if field != workspace.key_field
                )
                result = workspace.source.apply(DataChanges(updates=updates))
                if result.conflicts:
                    raise HTTPException(status_code=409, detail="conflict")
                if not result.ok:
                    raise HTTPException(status_code=422, detail="validation")
                if workspace.list_view is not None:
                    return refresh(workspace.list_view)
                return Text("updated")

            workspace.edit_command = edit_command
            workspace._attach_form_overrides(edit_command)
            return edit_command

        projection = PackageProjection(
            namespace=f"hedron.data.workspace.{self.name}",
            provider=self.provider,
            provider_version=self.provider_version,
            capabilities=(ProjectionCapability(name="DataWorkspace", support="supported"),),
            data={
                "name": self.name,
                "model_name": self.model.__name__,
                "surfaces": (
                    [
                        "screen",
                        "list_view",
                        "detail_view",
                        "create_command",
                        "edit_command",
                        "create_form",
                        "edit_form",
                    ]
                    if self._screen_meta is not None
                    else ["list", "detail", "create", "edit"]
                ),
                "screen": dict(self._screen_meta) if self._screen_meta is not None else None,
                "delete": "disabled" if self.policy.delete == "disabled" else "explicit",
                "optimism": self.policy.optimism,
                "direct_apis": True,
                "catalog_required": False,
                "exposure": False,
            },
            limitations=("opt-in; no inferred authz; delete disabled unless supplied",),
        )

        def screen_factory(app: _WorkspaceApp) -> object:
            meta = workspace._screen_meta
            if meta is None:
                tagged: Any = lambda: None  # noqa: E731
                tagged.logical_id = f"{workspace.name}-screen-unset"
                return tagged
            if not callable(getattr(app, "screen", None)):
                # Host without screen facade: fall back to page when available.
                if not callable(getattr(app, "page", None)):
                    tagged = lambda: None  # noqa: E731
                    tagged.logical_id = f"{workspace.name}-screen"
                    tagged.path = str(meta["path"])
                    return tagged

                @app.page(str(meta["path"]), name=str(meta["name"]))
                def screen_page() -> object:
                    from hedron import Text
                    from hedron_core.builtins.document import Page
                    from hedron_core.component import NodeLike

                    nodes: list[NodeLike] = [Text(str(meta["title"]))]
                    if workspace.list_view is not None:
                        with contextlib.suppress(Exception):
                            nodes.append(workspace.list_view())
                    return Page(*nodes, title=str(meta["title"]))

                workspace.screen = screen_page
                return screen_page

            @app.screen(
                str(meta["path"]),
                title=str(meta["title"]),
                name=str(meta["name"]),
                layout=str(meta["layout"]),  # type: ignore[arg-type]
            )
            def workspace_screen() -> object:
                from hedron import Stack, Text
                from hedron_core.component import NodeLike

                nodes: list[NodeLike] = [Text(str(meta["title"]))]
                if workspace.list_view is not None:
                    with contextlib.suppress(Exception):
                        nodes.append(workspace.list_view())
                return Stack(*nodes)

            workspace.screen = workspace_screen
            return workspace_screen

        views: tuple[object, ...]
        if self._screen_meta is not None:
            views = (screen_factory, list_factory, detail_factory)
        else:
            views = (list_factory, detail_factory)

        return FeatureBundle(
            logical_id=f"{self.provider}:{self.name}",
            provider=self.provider,
            provider_version=self.provider_version,
            views=views,
            commands=(create_factory, edit_factory),
            projections=(projection,),
            requirements=(FeatureRequirement(name="hedron-data", required=True),),
        )
