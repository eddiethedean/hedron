"""Localized failure boundaries for declared server-rendered regions (0.62)."""

from __future__ import annotations

from dataclasses import dataclass, replace

from hedron_core.action_state import OperationIdentity
from hedron_core.compat import StrEnum

__all__ = [
    "BoundaryDecision",
    "BoundaryPhase",
    "FailureBoundary",
    "FailureDisposition",
]


class BoundaryPhase(StrEnum):
    HEALTHY = "healthy"
    PENDING = "pending"
    RETRYABLE_ERROR = "retryable_error"
    DEGRADED = "degraded"
    FATAL = "fatal"


class FailureDisposition(StrEnum):
    LOCAL = "local"
    RECONCILE = "reconcile"
    PROPAGATE = "propagate"


@dataclass(frozen=True, slots=True)
class BoundaryDecision:
    accepted: bool
    boundary: FailureBoundary
    reason: str
    disposition: FailureDisposition
    diagnostic_code: str | None = None


@dataclass(frozen=True, slots=True)
class FailureBoundary:
    """Immutable lifecycle for one declared failure target."""

    boundary_id: str
    target: str
    has_fallback: bool = True
    max_retries: int = 2
    phase: BoundaryPhase = BoundaryPhase.HEALTHY
    attempt: int = 0
    operation: OperationIdentity | None = None

    def __post_init__(self) -> None:
        if not self.boundary_id or not self.target:
            raise ValueError("boundary_id and target are required")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        if self.attempt < 0:
            raise ValueError("attempt cannot be negative")

    def start(self, operation: OperationIdentity) -> BoundaryDecision:
        if not self.has_fallback:
            return BoundaryDecision(
                False,
                self,
                "missing_fallback",
                FailureDisposition.PROPAGATE,
                "HED-FAILURE-0001",
            )
        if operation.target not in {None, self.target}:
            return BoundaryDecision(
                False,
                self,
                "target_mismatch",
                FailureDisposition.PROPAGATE,
                "HED-IDENTITY-0003",
            )
        next_boundary = replace(self, phase=BoundaryPhase.PENDING, operation=operation)
        return BoundaryDecision(True, next_boundary, "pending", FailureDisposition.LOCAL)

    def complete(
        self,
        operation: OperationIdentity,
        *,
        success: bool,
        retryable: bool = False,
        uncertain: bool = False,
        fatal: bool = False,
    ) -> BoundaryDecision:
        if self.phase is not BoundaryPhase.PENDING or self.operation != operation:
            return BoundaryDecision(
                False,
                self,
                "stale_or_duplicate",
                FailureDisposition.LOCAL,
                "HED-FAILURE-0005",
            )
        if success:
            return BoundaryDecision(
                True,
                replace(self, phase=BoundaryPhase.HEALTHY),
                "success",
                FailureDisposition.LOCAL,
            )
        if uncertain:
            next_boundary = replace(self, phase=BoundaryPhase.DEGRADED)
            return BoundaryDecision(
                True,
                next_boundary,
                "uncertain_outcome",
                FailureDisposition.RECONCILE,
                "HED-FAILURE-0004",
            )
        if fatal:
            next_boundary = replace(self, phase=BoundaryPhase.FATAL)
            return BoundaryDecision(
                True, next_boundary, "fatal", FailureDisposition.PROPAGATE, "HED-FAILURE-0003"
            )
        next_phase = (
            BoundaryPhase.RETRYABLE_ERROR
            if retryable and self.attempt < self.max_retries
            else BoundaryPhase.DEGRADED
        )
        disposition = (
            FailureDisposition.LOCAL if self.has_fallback else FailureDisposition.PROPAGATE
        )
        return BoundaryDecision(
            True, replace(self, phase=next_phase), "error", disposition, "HED-FAILURE-0002"
        )

    def retry(self, operation: OperationIdentity) -> BoundaryDecision:
        if self.phase is not BoundaryPhase.RETRYABLE_ERROR:
            return BoundaryDecision(
                False, self, "retry_not_allowed", FailureDisposition.LOCAL, "HED-FAILURE-0006"
            )
        if self.attempt >= self.max_retries:
            return BoundaryDecision(
                False, self, "retry_limit", FailureDisposition.LOCAL, "HED-FAILURE-0007"
            )
        next_operation = operation.next_generation()
        next_boundary = replace(
            self, phase=BoundaryPhase.PENDING, attempt=self.attempt + 1, operation=next_operation
        )
        return BoundaryDecision(True, next_boundary, "retry", FailureDisposition.LOCAL)
