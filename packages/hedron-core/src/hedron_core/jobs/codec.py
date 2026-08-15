"""Job JSON codec and idempotency key helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import cast

from hedron_core.jobs.types import JobState, JobStatus
from hedron_core.typing_aliases import JobStatusDict, JsonValue


def _idempotency_scope_key(
    idempotency_key: str,
    *,
    tenant_id: str | None,
    auth_subject: str | None,
) -> str:
    # JSON preserves the distinction between an omitted scope and an explicit
    # empty-string scope, while also avoiding delimiter collisions in user input.
    return json.dumps([tenant_id, auth_subject, idempotency_key], separators=(",", ":"))


def _legacy_idempotency_scope_key(
    idempotency_key: str,
    *,
    tenant_id: str | None,
    auth_subject: str | None,
) -> str:
    """Return the pre-0.29 scope format for safe rolling-upgrade reads."""
    return f"{tenant_id or ''}\x1f{auth_subject or ''}\x1f{idempotency_key}"


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _status_from_dict(data: Mapping[str, object]) -> JobStatus:
    return JobStatus(
        job_id=str(data["job_id"]),
        state=JobState(str(data["state"])),
        job_type=str(data["job_type"]),
        tenant_id=_optional_str(data.get("tenant_id")),
        auth_subject=_optional_str(data.get("auth_subject")),
        result=data.get("result"),
        error=_optional_str(data.get("error")),
        retry_after=int(cast(int | float | str, data.get("retry_after", 2))),
        created_at=float(cast(int | float | str, data.get("created_at", 0))),
        updated_at=float(cast(int | float | str, data.get("updated_at", 0))),
        cancel_requested=bool(data.get("cancel_requested", False)),
    )


def _status_to_dict(
    status: JobStatus,
    *,
    payload: Mapping[str, JsonValue] | None = None,
) -> JobStatusDict:
    data: JobStatusDict = {
        "job_id": status.job_id,
        "state": status.state.value,
        "job_type": status.job_type,
        "tenant_id": status.tenant_id,
        "auth_subject": status.auth_subject,
        "result": status.result,
        "error": status.error,
        "retry_after": status.retry_after,
        "created_at": status.created_at,
        "updated_at": status.updated_at,
        "cancel_requested": status.cancel_requested,
    }
    if payload is not None:
        data["payload"] = dict(payload)
    return data
