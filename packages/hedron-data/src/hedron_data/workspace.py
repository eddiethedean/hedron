"""Opt-in DataWorkspace compiling to ordinary handles and a FeatureBundle."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, create_model

from hedron_core.bundles import (
    MAX_WORKSPACE_FIELDS,
    FeatureBundle,
    FeatureConflictError,
    FeatureRequirement,
)
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.codes import HED_BUNDLE_0005, HED_BUNDLE_0007
from hedron_core.diagnostics import DiagnosticSeverity, make_diagnostic
from hedron_data.sources import (
    CellUpdate,
    DataChanges,
    DataEditorSource,
    DataQuery,
)
from hedron_data.table import DataTable

ModelT = TypeVar("ModelT", bound=BaseModel)
AuthzHook = Callable[..., bool]

__all__ = ["DataWorkspace", "DataWorkspacePolicy"]


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
        source: DataEditorSource[Any],
        policy: DataWorkspacePolicy,
        create_model: type[BaseModel] | None = None,
        edit_model: type[BaseModel] | None = None,
        key_field: str = "id",
        provider: str = "hedron-data",
        provider_version: str = "0.47.0",
        columns: Sequence[object] = (),
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
        self.list_view: object | None = None
        self.detail_view: object | None = None
        self.create_command: object | None = None
        self.edit_command: object | None = None

    def _allowed(self, hook: AuthzHook | None, **kwargs: object) -> bool:
        if hook is None:
            return False
        try:
            return bool(hook(**kwargs) if kwargs else hook())
        except TypeError:
            return bool(hook())

    def _identity_model(self) -> type[BaseModel]:
        return create_model(
            f"{self.name.title()}Identity",
            **{self.key_field: (str, ...)},  # type: ignore[arg-type]
        )

    def to_bundle(self) -> FeatureBundle:
        workspace = self

        def list_factory(app: object) -> object:

            from starlette.exceptions import HTTPException

            if workspace.list_override is not None:
                handle = app.refreshable(f"/{workspace.name}", name=f"{workspace.name}-list")(  # type: ignore[union-attr]
                    workspace.list_override
                )
                workspace.list_view = handle
                return handle

            @app.refreshable(f"/{workspace.name}", name=f"{workspace.name}-list")  # type: ignore[union-attr]
            def list_view() -> object:
                if not workspace._allowed(workspace.policy.can_read):
                    raise HTTPException(status_code=403, detail="forbidden")
                page = workspace.source.fetch(DataQuery(limit=25))
                return DataTable(page=page, caption=workspace.name)

            workspace.list_view = list_view
            return list_view

        def detail_factory(app: object) -> object:
            from typing import Annotated

            from starlette.exceptions import HTTPException

            from hedron import ViewParams

            identity = workspace._identity_model()
            if workspace.detail_override is not None:
                handle = app.refreshable(  # type: ignore[union-attr]
                    f"/{workspace.name}/{{{workspace.key_field}}}",
                    name=f"{workspace.name}-detail",
                )(workspace.detail_override)
                workspace.detail_view = handle
                return handle

            @app.refreshable(  # type: ignore[union-attr]
                f"/{workspace.name}/{{{workspace.key_field}}}",
                name=f"{workspace.name}-detail",
            )
            def detail_view(params: Annotated[identity, ViewParams()]):  # type: ignore[valid-type]
                if not workspace._allowed(workspace.policy.can_read):
                    raise HTTPException(status_code=403, detail="forbidden")
                key = str(getattr(params, workspace.key_field))
                page = workspace.source.fetch(
                    DataQuery(filters={workspace.key_field: key}, limit=1)
                )
                if not page.rows:
                    raise HTTPException(status_code=404, detail="not_found")
                row = page.rows[0]
                from hedron import Text

                return Text(str(row.get(workspace.key_field, key)))

            workspace.detail_view = detail_view
            return detail_view

        def create_factory(app: object) -> object:
            from typing import Annotated

            from starlette.exceptions import HTTPException

            from hedron import FormBody, Text, refresh

            if workspace.create_override is not None:
                handle = app.command(  # type: ignore[union-attr]
                    f"/{workspace.name}/create",
                    name=f"{workspace.name}-create",
                    fallback=f"/{workspace.name}",
                )(workspace.create_override)
                workspace.create_command = handle
                return handle

            @app.command(  # type: ignore[union-attr]
                f"/{workspace.name}/create",
                name=f"{workspace.name}-create",
                fallback=f"/{workspace.name}",
            )
            def create_command(data: Annotated[workspace.create_model, FormBody()]):  # type: ignore[valid-type]
                if not workspace._allowed(workspace.policy.can_create):
                    raise HTTPException(status_code=403, detail="forbidden")
                payload = data.model_dump() if hasattr(data, "model_dump") else dict(data)
                result = workspace.source.apply(DataChanges(inserts=(payload,)))
                if result.conflicts:
                    raise HTTPException(status_code=409, detail="conflict")
                if not result.ok:
                    raise HTTPException(status_code=422, detail="validation")
                if workspace.list_view is not None:
                    return refresh(workspace.list_view)  # type: ignore[arg-type]
                return Text("created")

            workspace.create_command = create_command
            return create_command

        def edit_factory(app: object) -> object:
            from typing import Annotated

            from starlette.exceptions import HTTPException

            from hedron import FormBody, Text, refresh

            if workspace.edit_override is not None:
                handle = app.command(  # type: ignore[union-attr]
                    f"/{workspace.name}/edit",
                    name=f"{workspace.name}-edit",
                    fallback=f"/{workspace.name}",
                )(workspace.edit_override)
                workspace.edit_command = handle
                return handle

            class EditPayload(workspace.edit_model):  # type: ignore[valid-type,misc]
                pass

            if workspace.key_field not in getattr(workspace.edit_model, "model_fields", {}):
                EditModel = create_model(
                    f"{workspace.name.title()}Edit",
                    __base__=workspace.edit_model,
                    **{workspace.key_field: (str, ...)},  # type: ignore[arg-type]
                )
            else:
                EditModel = workspace.edit_model

            @app.command(  # type: ignore[union-attr]
                f"/{workspace.name}/edit",
                name=f"{workspace.name}-edit",
                fallback=f"/{workspace.name}",
            )
            def edit_command(data: Annotated[EditModel, FormBody()]):  # type: ignore[valid-type]
                if not workspace._allowed(workspace.policy.can_edit):
                    raise HTTPException(status_code=403, detail="forbidden")
                payload = data.model_dump() if hasattr(data, "model_dump") else dict(data)
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
                    return refresh(workspace.list_view)  # type: ignore[arg-type]
                return Text("updated")

            workspace.edit_command = edit_command
            return edit_command

        projection = PackageProjection(
            namespace=f"hedron.data.workspace.{self.name}",
            provider=self.provider,
            provider_version=self.provider_version,
            capabilities=(ProjectionCapability(name="DataWorkspace", support="supported"),),
            data={
                "name": self.name,
                "model_name": self.model.__name__,
                "surfaces": ["list", "detail", "create", "edit"],
                "delete": "disabled" if self.policy.delete == "disabled" else "explicit",
                "optimism": self.policy.optimism,
                "direct_apis": True,
                "catalog_required": False,
                "exposure": False,
            },
            limitations=("opt-in; no inferred authz; delete disabled unless supplied",),
        )
        return FeatureBundle(
            logical_id=f"{self.provider}:{self.name}",
            provider=self.provider,
            provider_version=self.provider_version,
            views=(list_factory, detail_factory),
            commands=(create_factory, edit_factory),
            projections=(projection,),
            requirements=(FeatureRequirement(name="hedron-data", required=True),),
        )
