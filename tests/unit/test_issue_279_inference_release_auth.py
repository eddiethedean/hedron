"""#279: InferencePolicy.release must not drop another caller’s inflight maps."""

from __future__ import annotations

import pytest

from hedron_core.inference import ConcurrencyGroup, InferencePolicy
from hedron_core.jobs import InMemoryJobBackend, reset_jobs_for_tests, set_job_backend


@pytest.fixture(autouse=True)
def _jobs() -> None:
    reset_jobs_for_tests()
    set_job_backend(InMemoryJobBackend())
    yield
    reset_jobs_for_tests()


def test_release_rejects_mismatched_caller() -> None:
    policy = InferencePolicy(groups={"g": ConcurrencyGroup(name="g", limit=1)})
    status = policy.admit(
        job_type="t",
        payload={},
        group="g",
        auth_subject="alice",
        tenant_id="ten",
    )
    policy.release("g", request_id=status.request_id, auth_subject="eve", tenant_id="ten")
    assert status.request_id in policy._request_auth
    assert policy._inflight["g"] == 1

    policy.release(
        "g",
        request_id=status.request_id,
        auth_subject="alice",
        tenant_id="ten",
    )
    assert status.request_id not in policy._request_auth
    assert policy._inflight["g"] == 0
