"""Inference execution policy over JobBackend (RFC-0047 / INFER-018).

Admission, fairness, named concurrency groups, batch windows, queue position/ETA,
generator streaming, and cancel/timeout semantics compose durable ``JobBackend``
contracts. An in-process queue is development-only and is never the production
durability promise.
"""

from __future__ import annotations

import itertools
import threading
import time
from collections import OrderedDict, defaultdict, deque
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from hedron_core.codes import HED_INFER_0001, HED_INFER_0002, HED_INFER_0003
from hedron_core.diagnostics import HedronError, error
from hedron_core.jobs import JobBackend, JobHandle, get_job_backend
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "BatchWindow",
    "ConcurrencyGroup",
    "InferenceAdmission",
    "InferenceDiagnostics",
    "InferenceError",
    "InferencePolicy",
    "InferencePriority",
    "InferenceQueueStatus",
    "InProcessInferenceQueue",
    "QueuedInference",
]


class InferenceError(ValueError):
    """Inference admission, scheduling, or lifecycle failure."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        diagnostic: HedronError | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.diagnostic = diagnostic


class InferencePriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class InferenceAdmission(StrEnum):
    ACCEPTED = "accepted"
    QUEUED = "queued"
    REJECTED = "rejected"
    OVERLOAD = "overload"


@dataclass(frozen=True, slots=True)
class ConcurrencyGroup:
    """Named model/resource/GPU capacity group (multi-worker aware via backend)."""

    name: str
    limit: int
    fair: bool = True


@dataclass(frozen=True, slots=True)
class BatchWindow:
    """Bounded batching window for compatible-shape grouping."""

    max_size: int
    max_wait_ms: int = 50
    shape_key: str = "default"


@dataclass(frozen=True, slots=True)
class QueuedInference:
    request_id: str
    job_type: str
    payload: Mapping[str, JsonValue]
    group: str
    priority: InferencePriority = InferencePriority.NORMAL
    tenant_id: str | None = None
    auth_subject: str | None = None
    correlation_id: str = ""
    shape_key: str = "default"
    enqueued_at: float = 0.0


@dataclass(frozen=True, slots=True)
class InferenceQueueStatus:
    request_id: str
    admission: InferenceAdmission
    position: int | None = None
    queue_size: int = 0
    eta_seconds: float | None = None
    group: str | None = None
    job_id: str | None = None
    batch_id: str | None = None


@dataclass(frozen=True, slots=True)
class InferenceDiagnostics:
    """Explorer-facing timing and resource snapshot (redacted inputs)."""

    request_id: str
    group: str
    queue_ms: float
    execute_ms: float | None = None
    batch_id: str | None = None
    batch_size: int = 1
    cancelled: bool = False
    overload: bool = False


_PRIORITY_RANK = {
    InferencePriority.HIGH: 0,
    InferencePriority.NORMAL: 1,
    InferencePriority.LOW: 2,
}


@dataclass
class InferencePolicy:
    """Admission and scheduling policy layered on a durable ``JobBackend``."""

    groups: Mapping[str, ConcurrencyGroup] = field(default_factory=dict)
    max_queue: int = 100
    default_eta_per_item: float = 1.0
    batch: BatchWindow | None = None
    development_in_process: bool = False
    cancel_ttl_seconds: float = 60.0
    max_cancelled: int = 1_024
    _inflight: dict[str, int] = field(default_factory=lambda: defaultdict(int), init=False)
    _inflight_ids: dict[str, deque[str]] = field(
        default_factory=lambda: defaultdict(deque), init=False, repr=False
    )
    _queue: list[QueuedInference] = field(default_factory=list, init=False)
    _lock: threading.RLock = field(default_factory=threading.RLock, init=False)
    _seq: Iterator[int] = field(default_factory=lambda: itertools.count(1), init=False, repr=False)
    _cancel: OrderedDict[str, float] = field(default_factory=OrderedDict, init=False, repr=False)
    _diagnostics: dict[str, InferenceDiagnostics] = field(default_factory=dict, init=False)
    _request_jobs: dict[str, str] = field(default_factory=dict, init=False)
    _request_groups: dict[str, str] = field(default_factory=dict, init=False)
    _request_auth: dict[str, tuple[str | None, str | None]] = field(
        default_factory=dict, init=False
    )
    _fair_cursor: dict[str, int] = field(default_factory=lambda: defaultdict(int), init=False)

    def register_group(self, group: ConcurrencyGroup) -> None:
        if group.limit < 1:
            raise InferenceError(
                "Concurrency group limit must be >= 1",
                code=HED_INFER_0002,
                diagnostic=error(
                    HED_INFER_0002,
                    title="Invalid concurrency group",
                    explanation=f"Group {group.name!r} has limit {group.limit}.",
                    remediation="Set a positive capacity limit.",
                ),
            )
        self.groups = {**dict(self.groups), group.name: group}

    def admit(
        self,
        *,
        job_type: str,
        payload: Mapping[str, JsonValue],
        group: str,
        priority: InferencePriority = InferencePriority.NORMAL,
        tenant_id: str | None = None,
        auth_subject: str | None = None,
        correlation_id: str = "",
        shape_key: str = "default",
        backend: JobBackend | None = None,
    ) -> InferenceQueueStatus:
        """Admit an inference request: run immediately, queue, or reject on overload."""
        with self._lock:
            if group not in self.groups:
                raise InferenceError(
                    f"Unknown concurrency group: {group!r}",
                    code=HED_INFER_0002,
                    diagnostic=error(
                        HED_INFER_0002,
                        title="Unknown concurrency group",
                        explanation=f"Group {group!r} is not registered.",
                        remediation="Register the group before admitting work.",
                    ),
                )
            request_id = f"inf-{next(self._seq)}"
            now = time.monotonic()
            item = QueuedInference(
                request_id=request_id,
                job_type=job_type,
                payload=dict(payload),
                group=group,
                priority=priority,
                tenant_id=tenant_id,
                auth_subject=auth_subject,
                correlation_id=correlation_id,
                shape_key=shape_key,
                enqueued_at=now,
            )
            capacity = self.groups[group].limit
            if self._inflight[group] < capacity:
                handle = self._submit(item, backend=backend)
                self._inflight[group] += 1
                self._inflight_ids[group].append(request_id)
                self._request_jobs[request_id] = handle.job_id
                self._request_groups[request_id] = group
                self._request_auth[request_id] = (auth_subject, tenant_id)
                self._diagnostics[request_id] = InferenceDiagnostics(
                    request_id=request_id,
                    group=group,
                    queue_ms=0.0,
                )
                return InferenceQueueStatus(
                    request_id=request_id,
                    admission=InferenceAdmission.ACCEPTED,
                    position=0,
                    queue_size=len(self._queue),
                    eta_seconds=0.0,
                    group=group,
                    job_id=handle.job_id,
                )
            if len(self._queue) >= self.max_queue:
                raise InferenceError(
                    "Inference queue overload",
                    code=HED_INFER_0001,
                    diagnostic=error(
                        HED_INFER_0001,
                        title="Inference queue overload",
                        explanation=f"Queue length reached max_queue={self.max_queue}.",
                        remediation="Retry later, scale workers, or raise capacity.",
                    ),
                )
            self._queue.append(item)
            self._request_auth[request_id] = (auth_subject, tenant_id)
            self._queue.sort(key=lambda q: (_PRIORITY_RANK[q.priority], q.enqueued_at))
            position = next(i for i, q in enumerate(self._queue) if q.request_id == request_id)
            eta = (position + 1) * self.default_eta_per_item
            self._diagnostics[request_id] = InferenceDiagnostics(
                request_id=request_id,
                group=group,
                queue_ms=0.0,
            )
            return InferenceQueueStatus(
                request_id=request_id,
                admission=InferenceAdmission.QUEUED,
                position=position,
                queue_size=len(self._queue),
                eta_seconds=eta,
                group=group,
            )

    def request_cancel(self, request_id: str, *, backend: JobBackend | None = None) -> bool:
        with self._lock:
            self._prune_cancelled(time.monotonic())
            known = (
                request_id in self._diagnostics
                or any(q.request_id == request_id for q in self._queue)
                or request_id in self._request_jobs
            )
            if not known and request_id not in self._cancel:
                return False
            was_queued = any(q.request_id == request_id for q in self._queue)
            job_id = self._request_jobs.get(request_id)
            group = self._request_groups.get(request_id)
            auth_subject, tenant_id = self._request_auth.get(request_id, (None, None))
            for queued in self._queue:
                if queued.request_id == request_id:
                    auth_subject = queued.auth_subject
                    tenant_id = queued.tenant_id
                    break

            if was_queued:
                self._mark_cancel_id(request_id)
                self._queue = [q for q in self._queue if q.request_id != request_id]
                self._forget_request_maps(request_id)
                return True

            if job_id is not None:
                job_backend = backend or get_job_backend()
                cancelled_backend = bool(
                    job_backend.request_cancel(
                        job_id,
                        auth_subject=auth_subject,
                        tenant_id=tenant_id,
                    )
                )
                if not cancelled_backend:
                    # Do not free the concurrency slot or claim cancel while the
                    # durable job remains running (scoped authz denial / race).
                    return False
                self._mark_cancel_id(request_id)
                if group is not None and request_id in self._request_groups:
                    self._inflight[group] = max(0, self._inflight[group] - 1)
                    self._drop_inflight_id(group, request_id)
                self._forget_request_maps(request_id)
                return True

            self._mark_cancel_id(request_id)
            self._forget_request_maps(request_id)
            return known

    def is_cancelled(self, request_id: str) -> bool:
        with self._lock:
            now = time.monotonic()
            self._prune_cancelled(now)
            stamped = self._cancel.get(request_id)
            if stamped is None:
                return False
            if now - stamped > self.cancel_ttl_seconds:
                del self._cancel[request_id]
                return False
            return True

    def drain_ready(
        self, *, backend: JobBackend | None = None
    ) -> list[tuple[QueuedInference, JobHandle]]:
        """Promote queued items into free concurrency slots (fair within group)."""
        started: list[tuple[QueuedInference, JobHandle]] = []
        with self._lock:
            self._prune_cancelled(time.monotonic())
            # Partition by group while preserving priority/enqueue order inside each group.
            by_group: dict[str, list[QueuedInference]] = defaultdict(list)
            for item in self._queue:
                if item.request_id in self._cancel:
                    continue
                by_group[item.group].append(item)

            remaining: list[QueuedInference] = []
            for group_name, items in by_group.items():
                group = self.groups[group_name]
                capacity = group.limit
                if group.fair and len(items) > 1:
                    # Round-robin from a per-group cursor across tenants/subjects.
                    buckets: dict[str, deque[QueuedInference]] = defaultdict(deque)
                    order_keys: list[str] = []
                    for item in items:
                        key = item.tenant_id or item.auth_subject or item.request_id
                        if key not in buckets:
                            order_keys.append(key)
                        buckets[key].append(item)
                    cursor = self._fair_cursor[group_name] % max(1, len(order_keys))
                    fair_items: list[QueuedInference] = []
                    while any(buckets.values()):
                        key = order_keys[cursor % len(order_keys)]
                        cursor += 1
                        if buckets[key]:
                            fair_items.append(buckets[key].popleft())
                    self._fair_cursor[group_name] = cursor
                    items = fair_items

                for item in items:
                    if self._inflight[group_name] >= capacity:
                        remaining.append(item)
                        continue
                    handle = self._submit(item, backend=backend)
                    self._inflight[group_name] += 1
                    self._inflight_ids[group_name].append(item.request_id)
                    self._request_jobs[item.request_id] = handle.job_id
                    self._request_groups[item.request_id] = group_name
                    self._request_auth[item.request_id] = (item.auth_subject, item.tenant_id)
                    queue_ms = (time.monotonic() - item.enqueued_at) * 1000.0
                    self._diagnostics[item.request_id] = InferenceDiagnostics(
                        request_id=item.request_id,
                        group=group_name,
                        queue_ms=queue_ms,
                    )
                    started.append((item, handle))
            self._queue = remaining
        return started

    def form_batch(
        self, items: Sequence[QueuedInference], *, now: float | None = None
    ) -> list[tuple[str, list[QueuedInference]]]:
        """Group compatible shapes within the configured batch window.

        Flushes when ``max_size`` is reached, when the oldest member has waited
        at least ``max_wait_ms`` (only when ``enqueued_at`` is set), or when
        flushing the trailing remainder of a one-shot call.
        """
        if self.batch is None:
            return [(f"solo-{it.request_id}", [it]) for it in items]
        clock = time.monotonic() if now is None else now
        max_wait = self.batch.max_wait_ms / 1000.0
        buckets: dict[str, list[QueuedInference]] = defaultdict(list)
        for item in items:
            buckets[item.shape_key].append(item)
        batches: list[tuple[str, list[QueuedInference]]] = []
        batch_seq = 0

        def _flush(shape: str, chunk: list[QueuedInference]) -> None:
            nonlocal batch_seq
            batch_seq += 1
            batch_id = f"batch-{shape}-{batch_seq}"
            for member in chunk:
                diag = self._diagnostics.get(member.request_id)
                if diag is not None:
                    self._diagnostics[member.request_id] = InferenceDiagnostics(
                        request_id=diag.request_id,
                        group=diag.group,
                        queue_ms=diag.queue_ms,
                        execute_ms=diag.execute_ms,
                        batch_id=batch_id,
                        batch_size=len(chunk),
                        cancelled=diag.cancelled,
                        overload=diag.overload,
                    )
            batches.append((batch_id, chunk))

        for shape, group_items in buckets.items():
            pending: list[QueuedInference] = []
            for item in group_items:
                pending.append(item)
                oldest = pending[0].enqueued_at
                waited_out = oldest > 0.0 and (clock - oldest) >= max_wait
                if len(pending) >= self.batch.max_size or waited_out:
                    _flush(shape, pending)
                    pending = []
            if pending:
                _flush(shape, pending)
        return batches

    def release(self, group: str, *, count: int = 1, request_id: str | None = None) -> None:
        with self._lock:
            self._inflight[group] = max(0, self._inflight[group] - count)
            if request_id is not None:
                self._drop_inflight_id(group, request_id)
                self._forget_request_maps(request_id)
                return
            for _ in range(max(0, count)):
                pending = self._inflight_ids.get(group)
                if not pending:
                    break
                self._forget_request_maps(pending.popleft())

    def queue_status(self) -> list[InferenceQueueStatus]:
        with self._lock:
            out: list[InferenceQueueStatus] = []
            for i, item in enumerate(self._queue):
                out.append(
                    InferenceQueueStatus(
                        request_id=item.request_id,
                        admission=InferenceAdmission.QUEUED,
                        position=i,
                        queue_size=len(self._queue),
                        eta_seconds=(i + 1) * self.default_eta_per_item,
                        group=item.group,
                    )
                )
            return out

    def diagnostics_for(self, request_id: str) -> InferenceDiagnostics | None:
        with self._lock:
            return self._diagnostics.get(request_id)

    def stream_progress(
        self,
        values: Iterator[Any],
        *,
        request_id: str,
        on_chunk: Callable[[Any], None] | None = None,
    ) -> list[Any]:
        """Consume a generator while honoring cancellation (INFER-018)."""
        chunks: list[Any] = []
        for value in values:
            if self.is_cancelled(request_id):
                raise InferenceError(
                    "Inference cancelled during streaming",
                    code=HED_INFER_0003,
                    diagnostic=error(
                        HED_INFER_0003,
                        title="Inference cancelled",
                        explanation=f"Request {request_id!r} was cancelled.",
                        remediation="Stop emitting chunks and clean up artifacts.",
                    ),
                )
            chunks.append(value)
            if on_chunk is not None:
                on_chunk(value)
        return chunks

    def _submit(self, item: QueuedInference, *, backend: JobBackend | None) -> JobHandle:
        job_backend = backend or get_job_backend()
        return job_backend.submit(
            item.job_type,
            dict(item.payload),
            tenant_id=item.tenant_id,
            auth_subject=item.auth_subject,
        )

    def _forget_request_maps(self, request_id: str) -> None:
        self._diagnostics.pop(request_id, None)
        self._request_jobs.pop(request_id, None)
        self._request_auth.pop(request_id, None)
        self._request_groups.pop(request_id, None)

    def _drop_inflight_id(self, group: str, request_id: str) -> None:
        pending = self._inflight_ids.get(group)
        if not pending:
            return
        try:
            pending.remove(request_id)
        except ValueError:
            return

    def _mark_cancel_id(self, request_id: str) -> None:
        now = time.monotonic()
        self._prune_cancelled(now)
        self._cancel[request_id] = now
        self._cancel.move_to_end(request_id)
        while len(self._cancel) > self.max_cancelled:
            self._cancel.popitem(last=False)

    def _prune_cancelled(self, now: float) -> None:
        expired = [
            key
            for key, stamped in self._cancel.items()
            if now - stamped > self.cancel_ttl_seconds
        ]
        for key in expired:
            del self._cancel[key]


@dataclass
class InProcessInferenceQueue:
    """Development-only in-process queue. Not a production durability promise."""

    policy: InferencePolicy
    _pending: deque[QueuedInference] = field(default_factory=deque)

    def __post_init__(self) -> None:
        if not self.policy.development_in_process:
            raise InferenceError(
                "InProcessInferenceQueue requires development_in_process=True",
                code=HED_INFER_0001,
            )

    def enqueue(self, item: QueuedInference) -> None:
        self._pending.append(item)

    def pop(self) -> QueuedInference | None:
        if not self._pending:
            return None
        return self._pending.popleft()
