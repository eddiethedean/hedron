"""Durable job backend protocol and in-memory / Redis implementations."""

from __future__ import annotations

from hedron_core.jobs.auth import job_authorized, job_authorized_http
from hedron_core.jobs.backend import JobBackend
from hedron_core.jobs.backend import RedisClient as RedisClient
from hedron_core.jobs.backend import RedisPipeline as RedisPipeline
from hedron_core.jobs.codec import (
    idempotency_scope_key,
    legacy_idempotency_scope_key,
    status_from_dict,
    status_to_dict,
)
from hedron_core.jobs.gate import get_job_backend, reset_jobs_for_tests, set_job_backend
from hedron_core.jobs.memory import InMemoryJobBackend
from hedron_core.jobs.redis import RedisJobBackend
from hedron_core.jobs.status_ui import action_state_for_job, job_status_interaction
from hedron_core.jobs.types import JobHandle, JobState, JobStatus

_idempotency_scope_key = idempotency_scope_key
_legacy_idempotency_scope_key = legacy_idempotency_scope_key
_status_from_dict = status_from_dict
_status_to_dict = status_to_dict

__all__ = [
    "InMemoryJobBackend",
    "JobBackend",
    "JobHandle",
    "JobState",
    "JobStatus",
    "RedisJobBackend",
    "action_state_for_job",
    "get_job_backend",
    "job_authorized",
    "job_authorized_http",
    "job_status_interaction",
    "reset_jobs_for_tests",
    "set_job_backend",
]
