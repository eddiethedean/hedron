"""Unified server-first interaction lifecycle for phase 0.61.

The values in this module are projections over existing Hedron actions, forms,
jobs, and fragments.  They are intentionally immutable and do not provide a
durable browser store or a second mutation authority.
"""

from __future__ import annotations

import math
import time
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any, Literal, cast

from hedron_core.compat import StrEnum
from hedron_core.security.secrets import redact_secret_like

__all__ = [
    "ActionPhase",
    "ActionPolicy",
    "ActionState",
    "ActionTransitionError",
    "AsyncPhase",
    "ActionTrace",
    "OperationIdentity",
    "TraceEvent",
    "begin_operation",
    "complete_operation",
    "transition_action",
]


class ActionPhase(StrEnum):
    """Closed lifecycle vocabulary shared by supported async interactions."""

    IDLE = "idle"
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"
    STALE = "stale"
    CONFLICT = "conflict"


AsyncPhase = Literal[
    "idle",
    "pending",
    "success",
    "error",
    "cancelled",
    "stale",
    "conflict",
    "empty",
    "timeout",
]

_TERMINAL = frozenset(
    {
        ActionPhase.SUCCESS,
        ActionPhase.ERROR,
        ActionPhase.CANCELLED,
        ActionPhase.STALE,
        ActionPhase.CONFLICT,
    }
)
_TRANSITIONS: dict[ActionPhase, frozenset[ActionPhase]] = {
    ActionPhase.IDLE: frozenset({ActionPhase.PENDING}),
    ActionPhase.PENDING: _TERMINAL,
    ActionPhase.ERROR: frozenset({ActionPhase.PENDING}),
    ActionPhase.CANCELLED: frozenset({ActionPhase.PENDING}),
    ActionPhase.STALE: frozenset({ActionPhase.PENDING}),
    ActionPhase.CONFLICT: frozenset({ActionPhase.PENDING}),
    ActionPhase.SUCCESS: frozenset({ActionPhase.PENDING}),
}


def _require_int(name: str, value: object, *, minimum: int, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if value < minimum or (maximum is not None and value > maximum):
        bound = (
            f" between {minimum} and {maximum}" if maximum is not None else f" at least {minimum}"
        )
        raise ValueError(f"{name} must be{bound}")
    return value


@dataclass(frozen=True, slots=True)
class OperationIdentity:
    """Stable identity for one server-authorized operation attempt."""

    operation_id: str
    generation: int = 0
    target: str | None = None
    correlation_id: str | None = None
    attempt: int = 0
    revision: str | int | None = None

    def __post_init__(self) -> None:
        if not self.operation_id or len(self.operation_id) > 128:
            raise ValueError("operation_id must be non-empty and at most 128 characters")
        _require_int("generation", self.generation, minimum=0)
        _require_int("attempt", self.attempt, minimum=0)
        for name in ("target", "correlation_id"):
            value = getattr(self, name)
            if value is not None and (not value or len(value) > 512):
                raise ValueError(f"{name} must be non-empty and at most 512 characters")

    def next_generation(self, *, attempt: int | None = None) -> OperationIdentity:
        """Return a new generation without mutating the current operation."""
        return replace(
            self,
            generation=self.generation + 1,
            attempt=self.attempt + 1 if attempt is None else attempt,
        )

    def to_dict(self) -> dict[str, object]:
        """Return the non-authoritative, JSON-compatible identity projection."""
        return {
            "operation_id": self.operation_id,
            "generation": self.generation,
            "target": self.target,
            "correlation_id": self.correlation_id,
            "attempt": self.attempt,
            "revision": self.revision,
        }


@dataclass(frozen=True, slots=True)
class ActionPolicy:
    """Explicit concurrency and retry policy for one operation family."""

    concurrency: Literal["drop", "replace", "queue"] = "drop"
    allow_retry: bool = False
    max_attempts: int = 1
    allow_cancellation: bool = True
    timeout_seconds: float | None = None
    idempotent: bool = False

    def __post_init__(self) -> None:
        timeout_seconds = cast(object, self.timeout_seconds)
        if self.concurrency not in {"drop", "replace", "queue"}:
            raise ValueError("concurrency must be 'drop', 'replace', or 'queue'")
        _require_int("max_attempts", self.max_attempts, minimum=1)
        if timeout_seconds is not None and (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(float(timeout_seconds))
            or timeout_seconds <= 0
        ):
            raise ValueError("timeout_seconds must be finite and positive when provided")
        if self.allow_retry and self.max_attempts < 2:
            raise ValueError("allow_retry requires max_attempts >= 2")
        if self.allow_retry and not self.idempotent:
            raise ValueError("retry requires an explicitly idempotent operation")

    def to_dict(self) -> dict[str, object]:
        """Return the explicit policy used by an adapter or diagnostic."""
        return {
            "concurrency": self.concurrency,
            "allow_retry": self.allow_retry,
            "max_attempts": self.max_attempts,
            "allow_cancellation": self.allow_cancellation,
            "timeout_seconds": self.timeout_seconds,
            "idempotent": self.idempotent,
        }


@dataclass(frozen=True, slots=True)
class ActionState:
    """Immutable projection of the current operation state."""

    phase: ActionPhase = ActionPhase.IDLE
    operation: OperationIdentity | None = None
    message: str | None = None
    retryable: bool = False
    progress: int | None = None
    revision: str | int | None = None
    _deadline_at: float | None = field(default=None, repr=False, compare=False)
    _policy: ActionPolicy | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        # Keep the runtime representation canonical even when a host or
        # adapter supplies the wire value as a plain string.
        object.__setattr__(self, "phase", ActionPhase(self.phase))
        if self.message is not None and len(self.message) > 512:
            raise ValueError("public action messages are limited to 512 characters")
        if self.progress is not None and not 0 <= self.progress <= 100:
            raise ValueError("progress must be between 0 and 100")
        if self.phase is ActionPhase.PENDING and self.operation is None:
            raise ValueError("pending state requires an operation identity")
        if self.retryable and self.phase is not ActionPhase.ERROR:
            raise ValueError("only error states may be retryable")

    @property
    def terminal(self) -> bool:
        return self.phase in _TERMINAL

    @property
    def busy(self) -> bool:
        return self.phase is ActionPhase.PENDING

    @property
    def deadline_at(self) -> float | None:
        """Return the internal monotonic deadline for lifecycle helpers."""
        return self._deadline_at

    @property
    def policy(self) -> ActionPolicy | None:
        """Return the policy retained for lifecycle completion."""
        return self._policy

    def to_dict(self) -> dict[str, object]:
        """Return the bounded public lifecycle projection."""
        return {
            "schema": "hedron.action-state.v1",
            "phase": self.phase.value,
            "operation": self.operation.to_dict() if self.operation else None,
            "message": self.message,
            "retryable": self.retryable,
            "progress": self.progress,
            "revision": self.revision,
        }


class ActionTransitionError(ValueError):
    """Raised when a lifecycle transition would violate the phase contract."""


def transition_action(
    state: ActionState,
    phase: ActionPhase | str,
    *,
    operation: OperationIdentity | None = None,
    message: str | None = None,
    retryable: bool = False,
    progress: int | None = None,
    revision: str | int | None = None,
) -> ActionState:
    """Apply one explicit lifecycle transition."""

    next_phase = ActionPhase(phase)
    if next_phase not in _TRANSITIONS[state.phase]:
        raise ActionTransitionError(f"cannot transition {state.phase.value} -> {next_phase.value}")
    if next_phase is ActionPhase.PENDING and operation is None:
        raise ActionTransitionError("pending transition requires an operation identity")
    if next_phase in _TERMINAL and operation is None:
        operation = state.operation
    if next_phase in _TERMINAL and state.operation is not None and operation is not None:
        if operation.operation_id != state.operation.operation_id:
            raise ActionTransitionError("terminal result operation does not match current state")
        if operation.generation < state.operation.generation:
            raise ActionTransitionError("terminal result belongs to a stale generation")
    return ActionState(
        phase=next_phase,
        operation=operation,
        message=message,
        retryable=retryable,
        progress=progress,
        revision=revision,
    )


def begin_operation(
    state: ActionState,
    operation: OperationIdentity,
    *,
    policy: ActionPolicy | None = None,
) -> tuple[ActionState, bool]:
    """Start an operation, returning ``(state, accepted)``.

    ``drop`` and ``queue`` reject a second pending operation at this layer;
    queue scheduling belongs to the host. ``replace`` starts the new generation.
    """

    resolved_policy = policy or ActionPolicy()
    if state.busy and resolved_policy.concurrency in {"drop", "queue"}:
        return state, False
    same_operation = (
        state.operation is not None and operation.operation_id == state.operation.operation_id
    )
    if state.phase is ActionPhase.ERROR and same_operation:
        if not resolved_policy.allow_retry:
            return state, False
        current_attempt = state.operation.attempt if state.operation else 0
        if current_attempt + 1 >= resolved_policy.max_attempts:
            return state, False
    if (
        state.operation is not None
        and operation.operation_id == state.operation.operation_id
        and operation.generation <= state.operation.generation
    ):
        operation = operation.next_generation()
    return (
        ActionState(
            phase=ActionPhase.PENDING,
            operation=operation,
            revision=operation.revision,
            _deadline_at=(
                time.monotonic() + resolved_policy.timeout_seconds
                if resolved_policy.timeout_seconds is not None
                else None
            ),
            _policy=resolved_policy,
        ),
        True,
    )


def complete_operation(
    state: ActionState,
    phase: ActionPhase | str,
    operation: OperationIdentity,
    *,
    policy: ActionPolicy | None = None,
    message: str | None = None,
    retryable: bool = False,
    progress: int | None = None,
    revision: str | int | None = None,
) -> tuple[ActionState, bool]:
    """Apply a result only when it belongs to the current operation generation.

    A stale result is observable through the returned ``False`` value and must
    be recorded in a trace, but it never replaces the current presentation.
    """

    if state.operation is None or state.operation.operation_id != operation.operation_id:
        return state, False
    if operation.generation != state.operation.generation:
        return state, False
    if operation.target != state.operation.target:
        return state, False
    if operation.correlation_id != state.operation.correlation_id:
        return state, False
    if operation.revision != state.operation.revision:
        return state, False
    resolved_policy = policy or state.policy
    if state.deadline_at is not None and time.monotonic() > state.deadline_at:
        return (
            replace(
                state,
                phase=ActionPhase.ERROR,
                message="Operation timed out",
                retryable=resolved_policy.allow_retry if resolved_policy is not None else False,
                _deadline_at=None,
            ),
            True,
        )
    next_phase = ActionPhase(phase)
    if (
        next_phase is ActionPhase.CANCELLED
        and resolved_policy is not None
        and not resolved_policy.allow_cancellation
    ):
        return state, False
    try:
        return (
            transition_action(
                state,
                phase,
                operation=operation,
                message=message,
                retryable=retryable,
                progress=progress,
                revision=revision,
            ),
            True,
        )
    except ActionTransitionError:
        return state, False


@dataclass(frozen=True, slots=True)
class TraceEvent:
    """One bounded, redacted lifecycle fact."""

    phase: str
    operation_id: str | None = None
    generation: int | None = None
    target: str | None = None
    status: int | None = None
    facts: Mapping[str, object] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True, slots=True)
class ActionTrace:
    """Immutable bounded trace suitable for tests, Explorer, and diagnostics."""

    events: tuple[TraceEvent, ...] = ()
    max_events: int = 128
    max_fact_chars: int = 512

    def __post_init__(self) -> None:
        _require_int("max_events", self.max_events, minimum=1, maximum=10_000)
        _require_int("max_fact_chars", self.max_fact_chars, minimum=32)
        if len(self.events) > self.max_events:
            raise ValueError("trace exceeds max_events")

    def append(
        self,
        phase: ActionPhase | str,
        *,
        operation: OperationIdentity | None = None,
        status: int | None = None,
        facts: Mapping[str, object] | None = None,
    ) -> ActionTrace:
        """Return a new trace with redacted, bounded facts."""

        clean: dict[str, object] = {}
        for key, value in (facts or {}).items():
            redacted = redact_secret_like({str(key): value})[str(key)]
            if isinstance(redacted, str):
                clean[str(key)] = redacted[: self.max_fact_chars]
            else:
                clean[str(key)] = redacted
        event = TraceEvent(
            phase=ActionPhase(phase).value,
            operation_id=operation.operation_id if operation else None,
            generation=operation.generation if operation else None,
            target=operation.target if operation else None,
            status=status,
            facts=MappingProxyType(clean),
        )
        events = (*self.events, event)
        if len(events) > self.max_events:
            events = events[-self.max_events :]
        return replace(self, events=events)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible redacted representation."""

        return {
            "schema": "hedron.interaction-trace.v1",
            "events": [
                {
                    "phase": event.phase,
                    "operation_id": event.operation_id,
                    "generation": event.generation,
                    "target": event.target,
                    "status": event.status,
                    "facts": dict(event.facts),
                }
                for event in self.events
            ],
        }
