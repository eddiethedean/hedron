"""Nested monotonic request resource budget ledger (BUDGET-056)."""

from __future__ import annotations

import contextvars
from dataclasses import dataclass, field


class BudgetExceeded(ValueError):
    """Raised when a request budget dimension is exceeded."""

    def __init__(self, dimension: str, limit: int, used: int) -> None:
        self.dimension = dimension
        self.limit = limit
        self.used = used
        super().__init__(f"request budget exceeded: {dimension} used={used} limit={limit}")


@dataclass(frozen=True, slots=True)
class RequestBudgetLimits:
    request_line_bytes: int = 8_192
    header_bytes: int = 32_768
    body_bytes: int = 1_048_576
    decompressed_bytes: int = 2_097_152
    multipart_parts: int = 64
    json_nodes: int = 10_000
    form_fields: int = 1_024
    concurrency: int = 32
    deadline_seconds: int = 60
    response_bytes: int = 5_242_880
    sse_events: int = 10_000
    websocket_messages: int = 10_000


@dataclass
class RequestBudget:
    """Monotonic nested ledger. Child views cannot reset parent counters."""

    limits: RequestBudgetLimits = field(default_factory=RequestBudgetLimits)
    _used: dict[str, int] = field(default_factory=dict)
    _parent: RequestBudget | None = None
    _closed: bool = False

    def _root(self) -> RequestBudget:
        node: RequestBudget = self
        while node._parent is not None:
            node = node._parent
        return node

    def used(self, dimension: str) -> int:
        return self._root()._used.get(dimension, 0)

    def remaining(self, dimension: str) -> int:
        limit = getattr(self.limits, dimension)
        return max(0, int(limit) - self.used(dimension))

    def charge(self, dimension: str, amount: int = 1) -> None:
        if amount < 0:
            raise ValueError("budget charge amount must be non-negative")
        if self._closed:
            raise BudgetExceeded(dimension, 0, self.used(dimension))
        root = self._root()
        limit = int(getattr(self.limits, dimension))
        next_used = root._used.get(dimension, 0) + amount
        if next_used > limit:
            raise BudgetExceeded(dimension, limit, next_used)
        root._used[dimension] = next_used

    def child(self) -> RequestBudget:
        """Nested view that shares the parent ledger and cannot loosen limits."""
        child_limits = RequestBudgetLimits(
            **{
                name: min(getattr(self.limits, name), getattr(self.limits, name))
                for name in RequestBudgetLimits.__dataclass_fields__
            }
        )
        return RequestBudget(limits=child_limits, _parent=self._root())

    def close(self) -> None:
        self._closed = True

    def snapshot(self) -> dict[str, int]:
        return dict(self._root()._used)


_current_budget: contextvars.ContextVar[RequestBudget | None] = contextvars.ContextVar(
    "hedron_request_budget", default=None
)


def get_request_budget() -> RequestBudget | None:
    return _current_budget.get()


def set_request_budget(budget: RequestBudget | None) -> contextvars.Token[RequestBudget | None]:
    return _current_budget.set(budget)


def reset_request_budget(token: contextvars.Token[RequestBudget | None]) -> None:
    _current_budget.reset(token)


def require_request_budget() -> RequestBudget:
    budget = get_request_budget()
    if budget is None:
        raise BudgetExceeded("ledger", 0, 0)
    return budget


# Default ceilings locked for PERF-056 evidence.
PERF_CEILINGS = {
    "policy_overhead_ms_p95": 5.0,
    "streaming_peak_memory_mb": 64.0,
    "metadata_retention_entries": 10_000,
    "event_cardinality_labels": 32,
    "max_concurrency": 32,
    "adversarial_body_reject_ms_p95": 50.0,
}
