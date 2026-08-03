"""BackgroundTasks vs durable jobs."""

from __future__ import annotations

from hedron.jobs import enqueue_durable, schedule_post_response
from hedron_core.jobs import reset_jobs_for_tests


def test_enqueue_durable_distinct_from_background() -> None:
    reset_jobs_for_tests()
    job_id = enqueue_durable("x", {"a": 1}, idempotency_key="i")
    assert isinstance(job_id, str) and job_id

    class _Tasks:
        def __init__(self) -> None:
            self.calls: list[tuple[object, ...]] = []

        def add_task(self, fn: object, *args: object) -> None:
            self.calls.append((fn, *args))

    tasks = _Tasks()
    schedule_post_response(tasks, lambda: None)  # type: ignore[arg-type]
    assert len(tasks.calls) == 1
