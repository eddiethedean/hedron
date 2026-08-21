"""WORKFLOW-057 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron import FileUpload
from hedron_core import FlowStep, ProcessFlow, Status
from hedron_core.rendering import RenderContext, RenderMode, render


def test_workflow_057_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.57.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["WORKFLOW-057"]["state"] == "Verified"


def test_file_upload_status_and_process_flow() -> None:
    ctx = RenderContext.standalone()
    upload = render(
        FileUpload(label="CSV", hint="UTF-8 CSV", status="Idle", appearance="soft"),
        context=ctx,
        mode=RenderMode.FRAGMENT,
    ).html
    assert "hedron-file-upload" in upload
    assert "UTF-8 CSV" in upload
    assert "Idle" in upload
    assert 'data-max-size="5000000"' in upload or 'data-hedron-file-upload="true"' in upload
    status = render(
        Status("Syncing", variant="activity", tone="info"),
        context=ctx,
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'data-hedron-status-variant="activity"' in status
    assert "hedron-status-indicator" in status
    assert "Syncing" in status
    flow = render(
        ProcessFlow(
            FlowStep("Extract", kind="step", status="complete"),
            FlowStep("Transform", kind="decision", status="current"),
            FlowStep("Load", kind="end", status="pending", connector="none"),
            label="Ingest",
            density="compact",
        ),
        context=ctx,
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'data-hedron-flow-kind="decision"' in flow
    assert "hedron-process-flow-connector" in flow
    assert 'data-hedron-density="compact"' in flow
