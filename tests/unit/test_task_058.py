"""TASK-058 evidence."""

from __future__ import annotations

from fastapi import Depends
from pydantic import BaseModel, Field

from hedron import JobScope, TaskFlow, Text
from hedron_core.bundles import FeatureBundle


def test_task_flow_and_job_scope() -> None:
    class ReportRequest(BaseModel):
        label: str = Field(min_length=1, max_length=80)

    def scope() -> JobScope:
        return JobScope(auth_subject="dev", tenant_id="local")

    def allow() -> None:
        return None

    flow = TaskFlow(
        name="report",
        input_model=ReportRequest,
        job_type="build-report",
        payload=lambda data: {"label": data.label},
        scope=scope,
        authorize_submit=Depends(allow),
        result=lambda result: Text(str(result)),
    )
    assert isinstance(flow.scope(), JobScope)
    assert flow.scope().auth_subject == "dev"

    bundle = flow.to_bundle()
    assert isinstance(bundle, FeatureBundle)
    assert "report" in bundle.logical_id or bundle.logical_id
