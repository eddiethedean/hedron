"""UploadFlow: secure upload form/status/result composition (phase 0.58)."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Generic, Protocol, TypeVar, cast

from fastapi import Request

from hedron.builtins.files import safe_download_response
from hedron.handles import ActionHandle, FragmentHandle
from hedron.upload import (
    UploadField,
    UploadHandle,
    cleanup_upload,
    materialize_upload,
    read_upload_capped,
    validate_upload_batch,
)
from hedron_core.bundles import FeatureBundle, FeatureRequirement
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.codes import HED_UPLOADFLOW_0001, HED_UPLOADFLOW_0002, HED_UPLOADFLOW_0003
from hedron_core.diagnostics import error

__all__ = ["UploadFlow"]

StoredT = TypeVar("StoredT")
ResultT = TypeVar("ResultT")

_SESSION_STORED_PREFIX = "hedron.upload.stored."
_SESSION_RESULT_PREFIX = "hedron.upload.result."


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
        result: Callable[[StoredT | list[StoredT]], ResultT | Awaitable[ResultT]],
        *,
        process: object | None = None,
        authorize_download: object | None = None,
        provider: str = "hedron",
        provider_version: str = "0.60.2",
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
        if authorize is None:
            raise error(
                HED_UPLOADFLOW_0001,
                title="UploadFlow authorize required",
                explanation="authorize must be a FastAPI dependency (fail closed).",
                remediation="Pass authorize=Depends(...).",
            )
        if process is not None and not callable(getattr(process, "to_bundle", None)):
            raise error(
                HED_UPLOADFLOW_0002,
                title="Invalid process TaskFlow",
                explanation="process must be a TaskFlow FeatureProvider.",
                remediation="Pass process=TaskFlow(...) or None.",
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
        self.upload_form: object | None = None
        self.status_view: object | None = None
        self.result_view: object | None = None
        self.download_view: object | None = None

    async def _call(self, fn: Callable[..., Any], *args: object, **kwargs: object) -> Any:
        value = fn(*args, **kwargs)
        if inspect.isawaitable(value):
            return await value
        return value

    def _session_key_stored(self) -> str:
        return f"{_SESSION_STORED_PREFIX}{self.name}"

    def _session_key_result(self) -> str:
        return f"{_SESSION_RESULT_PREFIX}{self.name}"

    @staticmethod
    def _opaque_stored(stored: object) -> object:
        """Return a session/payload-safe opaque representation."""
        scalar_types = (str, int, float, bool)
        if isinstance(stored, list):
            return [item if isinstance(item, scalar_types) else str(item) for item in stored]
        return stored if isinstance(stored, scalar_types) else str(stored)

    async def _enqueue_process(self, request: object, stored: object) -> str | None:
        process = self.process
        if process is None:
            return None
        from collections.abc import Mapping
        from typing import cast

        from hedron.jobs.durable import enqueue_durable
        from hedron.jobs.scope import JobScopeProvider, evaluate_job_scope
        from hedron_core.typing_aliases import JsonValue

        input_model = getattr(process, "input_model", None)
        payload_fn = getattr(process, "payload", None)
        job_type = getattr(process, "job_type", None)
        scope_policy = getattr(process, "scope", None)
        if input_model is None or not callable(payload_fn) or not isinstance(job_type, str):
            raise error(
                HED_UPLOADFLOW_0002,
                title="Invalid process TaskFlow",
                explanation="process TaskFlow is missing input_model/payload/job_type.",
                remediation="Pass a complete TaskFlow(...) as process=.",
            )
        if scope_policy is None or not callable(scope_policy):
            raise error(
                HED_UPLOADFLOW_0002,
                title="Invalid process TaskFlow scope",
                explanation="process TaskFlow is missing a JobScopeProvider.",
                remediation="Pass scope=... on the TaskFlow used as process=.",
            )
        fields = list(getattr(input_model, "model_fields", {}) or {})
        if len(fields) != 1:
            raise error(
                HED_UPLOADFLOW_0002,
                title="Invalid process TaskFlow input",
                explanation=(
                    "process TaskFlow input_model must declare exactly one field "
                    "for the opaque stored reference."
                ),
                remediation="Use a single-field input model for UploadFlow process composition.",
            )
        opaque = self._opaque_stored(stored)
        data = input_model.model_validate({fields[0]: opaque})
        try:
            body = payload_fn(data)
        except Exception as exc:
            raise error(
                HED_UPLOADFLOW_0002,
                title="Upload process payload failed",
                explanation="process.payload() rejected the opaque stored reference.",
                remediation="Accept a serializable stored id in the TaskFlow payload callback.",
            ) from exc
        if not isinstance(body, Mapping):
            raise error(
                HED_UPLOADFLOW_0002,
                title="Invalid process payload",
                explanation="process.payload() must return a JSON-compatible mapping.",
                remediation="Return a dict payload for enqueue_durable.",
            )
        scope = evaluate_job_scope(cast(JobScopeProvider, scope_policy), request=request)
        return enqueue_durable(
            job_type,
            cast(Mapping[str, JsonValue], body),
            tenant_id=scope.tenant_id,
            auth_subject=scope.auth_subject,
        )

    def to_bundle(self) -> FeatureBundle:
        flow = self

        def _ensure_upload_command(app: _UploadFlowApp) -> ActionHandle[Any, Any]:
            if flow.upload_command is not None:
                return flow.upload_command  # type: ignore[return-value]

            from fastapi import File, Request, UploadFile

            from hedron import FileUpload
            from hedron.security import redirect_local
            from hedron_core.builtins.forms import CsrfField, Form, SubmitButton

            field_name = flow.field.name
            allow_multiple = flow.field.budget.maximum_count > 1
            # Alias must match FileUpload(name=...); default param name "file" alone 422s (#591).
            file_param = File(..., alias=field_name)
            file_annotation: type[UploadFile] | type[list[UploadFile]] = (
                list[UploadFile] if allow_multiple else UploadFile
            )

            async def upload_command(
                request: Request,
                file: UploadFile | list[UploadFile] = file_param,
            ) -> object:
                uploads: list[UploadFile] = file if isinstance(file, list) else [file]
                handles: list[UploadHandle] = []
                try:
                    for upload in uploads:
                        try:
                            content = await read_upload_capped(
                                upload,
                                maximum_size=flow.field.budget.maximum_size,
                            )
                        except ValueError as exc:
                            raise error(
                                HED_UPLOADFLOW_0001,
                                title="Upload policy failure",
                                explanation=str(exc),
                                remediation="Respect UploadField budget and filename rules.",
                            ) from exc
                        try:
                            handles.append(
                                materialize_upload(
                                    filename=upload.filename or "upload.bin",
                                    content=content,
                                    content_type=upload.content_type,
                                    budget=flow.field.budget,
                                )
                            )
                        except ValueError as exc:
                            raise error(
                                HED_UPLOADFLOW_0001,
                                title="Upload policy failure",
                                explanation=str(exc),
                                remediation="Respect UploadField budget and filename rules.",
                            ) from exc
                    try:
                        validate_upload_batch(handles, flow.field.budget)
                    except ValueError as exc:
                        raise error(
                            HED_UPLOADFLOW_0001,
                            title="Upload policy failure",
                            explanation=str(exc),
                            remediation="Respect UploadField budget and filename rules.",
                        ) from exc

                    stored_items: list[StoredT] = []
                    for handle in handles:
                        try:
                            stored_items.append(cast(StoredT, await flow._call(flow.store, handle)))
                        except Exception as exc:
                            raise error(
                                HED_UPLOADFLOW_0002,
                                title="Upload store rejected",
                                explanation="store() failed; paths are not disclosed.",
                                remediation="Fix storage/quarantine callback.",
                            ) from exc
                        if handle.owned:
                            cleanup_upload(handle)
                    assert stored_items
                    stored: StoredT | list[StoredT] = (
                        stored_items[0] if len(stored_items) == 1 else stored_items
                    )
                    opaque = flow._opaque_stored(stored)
                    request.session[flow._session_key_stored()] = opaque
                    job_id = await flow._enqueue_process(request, stored)
                    if job_id is not None:
                        process = flow.process
                        assert process is not None
                        process_name = getattr(process, "name", flow.name)
                        return redirect_local(f"/{process_name}/status/{job_id}")
                    rendered = await flow._call(flow.result, stored)
                    if rendered is not None:
                        # Persist a bounded display string for the result surface.
                        request.session[flow._session_key_result()] = str(opaque)
                        return rendered
                    from hedron import Text as _Text

                    return _Text("uploaded")
                finally:
                    for handle in handles:
                        cleanup_upload(handle)

            # Concrete annotations so postponed-eval ForwardRefs resolve for FastAPI.
            upload_command.__annotations__ = {
                "request": Request,
                "file": file_annotation,
                "return": object,
            }
            # FastAPI File default must remain on the signature parameter.
            upload_command.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
                parameters=[
                    inspect.Parameter(
                        "request",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Request,
                    ),
                    inspect.Parameter(
                        "file",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=file_annotation,
                        default=file_param,
                    ),
                ],
                return_annotation=object,
            )
            # Route logical IDs are derived from the callable name. Each flow
            # must therefore expose a distinct callable identity even though
            # the implementation is a nested function.
            upload_command.__name__ = f"upload_command_{flow.name}"
            upload_command.__qualname__ = upload_command.__name__

            handle = app.command(
                f"/{flow.name}/upload",
                name=f"{flow.name}-upload-command",
                fallback=f"/{flow.name}/upload",
                dependencies=(flow.authorize,),
            )(upload_command)

            def upload_form(*, submit_label: str = "Upload") -> object:
                return Form(
                    CsrfField(),
                    FileUpload(
                        name=field_name,
                        maximum_size=flow.field.budget.maximum_size,
                        accept=",".join(flow.field.budget.allowed_content_types) or None,
                        multiple=flow.field.budget.maximum_count > 1,
                    ),
                    SubmitButton(submit_label),
                    action=handle,
                    method="post",
                    enctype="multipart/form-data",
                )

            flow.upload_command = handle
            flow.upload_form = upload_form
            return handle

        def screen_factory(app: _UploadFlowApp) -> object:
            from hedron import Stack, Text

            upload_handle = _ensure_upload_command(app)

            def upload_screen() -> object:
                from typing import cast

                from hedron_core.component import NodeLike

                form = flow.upload_form
                assert callable(form)
                return Stack(Text("Upload"), cast(NodeLike, form()))

            upload_screen.__name__ = f"upload_screen_{flow.name}"
            upload_screen.__qualname__ = upload_screen.__name__
            flow.upload_screen = app.screen(
                f"/{flow.name}/upload", title="Upload", name=f"{flow.name}-upload"
            )(upload_screen)
            # Keep handle referenced so type-checkers know materialization ran.
            _ = upload_handle
            return flow.upload_screen

        def upload_command_factory(app: _UploadFlowApp) -> object:
            return _ensure_upload_command(app)

        def result_factory(app: _UploadFlowApp) -> object:
            from hedron import Text

            async def result_view(request: Request) -> object:
                session = getattr(request, "session", None)
                if session is None:
                    return Text("No upload result")
                get = getattr(session, "get", None)
                if not callable(get):
                    return Text("No upload result")
                stored = get(flow._session_key_stored())
                if stored is None:
                    return Text("No upload result")
                try:
                    rendered = await flow._call(flow.result, stored)
                except Exception:  # noqa: BLE001
                    return Text("Upload result unavailable")
                return rendered if rendered is not None else Text(str(stored))

            result_view.__name__ = f"result_view_{flow.name}"
            result_view.__qualname__ = result_view.__name__
            registered = app.refreshable(
                f"/{flow.name}/result",
                name=f"{flow.name}-result",
                dependencies=(flow.authorize,),
            )(result_view)
            flow.result_view = registered
            flow.status_view = registered
            return registered

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
