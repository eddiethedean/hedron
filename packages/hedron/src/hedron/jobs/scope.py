"""Typed job scope for TaskFlow submit/status/cancel/result (phase 0.58)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from hedron_core.codes import HED_TASKFLOW_0001
from hedron_core.diagnostics import error

__all__ = [
    "JobScope",
    "JobScopeProvider",
    "evaluate_job_scope",
]


@dataclass(frozen=True, slots=True)
class JobScope:
    """Immutable subject/tenant identity for durable job authorization."""

    auth_subject: str | None = None
    tenant_id: str | None = None


@runtime_checkable
class JobScopeProvider(Protocol):
    """Per-request scope provider; evaluated on every submit/status/cancel/result."""

    def __call__(self, *args: object, **kwargs: object) -> JobScope: ...


def evaluate_job_scope(
    provider: JobScopeProvider | Callable[..., JobScope], **kwargs: object
) -> JobScope:
    """Evaluate scope for the current request; fail closed when unavailable."""
    try:
        try:
            scope = provider(**kwargs)
        except TypeError:
            scope = provider()
    except Exception as exc:
        raise error(
            HED_TASKFLOW_0001,
            title="Job scope unavailable",
            explanation=f"JobScopeProvider failed: {exc}",
            remediation="Ensure the scope provider returns JobScope for every request.",
        ) from exc
    if not isinstance(scope, JobScope):
        raise error(
            HED_TASKFLOW_0001,
            title="Invalid job scope",
            explanation=f"JobScopeProvider returned {type(scope).__name__}, not JobScope.",
            remediation="Return an immutable JobScope(auth_subject=..., tenant_id=...).",
        )
    return scope
