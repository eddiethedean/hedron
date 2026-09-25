"""Nested monotonic request resource budget ledger (BUDGET-056)."""

from __future__ import annotations

import contextvars
from dataclasses import dataclass, field
from typing import Literal

BudgetDimension = Literal[
    "request_line_bytes",
    "header_bytes",
    "body_bytes",
    "decompressed_bytes",
    "multipart_parts",
    "json_nodes",
    "form_fields",
    "concurrency",
    "deadline_seconds",
    "response_bytes",
    "sse_events",
    "websocket_messages",
]


class BudgetExceeded(ValueError):
    """Raised when a request budget dimension is exceeded."""

    def __init__(self, dimension: str, limit: int, used: int) -> None:
        self.dimension = dimension
        self.limit = limit
        self.used = used
        super().__init__(f"request budget exceeded: {dimension} used={used} limit={limit}")


class BudgetMissing(RuntimeError):
    """Raised when a request budget ledger is required but not installed."""


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
    _used: dict[str, int] = field(default_factory=dict[str, int])
    _parent: RequestBudget | None = None
    _closed: bool = False

    def _root(self) -> RequestBudget:
        node: RequestBudget = self
        while node._parent is not None:
            node = node._parent
        return node

    def used(self, dimension: str) -> int:
        return self._root()._used.get(dimension, 0)

    def remaining(self, dimension: BudgetDimension) -> int:
        return max(0, _limit_value(self.limits, dimension) - self.used(dimension))

    def charge(self, dimension: BudgetDimension, amount: int = 1) -> None:
        if amount < 0:
            raise ValueError("budget charge amount must be non-negative")
        root = self._root()
        if root._closed:
            raise BudgetExceeded(dimension, 0, self.used(dimension))
        limit = _limit_value(self.limits, dimension)
        next_used = root._used.get(dimension, 0) + amount
        if next_used > limit:
            raise BudgetExceeded(dimension, limit, next_used)
        root._used[dimension] = next_used

    def child(self, limits: RequestBudgetLimits | None = None) -> RequestBudget:
        """Nested view that shares the parent ledger and cannot loosen limits."""
        parent_limits = self.limits
        if limits is None:
            child_limits = parent_limits
        else:
            child_limits = RequestBudgetLimits(
                request_line_bytes=min(parent_limits.request_line_bytes, limits.request_line_bytes),
                header_bytes=min(parent_limits.header_bytes, limits.header_bytes),
                body_bytes=min(parent_limits.body_bytes, limits.body_bytes),
                decompressed_bytes=min(parent_limits.decompressed_bytes, limits.decompressed_bytes),
                multipart_parts=min(parent_limits.multipart_parts, limits.multipart_parts),
                json_nodes=min(parent_limits.json_nodes, limits.json_nodes),
                form_fields=min(parent_limits.form_fields, limits.form_fields),
                concurrency=min(parent_limits.concurrency, limits.concurrency),
                deadline_seconds=min(parent_limits.deadline_seconds, limits.deadline_seconds),
                response_bytes=min(parent_limits.response_bytes, limits.response_bytes),
                sse_events=min(parent_limits.sse_events, limits.sse_events),
                websocket_messages=min(parent_limits.websocket_messages, limits.websocket_messages),
            )
        return RequestBudget(limits=child_limits, _parent=self._root())

    def close(self) -> None:
        self._root()._closed = True

    def snapshot(self) -> dict[str, int]:
        return dict(self._root()._used)


def _limit_value(limits: RequestBudgetLimits, dimension: BudgetDimension) -> int:
    match dimension:
        case "request_line_bytes":
            return limits.request_line_bytes
        case "header_bytes":
            return limits.header_bytes
        case "body_bytes":
            return limits.body_bytes
        case "decompressed_bytes":
            return limits.decompressed_bytes
        case "multipart_parts":
            return limits.multipart_parts
        case "json_nodes":
            return limits.json_nodes
        case "form_fields":
            return limits.form_fields
        case "concurrency":
            return limits.concurrency
        case "deadline_seconds":
            return limits.deadline_seconds
        case "response_bytes":
            return limits.response_bytes
        case "sse_events":
            return limits.sse_events
        case "websocket_messages":
            return limits.websocket_messages


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
        raise BudgetMissing("request budget ledger is not installed")
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
