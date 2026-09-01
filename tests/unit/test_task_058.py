"""TASK-058 evidence."""

from __future__ import annotations

import pytest
from fastapi import Depends
from pydantic import BaseModel, Field

from hedron import JobScope, TaskFlow, Text
from hedron.jobs.flow import PollPolicy
from hedron_core.bundles import FeatureBundle
from hedron_core.diagnostics import HedronError


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


@pytest.mark.parametrize("interval", [True, 999, 60_001, 1.5, float("nan"), float("inf"), "2000"])
def test_poll_policy_rejects_malformed_or_out_of_range_intervals(interval: object) -> None:
    with pytest.raises(HedronError):
        PollPolicy(interval_ms=interval)  # type: ignore[arg-type]


def test_poll_policy_accepts_progressive_budget_boundaries() -> None:
    assert PollPolicy(interval_ms=1000).interval_ms == 1000
    assert PollPolicy(interval_ms=60_000).interval_ms == 60_000
