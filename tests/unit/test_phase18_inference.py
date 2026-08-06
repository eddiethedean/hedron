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
    req = policy.admit(job_type="infer", payload={}, group="g")
    policy.request_cancel(req.request_id)

    def gen():
        yield 1
        yield 2

    with pytest.raises(InferenceError) as exc2:
        policy.stream_progress(gen(), request_id=req.request_id)
    assert exc2.value.code == HED_INFER_0003
