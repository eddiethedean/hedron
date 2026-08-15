"""Workflow authorization helpers."""

from __future__ import annotations

from hedron_core.codes import HED_WORKFLOW_0002
from hedron_core.diagnostics import error
from hedron_core.inference_workflow.graph import WorkflowError, WorkflowPermission


def grant(
    permissions: dict[str, set[WorkflowPermission]],
    principal: str,
    *needed: WorkflowPermission,
) -> None:
    permissions.setdefault(principal, set()).update(needed)


def assert_permission(
    permissions: dict[str, set[WorkflowPermission]],
    principal: str,
    permission: WorkflowPermission,
) -> None:
    allowed = permissions.get(principal, set())
    if permission not in allowed:
        raise WorkflowError(
            f"Principal {principal!r} lacks {permission.value}",
            code=HED_WORKFLOW_0002,
            diagnostic=error(
                HED_WORKFLOW_0002,
                title="Workflow authorization failure",
                explanation=f"Missing permission {permission.value}.",
                remediation="Grant the required permission explicitly.",
            ),
        )
