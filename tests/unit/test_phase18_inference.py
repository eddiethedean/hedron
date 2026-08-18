"""Phase 0.18 INFER-018: InferencePolicy over JobBackend."""

from __future__ import annotations

import pytest

from hedron_core import (
    BatchWindow,
    ConcurrencyGroup,
    InferenceAdmission,
    InferenceError,
    InferencePolicy,
    InferencePriority,
    InProcessInferenceQueue,
    QueuedInference,
)
from hedron_core.codes import HED_INFER_0001, HED_INFER_0003
from hedron_core.jobs import InMemoryJobBackend, reset_jobs_for_tests, set_job_backend


@pytest.fixture(autouse=True)
def _jobs() -> None:
    reset_jobs_for_tests()
    set_job_backend(InMemoryJobBackend())
    yield
    reset_jobs_for_tests()


def test_admission_queue_and_eta() -> None:
    policy = InferencePolicy(
        groups={"gpu": ConcurrencyGroup(name="gpu", limit=1)},
        max_queue=10,
        default_eta_per_item=2.0,
    )
    first = policy.admit(
        job_type="infer",
        payload={"x": 1},
        group="gpu",
        priority=InferencePriority.NORMAL,
    )
    assert first.admission == InferenceAdmission.ACCEPTED
    assert first.job_id is not None

    second = policy.admit(
        job_type="infer",
        payload={"x": 2},
        group="gpu",
        priority=InferencePriority.HIGH,
    )
    assert second.admission == InferenceAdmission.QUEUED
    assert second.position == 0
    assert second.eta_seconds == 2.0

    policy.release("gpu")
    started = policy.drain_ready()
    assert len(started) == 1
    assert started[0][0].request_id == second.request_id


def test_overload() -> None:
    policy = InferencePolicy(
        groups={"cpu": ConcurrencyGroup(name="cpu", limit=1)},
        max_queue=1,
    )
    policy.admit(job_type="infer", payload={}, group="cpu")
    policy.admit(job_type="infer", payload={}, group="cpu")
    with pytest.raises(InferenceError) as exc:
        policy.admit(job_type="infer", payload={}, group="cpu")
    assert exc.value.code == HED_INFER_0001


def test_batch_grouping_and_dev_queue() -> None:
    from hedron_core.inference import InferenceDiagnostics

    policy = InferencePolicy(
        groups={"g": ConcurrencyGroup(name="g", limit=4)},
        batch=BatchWindow(max_size=2, shape_key="default"),
        development_in_process=True,
    )
    items = [
        QueuedInference(request_id="a", job_type="t", payload={}, group="g", shape_key="img"),
        QueuedInference(request_id="b", job_type="t", payload={}, group="g", shape_key="img"),
        QueuedInference(request_id="c", job_type="t", payload={}, group="g", shape_key="txt"),
    ]
    for it in items:
        policy._diagnostics[it.request_id] = InferenceDiagnostics(
            request_id=it.request_id, group="g", queue_ms=0.0
        )
    batches = policy.form_batch(items)
    assert len(batches) == 2
    sizes = sorted(len(chunk) for _, chunk in batches)
    assert sizes == [1, 2]

    q = InProcessInferenceQueue(policy=policy)
    q.enqueue(items[0])
    assert q.pop() is not None

    with pytest.raises(InferenceError):
        InProcessInferenceQueue(policy=InferencePolicy(development_in_process=False))


def test_cancel_stream() -> None:
    policy = InferencePolicy(groups={"g": ConcurrencyGroup(name="g", limit=2)})
    req = policy.admit(
        job_type="infer",
        payload={},
        group="g",
        auth_subject="alice",
        tenant_id="ten",
    )
    assert policy.request_cancel(req.request_id, auth_subject="alice", tenant_id="ten") is True
    assert policy.request_cancel("unknown-id", auth_subject="alice", tenant_id="ten") is False

    def gen():
        yield 1
        yield 2

    with pytest.raises(InferenceError) as exc2:
        policy.stream_progress(gen(), request_id=req.request_id)
    assert exc2.value.code == HED_INFER_0003


def test_cancel_releases_inflight_and_backend() -> None:
    backend = InMemoryJobBackend()
    set_job_backend(backend)
    policy = InferencePolicy(groups={"g": ConcurrencyGroup(name="g", limit=1)})
    req = policy.admit(
        job_type="infer",
        payload={},
        group="g",
        backend=backend,
        auth_subject="alice",
        tenant_id="ten",
    )
    assert req.job_id is not None
    assert policy._inflight["g"] == 1
    assert (
        policy.request_cancel(
            req.request_id, backend=backend, auth_subject="alice", tenant_id="ten"
        )
        is True
    )
    assert policy._inflight["g"] == 0


def test_cancel_requires_caller_identity_matching_owner() -> None:
    """#264: cancel must not replay stored owner credentials to the backend."""
    backend = InMemoryJobBackend()
    set_job_backend(backend)
    policy = InferencePolicy()
    policy.register_group(ConcurrencyGroup(name="g", limit=1))
    st = policy.admit(
        job_type="demo",
        payload={"x": 1},
        group="g",
        auth_subject="alice",
        tenant_id="ten",
    )
    assert st.job_id is not None
    assert backend.request_cancel(st.job_id, auth_subject="eve", tenant_id="ten") is False
    assert policy.request_cancel(st.request_id, auth_subject="eve", tenant_id="ten") is False
    assert policy.request_cancel(st.request_id) is False
    queued = policy.admit(
        job_type="demo",
        payload={"x": 2},
        group="g",
        auth_subject="alice",
        tenant_id="ten",
    )
    assert queued.admission == InferenceAdmission.QUEUED
    assert policy.request_cancel(queued.request_id, auth_subject="eve", tenant_id="ten") is False
    assert any(q.request_id == queued.request_id for q in policy._queue)
    assert policy.request_cancel(queued.request_id, auth_subject="alice", tenant_id="ten") is True
    assert policy.request_cancel(st.request_id, auth_subject="alice", tenant_id="ten") is True


def test_cancel_fails_closed_for_unscoped_and_mismatched_tenant() -> None:
    policy = InferencePolicy(groups={"g": ConcurrencyGroup(name="g", limit=2)})
    unscoped = policy.admit(job_type="demo", payload={}, group="g")
    assert policy.request_cancel(unscoped.request_id) is False
    assert (
        policy.request_cancel(unscoped.request_id, auth_subject="alice", tenant_id="ten") is False
    )
    scoped = policy.admit(
        job_type="demo",
        payload={},
        group="g",
        auth_subject="alice",
        tenant_id="ten",
    )
    assert (
        policy.request_cancel(scoped.request_id, auth_subject="alice", tenant_id="other") is False
    )


def test_request_ids_are_not_sequential() -> None:
    policy = InferencePolicy(groups={"g": ConcurrencyGroup(name="g", limit=8)})
    ids = [policy.admit(job_type="infer", payload={}, group="g").request_id for _ in range(8)]
    assert all(rid.startswith("inf-") for rid in ids)
    assert ids != [f"inf-{n}" for n in range(1, 9)]
    assert len(set(ids)) == 8


def test_fair_drain_and_batch_max_wait() -> None:
    policy = InferencePolicy(
        groups={"g": ConcurrencyGroup(name="g", limit=1, fair=True)},
        max_queue=10,
        batch=BatchWindow(max_size=4, max_wait_ms=10),
    )
    policy.admit(job_type="infer", payload={}, group="g", tenant_id="t1")
    policy.admit(job_type="infer", payload={}, group="g", tenant_id="t2")
    policy.admit(job_type="infer", payload={}, group="g", tenant_id="t1")
    policy.release("g", tenant_id="t1")
    started = policy.drain_ready()
    assert len(started) == 1
    # Fairness should prefer alternating tenants (t2 before second t1).
    assert started[0][0].tenant_id == "t2"

    now = 100.0
    items = [
        QueuedInference(
            request_id="a",
            job_type="t",
            payload={},
            group="g",
            shape_key="img",
            enqueued_at=now - 1.0,
        ),
        QueuedInference(
            request_id="b",
            job_type="t",
            payload={},
            group="g",
            shape_key="img",
            enqueued_at=now - 0.9,
        ),
    ]
    from hedron_core.inference import InferenceDiagnostics

    for it in items:
        policy._diagnostics[it.request_id] = InferenceDiagnostics(
            request_id=it.request_id, group="g", queue_ms=0.0
        )
    batches = policy.form_batch(items, now=now)
    # max_wait exceeded for oldest → flush before max_size
    assert len(batches) == 2
    assert all(len(chunk) == 1 for _, chunk in batches)
