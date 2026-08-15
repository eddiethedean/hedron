"""Durability capability for job and cache backends."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = ["ProcessLocalBackend", "is_process_local"]


@runtime_checkable
class ProcessLocalBackend(Protocol):
    """Implemented by backends that do not survive process boundaries."""

    @property
    def process_local(self) -> bool: ...


def is_process_local(backend: object) -> bool:
    """Return True when a backend is process-local (in-memory).

    Backends opt in with ``process_local = True``. Missing attribute is treated as
    durable so third-party Redis/Celery implementations keep working.
    """
    return bool(getattr(backend, "process_local", False))
