"""Inference admission types."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from hedron_core.diagnostics import HedronError
from hedron_core.typing_aliases import JsonValue


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
