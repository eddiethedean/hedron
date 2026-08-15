"""Job observation authorization helpers."""

from __future__ import annotations

from hedron_core.jobs.types import JobStatus


def job_authorized(
    status: JobStatus,
    *,
    auth_subject: str | None = None,
    tenant_id: str | None = None,
) -> bool:
    """Return True when caller credentials exactly match the job's auth/tenant scope.

    Each dimension is compared for equality (including ``None``). A tenant-only job
    (``auth_subject=None``) does **not** authorize an arbitrary subject in that tenant —
    the caller must also pass ``auth_subject=None``. Unscoped jobs authorize only when
    the caller likewise omits both scopes — use :func:`job_authorized_http` for HTTP
    observers (unscoped jobs are never HTTP-readable).
    """
    return status.auth_subject == auth_subject and status.tenant_id == tenant_id


def job_authorized_http(
    status: JobStatus,
    *,
    auth_subject: str | None = None,
    tenant_id: str | None = None,
) -> bool:
    """Authorize job observation over HTTP (fail closed for unscoped jobs).

    Jobs without stored scope are never readable via HTTP helpers. Callers must
    supply credentials that **exactly** match every scope dimension on the job
    (including ``None`` on unset dimensions).
    """
    if status.auth_subject is None and status.tenant_id is None:
        return False
    if auth_subject is None and tenant_id is None:
        return False
    return job_authorized(status, auth_subject=auth_subject, tenant_id=tenant_id)
