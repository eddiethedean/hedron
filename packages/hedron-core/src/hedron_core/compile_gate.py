"""Production compile gates for mutable build inputs such as scoped CSS."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from hedron_core.codes import HED_BUILD_RUNTIME_COMPILE
from hedron_core.diagnostics import error

__all__ = [
    "assert_runtime_compile_allowed",
    "force_runtime_compile",
    "is_production_env",
    "set_runtime_compile_allowed",
]

# Process-wide flag flipped by production lifespan. Build/CLI force-allow via context.
_process_allow_runtime_compile: bool = True
_force_allow: ContextVar[bool] = ContextVar("hedron_force_runtime_compile", default=False)


def is_production_env(*, production: bool | None = None) -> bool:
    if production is not None:
        return production
    return os.environ.get("HEDRON_ENV", "").lower() in {"prod", "production"}


def set_runtime_compile_allowed(allowed: bool) -> None:
    """Process-wide allow/deny for runtime build-input compilation."""
    global _process_allow_runtime_compile
    _process_allow_runtime_compile = allowed


@contextmanager
def force_runtime_compile() -> Iterator[None]:
    """Temporarily allow compile APIs (e.g. ``hedron build`` under HEDRON_ENV=production)."""
    token = _force_allow.set(True)
    try:
        yield
    finally:
        _force_allow.reset(token)


def assert_runtime_compile_allowed(
    *, production: bool | None = None, what: str = "CSS"
) -> None:
    if _force_allow.get():
        return
    if production is False:
        return
    blocked = production is True or not _process_allow_runtime_compile or is_production_env()
    if blocked:
        raise error(
            HED_BUILD_RUNTIME_COMPILE,
            title="Runtime compilation disabled in production",
            explanation=(
                f"Production mode forbids runtime {what} compilation. "
                "Load versioned build artifacts instead."
            ),
            remediation="Run `hedron build` and load programs/styles from the build manifest.",
        )


def production_compile_guard(fn: Any) -> Any:
    """Decorator that rejects compile helpers under production env."""

    def wrapped(*args: Any, **kwargs: Any) -> Any:
        assert_runtime_compile_allowed()
        return fn(*args, **kwargs)

    wrapped.__name__ = getattr(fn, "__name__", "wrapped")
    wrapped.__doc__ = getattr(fn, "__doc__", None)
    return wrapped
