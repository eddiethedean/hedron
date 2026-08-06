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
from collections import defaultdict, deque
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
    _inflight: dict[str, int] = field(default_factory=lambda: defaultdict(int), init=False)
    _queue: list[QueuedInference] = field(default_factory=list, init=False)
    _lock: threading.RLock = field(default_factory=threading.RLock, init=False)
    _seq: Iterator[int] = field(default_factory=lambda: itertools.count(1), init=False, repr=False)
    _cancel: set[str] = field(default_factory=set, init=False)
    _diagnostics: dict[str, InferenceDiagnostics] = field(default_factory=dict, init=False)

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
                self._diagnostics[request_id] = InferenceDiagnostics(
                    request_id=request_id,
                    group=group,
                    queue_ms=0.0,
                    overload=True,
                )
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
            self._cancel.add(request_id)
            self._queue = [q for q in self._queue if q.request_id != request_id]
            diag = self._diagnostics.get(request_id)
            if diag is not None:
                self._diagnostics[request_id] = InferenceDiagnostics(
                    request_id=diag.request_id,
                    group=diag.group,
                    queue_ms=diag.queue_ms,
                    execute_ms=diag.execute_ms,
                    batch_id=diag.batch_id,
                    batch_size=diag.batch_size,
                    cancelled=True,
                    overload=diag.overload,
                )
            return True

    def is_cancelled(self, request_id: str) -> bool:
        with self._lock:
            return request_id in self._cancel

    def drain_ready(
        self, *, backend: JobBackend | None = None
    ) -> list[tuple[QueuedInference, JobHandle]]:
        """Promote queued items into free concurrency slots (fair within group)."""
        started: list[tuple[QueuedInference, JobHandle]] = []
        with self._lock:
            remaining: list[QueuedInference] = []
            for item in self._queue:
                if item.request_id in self._cancel:
                    continue
                capacity = self.groups[item.group].limit
                if self._inflight[item.group] >= capacity:
                    remaining.append(item)
                    continue
                handle = self._submit(item, backend=backend)
                self._inflight[item.group] += 1
                queue_ms = (time.monotonic() - item.enqueued_at) * 1000.0
                self._diagnostics[item.request_id] = InferenceDiagnostics(
                    request_id=item.request_id,
                    group=item.group,
                    queue_ms=queue_ms,
                )
                started.append((item, handle))
            self._queue = remaining
        return started

    def form_batch(
        self, items: Sequence[QueuedInference]
    ) -> list[tuple[str, list[QueuedInference]]]:
        """Group compatible shapes within the configured batch window."""
        if self.batch is None:
            return [(f"solo-{it.request_id}", [it]) for it in items]
        buckets: dict[str, list[QueuedInference]] = defaultdict(list)
        for item in items:
            buckets[item.shape_key].append(item)
        batches: list[tuple[str, list[QueuedInference]]] = []
        batch_seq = 0
        for shape, group_items in buckets.items():
            for i in range(0, len(group_items), self.batch.max_size):
                chunk = list(group_items[i : i + self.batch.max_size])
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
        return batches

    def release(self, group: str, *, count: int = 1) -> None:
        with self._lock:
            self._inflight[group] = max(0, self._inflight[group] - count)

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
