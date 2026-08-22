"""DashboardWorkspace: typed filters, loader, and render-only panels (phase 0.58)."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Generic, Literal, Protocol, TypeVar

from pydantic import BaseModel

from hedron.handles import ActionHandle, FragmentHandle
from hedron_core.bundles import FeatureBundle, FeatureRequirement
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.codes import HED_DASH_0001, HED_DASH_0002, HED_DASH_0003
from hedron_core.component import NodeLike
from hedron_core.diagnostics import error
from hedron_core.htmx.policy import CacheHint

__all__ = [
    "CachePolicy",
    "DashboardHistory",
    "DashboardWorkspace",
]

FiltersT = TypeVar("FiltersT", bound=BaseModel)
DataT = TypeVar("DataT")

DashboardHistory = Literal["replace", "push", "none"]


class _DashboardApp(Protocol):
    """Minimal Hedron host surface for dashboard materialization."""

    def screen(
        self,
        path: str,
        *,
        title: str,
        name: str | None = None,
    ) -> Callable[[Callable[..., object]], object]: ...

    def refreshable(
        self,
        path: str,
        *,
        name: str | None = None,
        cache: CacheHint | None = None,
    ) -> Callable[[Callable[..., object]], FragmentHandle[Any, Any]]: ...

    def command(
        self,
        path: str,
        *,
        name: str | None = None,
        fallback: str | None = None,
        dependencies: Sequence[object] | None = None,
        outcomes: object | None = None,
    ) -> Callable[[Callable[..., object]], ActionHandle[Any, Any]]: ...


@dataclass(frozen=True, slots=True)
class CachePolicy:
    """Explicit dashboard cache policy keyed by validated filters."""

    hint: CacheHint | None = "no-store"
    ttl_seconds: int | None = None


_SENSITIVE_FILTER_MARKERS = frozenset(
    {
        "password",
        "passwd",
        "secret",
        "token",
        "credential",
        "ssn",
        "credit_card",
        "api_key",
        "apikey",
        "access_key",
        "private_key",
    }
)


def _reject_sensitive_filters(model: type[BaseModel]) -> None:
    fields = getattr(model, "model_fields", {}) or {}
    for name, info in fields.items():
        lowered = name.lower()
        if any(marker in lowered for marker in _SENSITIVE_FILTER_MARKERS):
            raise error(
                HED_DASH_0003,
                title="Sensitive filter rejected from URL mode",
                explanation=(
                    f"Filter field {name!r} looks sensitive and cannot be a public URL param."
                ),
                remediation="Rename the field or use an explicit non-URL filter strategy.",
            )
        extra = getattr(info, "json_schema_extra", None)
        if isinstance(extra, Mapping) and extra.get("sensitive"):
            raise error(
                HED_DASH_0003,
                title="Sensitive filter rejected from URL mode",
                explanation=f"Filter field {name!r} is marked sensitive.",
                remediation="Keep sensitive filters out of DashboardWorkspace URL mode.",
            )


class DashboardWorkspace(Generic[FiltersT, DataT]):
    """Compose a screen, filter form, and named refreshable panels."""

    def __init__(
        self,
        name: str,
        path: str,
        title: str,
        filters: type[FiltersT],
        load: Callable[[FiltersT], DataT | Awaitable[DataT]],
        panels: Mapping[str, Callable[[DataT], NodeLike]],
        *,
        history: DashboardHistory = "replace",
        cache: CachePolicy | None = None,
        provider: str = "hedron",
        provider_version: str = "0.58.1",
    ) -> None:
        if not name or not str(name).strip():
            raise error(
                HED_DASH_0001,
                title="DashboardWorkspace name required",
                explanation="name must be a non-empty string.",
                remediation="Pass name=... when constructing DashboardWorkspace.",
            )
        if not path or not str(path).startswith("/"):
            raise error(
                HED_DASH_0001,
                title="DashboardWorkspace path required",
                explanation="path must be an absolute local path starting with '/'.",
                remediation="Pass path='/sales' (or similar).",
            )
        if not title or not str(title).strip():
            raise error(
                HED_DASH_0001,
                title="DashboardWorkspace title required",
                explanation="title must be an explicit non-empty string.",
                remediation="Pass title=... for the generated screen.",
            )
        if history not in {"replace", "push", "none"}:
            raise error(
                HED_DASH_0001,
                title="Invalid dashboard history mode",
                explanation=f"history={history!r} is unsupported.",
                remediation="Use 'replace', 'push', or 'none'.",
            )
        if not panels:
            raise error(
                HED_DASH_0001,
                title="DashboardWorkspace requires panels",
                explanation="At least one named panel renderer is required.",
                remediation="Pass panels={'summary': render_summary, ...}.",
            )
        if len(panels) > 16:
            raise error(
                HED_DASH_0001,
                title="Too many dashboard panels",
                explanation=f"Got {len(panels)} panels; max is 16.",
                remediation="Reduce panels or split into multiple dashboards.",
            )
        _reject_sensitive_filters(filters)
        self.name = name
        self.path = path
        self.title = title
        self.filters = filters
        self.load = load
        self.panels = dict(panels)
        self.history = history
        self.cache = cache
        self.provider = provider
        self.provider_version = provider_version
        self.screen: object | None = None
        self.filter_form: object | None = None
        self.panel_views: dict[str, FragmentHandle[Any, Any]] = {}

    async def _load_data(self, filters: FiltersT) -> DataT:
        result = self.load(filters)
        if inspect.isawaitable(result):
            return await result  # type: ignore[no-any-return]
        return result  # type: ignore[return-value]

    def to_bundle(self) -> FeatureBundle:
        workspace = self

        def screen_factory(app: _DashboardApp) -> object:
            panel_handles: dict[str, FragmentHandle[Any, Any]] = {}

            for panel_name, render in workspace.panels.items():
                panel_path = f"{workspace.path}/panels/{panel_name}"

                def _make_panel(
                    pname: str = panel_name,
                    renderer: Callable[[DataT], NodeLike] = render,
                    ppath: str = panel_path,
                ) -> FragmentHandle[Any, Any]:
                    from typing import Annotated

                    from hedron import ViewParams

                    defaults = workspace.filters()

                    @app.refreshable(
                        ppath,
                        name=f"{workspace.name}-panel-{pname}",
                        cache=None if workspace.cache is None else workspace.cache.hint,
                    )
                    async def panel_view(
                        params: Annotated[workspace.filters, ViewParams(source="query")] = defaults,  # type: ignore[valid-type]
                    ) -> object:
                        try:
                            data = await workspace._load_data(params)  # type: ignore[arg-type]
                        except Exception as exc:
                            raise error(
                                HED_DASH_0002,
                                title="Dashboard loader failure",
                                explanation=f"load() failed for panel {pname!r}: {exc}",
                                remediation="Fix the loader or return a declared error state.",
                            ) from exc
                        return renderer(data)

                    return panel_view

                handle = _make_panel()
                panel_handles[panel_name] = handle
                workspace.panel_views[panel_name] = handle

            from hedron import Stack, Text
            from hedron.app.form_commands import form_command
            from hedron_core.builtins import PageHeader

            # Runtime annotation: postponed eval cannot resolve closure attribute types.
            filters_model = workspace.filters

            def filter_command(data: BaseModel) -> object:
                from urllib.parse import urlencode

                from fastapi import HTTPException, status
                from fastapi.responses import RedirectResponse

                from hedron_core.htmx_contract import is_local_path

                # Validate the path alone so encoded query values cannot trip traversal checks.
                if not is_local_path(workspace.path):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="External redirect rejected; use redirect_external explicitly",
                    )
                raw = data.model_dump(mode="json", exclude_none=True)
                flat: dict[str, str] = {}
                for key, value in raw.items():
                    if isinstance(value, (list, tuple)):
                        flat[str(key)] = ",".join(str(item) for item in value)
                    else:
                        flat[str(key)] = str(value)
                qs = urlencode(flat)
                target = workspace.path if not qs else f"{workspace.path}?{qs}"
                response = RedirectResponse(url=target, status_code=303)
                if workspace.history == "replace":
                    response.headers["HX-Replace-Url"] = target
                elif workspace.history == "push":
                    response.headers["HX-Push-Url"] = target
                return response

            filter_command.__annotations__ = {"data": filters_model, "return": object}
            # No refreshes= here: RedirectResponse must remain a Starlette Response.
            # Panels reload from the redirected URL query string on the next page GET.
            filter_handle = form_command(
                app,
                f"{workspace.path}/filters",
                name=f"{workspace.name}-filters",
                fallback=workspace.path,
            )(filter_command)

            workspace.filter_form = filter_handle

            @app.screen(workspace.path, title=workspace.title, name=workspace.name)
            def dashboard_screen() -> object:
                nodes: list[NodeLike] = [
                    PageHeader(workspace.title),
                    filter_handle.form(submit_label="Apply filters"),
                ]
                for pname, handle in panel_handles.items():
                    if callable(handle):
                        try:
                            nodes.append(handle())  # type: ignore[arg-type]
                        except Exception:  # noqa: BLE001
                            nodes.append(Text(pname))
                    else:
                        nodes.append(Text(pname))
                return Stack(*nodes)

            workspace.screen = dashboard_screen
            return dashboard_screen

        # screen_factory registers filter + panels as side effects when materialized.
        def filter_factory(app: _DashboardApp) -> object:
            # Ensure screen_factory ran first via include order: views then commands.
            if workspace.filter_form is None:
                screen_factory(app)
            assert workspace.filter_form is not None
            return workspace.filter_form

        def panels_factory(app: _DashboardApp) -> object:
            if not workspace.panel_views:
                screen_factory(app)
            # Return a sentinel handle listing panel logical ids.
            tagged: Any = lambda: None  # noqa: E731
            tagged.logical_id = f"{workspace.name}-panels"
            tagged.path = f"{workspace.path}/panels"
            return tagged

        projection = PackageProjection(
            namespace=f"hedron.dashboard.{self.name}",
            provider=self.provider,
            provider_version=self.provider_version,
            capabilities=(ProjectionCapability(name="DashboardWorkspace", support="supported"),),
            data={
                "name": self.name,
                "path": self.path,
                "title": self.title,
                "history": self.history,
                "surfaces": ["screen", "filter_form", "panel_views"],
                "panels": list(self.panels),
            },
            limitations=("URL filters only; panels are render-only; no client store",),
        )
        return FeatureBundle(
            logical_id=f"{self.provider}:dashboard:{self.name}",
            provider=self.provider,
            provider_version=self.provider_version,
            views=(screen_factory, panels_factory),
            commands=(filter_factory,),
            projections=(projection,),
            requirements=(FeatureRequirement(name="hedron", required=True),),
            limitations=("typed URL filters; loader is the sole I/O boundary",),
        )
