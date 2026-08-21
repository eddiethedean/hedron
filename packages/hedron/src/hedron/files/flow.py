"""UploadFlow: secure upload form/status/result composition (phase 0.58)."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Generic, Protocol, TypeVar

from hedron.builtins.files import safe_download_response
from hedron.handles import ActionHandle, FragmentHandle
from hedron.upload import UploadField, UploadHandle, cleanup_upload, materialize_upload
from hedron_core.bundles import FeatureBundle, FeatureRequirement
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.codes import HED_UPLOADFLOW_0001, HED_UPLOADFLOW_0002, HED_UPLOADFLOW_0003
from hedron_core.diagnostics import error

__all__ = ["UploadFlow"]

StoredT = TypeVar("StoredT")
ResultT = TypeVar("ResultT")


class _UploadFlowApp(Protocol):
    """Minimal Hedron host surface for UploadFlow materialization."""

    def screen(
        self,
        path: str,
        *,
        title: str,
        name: str | None = None,
    ) -> Callable[[Callable[..., object]], object]: ...

    def command(
        self,
        path: str,
        *,
        name: str | None = None,
        fallback: str | None = None,
        dependencies: Sequence[object] | None = None,
    ) -> Callable[[Callable[..., object]], ActionHandle[Any, Any]]: ...

    def refreshable(
        self,
        path: str,
        *,
        name: str | None = None,
        dependencies: Sequence[object] | None = None,
    ) -> Callable[[Callable[..., object]], FragmentHandle[Any, Any]]: ...


class UploadFlow(Generic[StoredT, ResultT]):
    """Compose upload screen/command/result (and optional TaskFlow processing)."""

    def __init__(
        self,
        name: str,
        field: UploadField,
        authorize: object,
        store: Callable[[UploadHandle], StoredT | Awaitable[StoredT]],
        result: Callable[[StoredT], ResultT | Awaitable[ResultT]],
        *,
        process: object | None = None,
        authorize_download: object | None = None,
        provider: str = "hedron",
        provider_version: str = "0.58.0",
    ) -> None:
        if not name or not str(name).strip():
            raise error(
                HED_UPLOADFLOW_0001,
                title="UploadFlow name required",
                explanation="name must be a non-empty string.",
                remediation="Pass name=... when constructing UploadFlow.",
            )
        if not isinstance(field, UploadField):
            raise error(
                HED_UPLOADFLOW_0001,
                title="UploadFlow requires UploadField",
                explanation="field must be an UploadField policy value.",
                remediation="Construct UploadField(name=..., budget=...).",
            )
        self.name = name
        self.field = field
        self.authorize = authorize
        self.store = store
        self.result = result
        self.process = process
        self.authorize_download = authorize_download
        self.provider = provider
        self.provider_version = provider_version
        self.upload_screen: object | None = None
        self.upload_command: object | None = None
        self.status_view: object | None = None
        self.result_view: object | None = None
        self.download_view: object | None = None

    async def _call(self, fn: Callable[..., Any], *args: object, **kwargs: object) -> Any:
        value = fn(*args, **kwargs)
        if inspect.isawaitable(value):
            return await value
        return value

    def to_bundle(self) -> FeatureBundle:
        flow = self

        def screen_factory(app: _UploadFlowApp) -> object:
            from hedron import FileUpload, Form, Stack, Text

            @app.screen(f"/{flow.name}/upload", title="Upload", name=f"{flow.name}-upload")
            def upload_screen() -> object:
                return Stack(
                    Text("Upload"),
                    Form(
                        FileUpload(
                            name=flow.field.name,
                            maximum_size=flow.field.budget.maximum_size,
                            accept=",".join(flow.field.budget.allowed_content_types) or None,
                            multiple=flow.field.budget.maximum_count > 1,
                        ),
                        action=f"/{flow.name}/upload",
                        method="post",
                        enctype="multipart/form-data",
                    ),
                )

            flow.upload_screen = upload_screen
            return upload_screen

        def upload_command_factory(app: _UploadFlowApp) -> object:
            from fastapi import File, Request, UploadFile

            deps = (flow.authorize,) if flow.authorize is not None else ()

            @app.command(
                f"/{flow.name}/upload",
                name=f"{flow.name}-upload-command",
                fallback=f"/{flow.name}/upload",
                dependencies=deps,
            )
            async def upload_command(
                request: Request,
                file: UploadFile = File(...),  # noqa: B008
            ) -> object:
                handle: UploadHandle | None = None
                try:
                    content = await file.read()
                    try:
                        handle = materialize_upload(
                            filename=file.filename or "upload.bin",
                            content=content,
                            content_type=file.content_type,
                            budget=flow.field.budget,
                        )
                    except ValueError as exc:
                        raise error(
                            HED_UPLOADFLOW_0001,
                            title="Upload policy failure",
                            explanation=str(exc),
                            remediation="Respect UploadField budget and filename rules.",
                        ) from exc
                    try:
                        stored = await flow._call(flow.store, handle)
                    except Exception as exc:
                        raise error(
                            HED_UPLOADFLOW_0002,
                            title="Upload store rejected",
                            explanation="store() failed; paths are not disclosed.",
                            remediation="Fix storage/quarantine callback.",
                        ) from exc
                    if handle is not None and handle.owned:
                        cleanup_upload(handle)
                    rendered = await flow._call(flow.result, stored)
                    if flow.process is not None:
                        # Optional TaskFlow composition: opaque stored reference only.
                        to_bundle = getattr(flow.process, "to_bundle", None)
                        if not callable(to_bundle):
                            raise error(
                                HED_UPLOADFLOW_0002,
                                title="Invalid process TaskFlow",
                                explanation="process must be a TaskFlow FeatureProvider.",
                                remediation="Pass process=TaskFlow(...) or None.",
                            )
                    from hedron import Text

                    return rendered if rendered is not None else Text("uploaded")
                finally:
                    cleanup_upload(handle)

            flow.upload_command = upload_command
            return upload_command

        def result_factory(app: _UploadFlowApp) -> object:
            @app.refreshable(f"/{flow.name}/result", name=f"{flow.name}-result")
            def result_view() -> object:
                from hedron import Text

                return Text("result")

            flow.result_view = result_view
            return result_view

        def download_factory(app: _UploadFlowApp) -> object | None:
            if flow.authorize_download is None:
                return None

            @app.refreshable(
                f"/{flow.name}/download",
                name=f"{flow.name}-download",
                dependencies=(flow.authorize_download,),
            )
            def download_view() -> object:
                raise error(
                    HED_UPLOADFLOW_0003,
                    title="Download not configured",
                    explanation=(
                        "authorize_download is set but the application must supply "
                        "a stored path via result/download composition."
                    ),
                    remediation="Eject and wire safe_download_response with an authorized root.",
                )

            flow.download_view = download_view
            return download_view

        views: list[object] = [screen_factory, result_factory]
        commands: list[object] = [upload_command_factory]
        if self.authorize_download is not None:
            views.append(download_factory)

        projection = PackageProjection(
            namespace=f"hedron.files.uploadflow.{self.name}",
            provider=self.provider,
            provider_version=self.provider_version,
            capabilities=(ProjectionCapability(name="UploadFlow", support="supported"),),
            data={
                "name": self.name,
                "field": self.field.name,
                "surfaces": [
                    "upload_screen",
                    "upload_command",
                    "upload_form",
                    "status_view",
                    "result_view",
                    "download_view",
                ],
                "download": self.authorize_download is not None,
                "process": self.process is not None,
            },
            limitations=("storage/scanning application-owned; no path disclosure",),
        )
        return FeatureBundle(
            logical_id=f"{self.provider}:uploadflow:{self.name}",
            provider=self.provider,
            provider_version=self.provider_version,
            views=tuple(views),
            commands=tuple(commands),
            projections=(projection,),
            requirements=(FeatureRequirement(name="hedron", required=True),),
            limitations=("uses UploadField/UploadHandle and safe_download_response",),
        )


# Re-export for callers that compose downloads explicitly.
_ = safe_download_response
