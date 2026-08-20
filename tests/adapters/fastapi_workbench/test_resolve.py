"""fastapi-workbench resolver regressions (issue #135)."""

from __future__ import annotations

from fastapi_workbench.config import WorkbenchConfig
from fastapi_workbench.resolve import resolve_deployment
from fastapi_workbench.runner import export_workbench_state


def test_issue_135_resolved_public_base_preserves_mount_path() -> None:
    """Export must retain mount path when only RESOLVED_PUBLIC_BASE is replayed."""
    resolved = resolve_deployment(
        WorkbenchConfig(public_base_url="https://wb.example/s/session/p/12345"),
        environ={},
    )
    env: dict[str, str] = {}
    export_workbench_state(resolved, environ=env)
    assert env["FASTAPI_WORKBENCH_RESOLVED_PUBLIC_BASE"] == (
        "https://wb.example/s/session/p/12345"
    )

    env.pop("FASTAPI_WORKBENCH_RESOLVED_MOUNT", None)
    env.pop("FASTAPI_WORKBENCH_ROOT_PATH", None)
    replayed = resolve_deployment(WorkbenchConfig(), environ=env)
    assert replayed.browser_mount == "/s/session/p/12345"
    assert replayed.external_origin == "https://wb.example"
    assert replayed.active is True
