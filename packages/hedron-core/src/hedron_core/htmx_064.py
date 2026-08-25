"""Framework-neutral lifecycle facts projected by ``htmx-ext-hedron``.

This module is the server-side contract for the browser asset.  It does not
own requests or authorization; it only validates bounded presentation choices
and provides deterministic state transitions for tests and integrations.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

__all__ = [
    "HEDRON_LIFECYCLE_SCHEMA",
    "HedronLifecycleEvent",
    "LifecycleFact",
    "LifecyclePolicy",
    "LifecycleState",
    "lifecycle_attributes",
    "transition_lifecycle",
]

HEDRON_LIFECYCLE_SCHEMA: Final = "hedron.htmx-lifecycle/1"
_IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,95}$")


class LifecycleState(StrEnum):
    IDLE = "idle"
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"
    ABORTED = "aborted"
    STALE = "stale"
    SUPERSEDED = "superseded"


class LifecyclePolicy(StrEnum):
    LATEST = "latest"
    REPLACE = "replace"
    QUEUE = "queue"
    DROP = "drop"


class HedronLifecycleEvent(StrEnum):
    REQUEST = "request"
    SUCCESS = "success"
    ERROR = "error"
    ABORT = "abort"
    SWAP = "swap"
    SETTLE = "settle"
    CLEANUP = "cleanup"


@dataclass(frozen=True, slots=True)
class LifecycleFact:
    """A redacted, bounded lifecycle fact suitable for DOM markers or traces."""

    state: LifecycleState
    generation: int = 0
    operation_id: str | None = None
    event: HedronLifecycleEvent | None = None

    def __post_init__(self) -> None:
        if self.generation < 0:
            raise ValueError("lifecycle generation must be non-negative")
        if self.operation_id is not None and _IDENTIFIER.fullmatch(self.operation_id) is None:
            raise ValueError("operation_id must be a bounded identifier")

    def markers(self) -> Mapping[str, str]:
        values = {
            "data-hedron-state": self.state.value,
            "data-hedron-generation": str(self.generation),
        }
        if self.operation_id:
            values["data-hedron-operation"] = self.operation_id
        return values

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": HEDRON_LIFECYCLE_SCHEMA,
            "state": self.state.value,
            "generation": self.generation,
            "operation_id": self.operation_id,
            "event": self.event.value if self.event else None,
        }

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(
            json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


def transition_lifecycle(
    current: LifecycleFact,
    event: HedronLifecycleEvent,
    *,
    generation: int | None = None,
    operation_id: str | None = None,
) -> LifecycleFact:
    """Apply one bounded event, ignoring an older generation as ``stale``."""
    next_generation = current.generation if generation is None else generation
    if next_generation < current.generation:
        return LifecycleFact(
            LifecycleState.STALE,
            generation=next_generation,
            operation_id=operation_id or current.operation_id,
            event=event,
        )
    if event is HedronLifecycleEvent.REQUEST:
        state = LifecycleState.PENDING
    elif event is HedronLifecycleEvent.SUCCESS:
        state = LifecycleState.SUCCESS
    elif event is HedronLifecycleEvent.ERROR:
        state = LifecycleState.ERROR
    elif event is HedronLifecycleEvent.ABORT:
        state = LifecycleState.ABORTED
    elif event is HedronLifecycleEvent.CLEANUP:
        state = LifecycleState.IDLE
    else:
        state = current.state
    return LifecycleFact(
        state,
        generation=next_generation,
        operation_id=operation_id or current.operation_id,
        event=event,
    )


def lifecycle_attributes(
    *,
    concurrency: LifecyclePolicy | str = LifecyclePolicy.LATEST,
    focus: str = "none",
    announcement: str = "polite",
) -> dict[str, str]:
    """Return validated opt-in attributes for a lifecycle host."""
    try:
        policy = LifecyclePolicy(concurrency)
    except ValueError as exc:
        raise ValueError("concurrency must be latest, replace, queue, or drop") from exc
    if focus not in {"none", "success", "error", "validation"}:
        raise ValueError("focus must be none, success, error, or validation")
    if announcement not in {"none", "polite", "assertive"}:
        raise ValueError("announcement must be none, polite, or assertive")
    return {
        "data-hedron-state-host": "true",
        "data-hedron-concurrency": policy.value,
        "data-hedron-focus": focus,
        "data-hedron-announcement": announcement,
    }
