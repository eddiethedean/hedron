"""Graceful shutdown."""

from __future__ import annotations

from hedron.ops import ShutdownRegistry
from hedron_core.adapter import LifecycleResource


def test_graceful_shutdown_runs_callbacks() -> None:
    seen: list[str] = []
    reg = ShutdownRegistry()
    reg.register(LifecycleResource("cache", order=50), lambda: seen.append("cache"))
    reg.register(LifecycleResource("jobs", order=40), lambda: seen.append("jobs"))
    assert reg.shutdown() == ["cache", "jobs"]
    assert seen == ["cache", "jobs"]
