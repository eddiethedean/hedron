"""Development-only in-process inference queue."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from hedron_core.codes import HED_INFER_0001
from hedron_core.inference.policy import InferencePolicy
from hedron_core.inference.types import InferenceError, QueuedInference


@dataclass
class InProcessInferenceQueue:
    """Development-only in-process queue. Not a production durability promise.

    ``InferenceScheduler`` implementation over the configured ``JobBackend``
    (via ``InferencePolicy``) for local admission tests.
    """

    policy: InferencePolicy
    _pending: deque[QueuedInference] = field(default_factory=deque[QueuedInference])

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
