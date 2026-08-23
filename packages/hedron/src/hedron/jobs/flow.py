"""TaskFlow: durable job UI composition over JobBackend (phase 0.58)."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Generic, Literal, Protocol, TypeAlias, TypeVar

from pydantic import BaseModel

from hedron.handles import ActionHandle, FragmentHandle
from hedron.jobs.durable import enqueue_durable
from hedron.jobs.scope import JobScope, JobScopeProvider, evaluate_job_scope
from hedron_core.bundles import FeatureBundle, FeatureRequirement
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.codes import HED_TASKFLOW_0001, HED_TASKFLOW_0003
from hedron_core.component import NodeLike
from hedron_core.diagnostics import error
from hedron_core.jobs import JobState, get_job_backend, job_authorized_http
from hedron_core.operation_workflow import is_terminal_job_state
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "PollPolicy",
    "TaskFlow",
    "TaskUnavailablePolicy",
    "Dependency",
]

InputT = TypeVar("InputT", bound=BaseModel)
ResultT = TypeVar("ResultT")

TaskUnavailablePolicy = Literal["fail_closed"]
Dependency: TypeAlias = object


class _TaskFlowApp(Protocol):
    """Minimal Hedron host surface for TaskFlow materialization."""

    def refreshable(
        self,
        path: str,
        *,
        name: str | None = None,
        dependencies: Sequence[object] | None = None,
    ) -> Callable[[Callable[..., object]], FragmentHandle[Any, Any]]: ...

    def command(
        self,
        path: str,
        *,
        name: str | None = None,
        fallback: str | None = None,
        dependencies: Sequence[object] | None = None,
    ) -> Callable[[Callable[..., object]], ActionHandle[Any, Any]]: ...


@dataclass(frozen=True, slots=True)
class PollPolicy:
    """Bounded status polling policy (stops on terminal job states)."""

    interval_ms: int = 2000
    stop_on_terminal: bool = True

    def __post_init__(self) -> None:
        if self.interval_ms < 1000 or self.interval_ms > 60_000:
            raise error(
                HED_TASKFLOW_0003,
                title="Invalid poll interval",
                explanation=f"interval_ms={self.interval_ms} is outside 1000–60000.",
                remediation="Use PollPolicy(interval_ms=...) within progressive budgets.",
            )


class TaskFlow(Generic[InputT, ResultT]):
    """Compose submit/status/cancel/result surfaces around an application JobBackend."""

    def __init__(
        self,
        name: str,
        input_model: type[InputT],
        job_type: str,
        payload: Callable[[InputT], Mapping[str, JsonValue]],
        scope: JobScopeProvider,
        authorize_submit: Dependency,
        result: Callable[[ResultT], NodeLike],
        *,
        authorize_cancel: Dependency | None = None,
        poll: PollPolicy | None = None,
        backend_unavailable: TaskUnavailablePolicy = "fail_closed",
        provider: str = "hedron",
        provider_version: str = "0.60.0",
    ) -> None:
        if not name or not str(name).strip():
            raise error(
                HED_TASKFLOW_0001,
                title="TaskFlow name required",
                explanation="name must be a non-empty string.",
                remediation="Pass name=... when constructing TaskFlow.",
            )
        if not job_type or not str(job_type).strip():
            raise error(
                HED_TASKFLOW_0001,
                title="TaskFlow job_type required",
                explanation="job_type must be a non-empty backend job type string.",
                remediation="Pass the JobBackend job_type your workers handle.",
            )
        self.name = name
        self.input_model = input_model
        self.job_type = job_type
        self.payload = payload
        self.scope = scope
        self.authorize_submit = authorize_submit
        self.result = result
        self.authorize_cancel = authorize_cancel
        self.poll = poll if poll is not None else PollPolicy()
        self.backend_unavailable = backend_unavailable
        self.provider = provider
        self.provider_version = provider_version
        self.submit_command: object | None = None
        self.status_view: object | None = None
        self.cancel_command: object | None = None
        self.result_view: object | None = None

    def _deps(self, *items: Dependency | None) -> Sequence[object]:
        return tuple(item for item in items if item is not None)

    def _scope_for_request(self) -> JobScope:
        try:
            from hedron.routing.router import current_request

            request = current_request.get()
        except Exception:  # noqa: BLE001
            request = None
        if request is not None:
            return evaluate_job_scope(self.scope, request=request)
        return evaluate_job_scope(self.scope)

    def to_bundle(self) -> FeatureBundle:
        flow = self

        def submit_factory(app: _TaskFlowApp) -> object:
            from starlette.exceptions import HTTPException

            from hedron.app.form_commands import form_command

            input_model = flow.input_model

            def submit_command(data: BaseModel) -> object:
                scope = flow._scope_for_request()
                try:
                    body = flow.payload(data)  # type: ignore[arg-type]
                except Exception as exc:
                    raise HTTPException(status_code=422, detail="invalid_payload") from exc
                try:
                    job_id = enqueue_durable(
                        flow.job_type,
                        body,
                        tenant_id=scope.tenant_id,
                        auth_subject=scope.auth_subject,
                    )
                except Exception as exc:
                    if flow.backend_unavailable == "fail_closed":
                        raise error(
                            HED_TASKFLOW_0001,
                            title="Job backend unavailable",
                            explanation=f"Durable enqueue failed: {exc}",
                            remediation="Configure a durable JobBackend before submit.",
                        ) from exc
                    raise
                from hedron.security import redirect_local

                return redirect_local(f"/{flow.name}/status/{job_id}")

            submit_command.__annotations__ = {"data": input_model, "return": object}
            submit_handle = form_command(
                app,
                f"/{flow.name}/submit",
                name=f"{flow.name}-submit",
                fallback=f"/{flow.name}/status",
                dependencies=flow._deps(flow.authorize_submit),
            )(submit_command)

            flow.submit_command = submit_handle
            return submit_handle

        def status_factory(app: _TaskFlowApp) -> object:
            from typing import Annotated

            from pydantic import BaseModel, Field
            from starlette.exceptions import HTTPException

            from hedron import Poll, ViewParams
            from hedron_core.builtins import Status

            class _JobId(BaseModel):
                job_id: str = Field(min_length=1)

            @app.refreshable(
                f"/{flow.name}/status/{{job_id}}",
                name=f"{flow.name}-status",
                dependencies=flow._deps(flow.authorize_submit),
            )
            def status_view(
                params: Annotated[_JobId, ViewParams()],  # type: ignore[valid-type]
            ) -> object:
                scope = flow._scope_for_request()
                job_id = str(params.job_id)
                try:
                    status = get_job_backend().get(
                        job_id,
                        auth_subject=scope.auth_subject,
                        tenant_id=scope.tenant_id,
                    )
                except Exception as exc:
                    raise error(
                        HED_TASKFLOW_0001,
                        title="Job backend unavailable",
                        explanation=f"Status lookup failed: {exc}",
                        remediation="Ensure the JobBackend is healthy.",
                    ) from exc
                if status is None or not job_authorized_http(
                    status,
                    auth_subject=scope.auth_subject,
                    tenant_id=scope.tenant_id,
                ):
                    raise HTTPException(status_code=404, detail="Job not found")
                label = f"Job {status.job_id}: {status.state.value}"
                body = Status(label, tone="info", live=True)
                if flow.poll.stop_on_terminal and is_terminal_job_state(status.state):
                    if status.state is JobState.SUCCEEDED and status.result is not None:
                        try:
                            return flow.result(status.result)  # type: ignore[arg-type]
                        except Exception:  # noqa: BLE001
                            return body
                    return body
                from hedron import ComponentRef

                ref = ComponentRef(
                    logical_id=f"{flow.name}-status",
                    path=f"/{flow.name}/status/{job_id}",
                    method="GET",
                )
                return Poll(
                    ref=ref,
                    interval_ms=flow.poll.interval_ms,
                    content=body,
                )

            flow.status_view = status_view
            return status_view

        def cancel_factory(app: _TaskFlowApp) -> object | None:
            if flow.authorize_cancel is None:
                return None
            from typing import Annotated

            from pydantic import BaseModel, Field
            from starlette.exceptions import HTTPException

            from hedron import FormBody, Text

            class _CancelBody(BaseModel):
                job_id: str = Field(min_length=1)

            @app.command(
                f"/{flow.name}/cancel",
                name=f"{flow.name}-cancel",
                fallback=f"/{flow.name}/status",
                dependencies=flow._deps(flow.authorize_cancel),
            )
            def cancel_command(
                data: Annotated[_CancelBody, FormBody()],  # type: ignore[valid-type]
            ) -> object:
                scope = flow._scope_for_request()
                job_id = str(data.job_id)
                try:
                    get_job_backend().request_cancel(
                        job_id,
                        auth_subject=scope.auth_subject,
                        tenant_id=scope.tenant_id,
                    )
                except Exception as exc:
                    raise error(
                        HED_TASKFLOW_0003,
                        title="Cancel failed",
                        explanation=f"request_cancel raised: {exc}",
                        remediation="Check JobBackend cancel support and scope.",
                    ) from exc
                status = get_job_backend().get(
                    job_id,
                    auth_subject=scope.auth_subject,
                    tenant_id=scope.tenant_id,
                )
                if status is None or not job_authorized_http(
                    status,
                    auth_subject=scope.auth_subject,
                    tenant_id=scope.tenant_id,
                ):
                    raise HTTPException(status_code=404, detail="Job not found")
                return Text(f"cancel:{status.state.value}")

            flow.cancel_command = cancel_command
            return cancel_command

        def result_factory(app: _TaskFlowApp) -> object:
            from typing import Annotated

            from pydantic import BaseModel, Field
            from starlette.exceptions import HTTPException

            from hedron import Text, ViewParams

            class _JobId(BaseModel):
                job_id: str = Field(min_length=1)

            @app.refreshable(
                f"/{flow.name}/result/{{job_id}}",
                name=f"{flow.name}-result",
                dependencies=flow._deps(flow.authorize_submit),
            )
            def result_view(
                params: Annotated[_JobId, ViewParams()],  # type: ignore[valid-type]
            ) -> object:
                scope = flow._scope_for_request()
                job_id = str(params.job_id)
                status = get_job_backend().get(
                    job_id,
                    auth_subject=scope.auth_subject,
                    tenant_id=scope.tenant_id,
                )
                if status is None or not job_authorized_http(
                    status,
                    auth_subject=scope.auth_subject,
                    tenant_id=scope.tenant_id,
                ):
                    raise HTTPException(status_code=404, detail="Job not found")
                if not is_terminal_job_state(status.state):
                    raise error(
                        HED_TASKFLOW_0003,
                        title="Job not terminal",
                        explanation=f"Job {job_id!r} is still {status.state.value}.",
                        remediation="Poll status_view until a terminal state.",
                    )
                if status.state is not JobState.SUCCEEDED:
                    raise HTTPException(status_code=409, detail=status.state.value)
                if status.result is None:
                    return Text("empty")
                return flow.result(status.result)  # type: ignore[arg-type]

            flow.result_view = result_view
            return result_view

        views: list[object] = [status_factory, result_factory]
        commands: list[object] = [submit_factory]
        if self.authorize_cancel is not None:
            commands.append(cancel_factory)

        projection = PackageProjection(
            namespace=f"hedron.jobs.taskflow.{self.name}",
            provider=self.provider,
            provider_version=self.provider_version,
            capabilities=(ProjectionCapability(name="TaskFlow", support="supported"),),
            data={
                "name": self.name,
                "job_type": self.job_type,
                "surfaces": [
                    "submit_command",
                    "submit_form",
                    "status_view",
                    "cancel_command",
                    "result_view",
                ],
                "poll_interval_ms": self.poll.interval_ms,
                "backend_unavailable": self.backend_unavailable,
                "cancel": self.authorize_cancel is not None,
            },
            limitations=("no worker/scheduler; JobBackend and scope remain application-owned",),
        )
        return FeatureBundle(
            logical_id=f"{self.provider}:taskflow:{self.name}",
            provider=self.provider,
            provider_version=self.provider_version,
            views=tuple(views),
            commands=tuple(commands),
            projections=(projection,),
            requirements=(FeatureRequirement(name="hedron", required=True),),
            limitations=("durable UI only; no unscoped enumeration",),
        )
