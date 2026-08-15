"""Durable job backend protocol and in-memory / Redis implementations."""

from __future__ import annotations

from hedron_core.jobs.auth import job_authorized, job_authorized_http
from hedron_core.jobs.backend import JobBackend
from hedron_core.jobs.backend import RedisClient as RedisClient
from hedron_core.jobs.backend import RedisPipeline as RedisPipeline
from hedron_core.jobs.codec import _idempotency_scope_key as _idempotency_scope_key
from hedron_core.jobs.codec import _legacy_idempotency_scope_key as _legacy_idempotency_scope_key
from hedron_core.jobs.codec import _status_from_dict as _status_from_dict
from hedron_core.jobs.codec import _status_to_dict as _status_to_dict
from hedron_core.jobs.gate import get_job_backend, reset_jobs_for_tests, set_job_backend
from hedron_core.jobs.memory import InMemoryJobBackend
from hedron_core.jobs.redis import RedisJobBackend
from hedron_core.jobs.status_ui import job_status_interaction
from hedron_core.jobs.types import JobHandle, JobState, JobStatus

__all__ = [
    "InMemoryJobBackend",
    "JobBackend",
    "JobHandle",
    "JobState",
    "JobStatus",
    "RedisJobBackend",
    "get_job_backend",
    "job_authorized",
    "job_authorized_http",
    "job_status_interaction",
    "reset_jobs_for_tests",
    "set_job_backend",
]
