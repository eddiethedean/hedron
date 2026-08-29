"""Framework-neutral request context bridge for portable integrations."""

from __future__ import annotations

from contextvars import ContextVar

current_request: ContextVar[object | None] = ContextVar("hedron_current_request", default=None)

__all__ = ["current_request"]
