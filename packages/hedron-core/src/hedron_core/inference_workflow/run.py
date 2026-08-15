"""Workflow run entry-point (delegates to InferenceWorkflow.run)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from hedron_core.inference_workflow.graph import WorkflowRunResult

if TYPE_CHECKING:
    from hedron_core.inference import InferencePolicy
    from hedron_core.inference_workflow.workflow import InferenceWorkflow
    from hedron_core.model_demo import ActionRegistry


def run_workflow(
    workflow: InferenceWorkflow,
    *,
    principal: str,
    registry: ActionRegistry,
    inputs: Mapping[str, Any] | None = None,
    policy: InferencePolicy | None = None,
    request_id: str | None = None,
) -> WorkflowRunResult:
    return workflow.run(
        principal=principal,
        registry=registry,
        inputs=inputs,
        policy=policy,
        request_id=request_id,
    )
