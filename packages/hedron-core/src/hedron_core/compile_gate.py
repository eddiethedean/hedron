"""Production compile gates for mutable build inputs such as scoped CSS."""

from __future__ import annotations

import os
import threading
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

from hedron_core.codes import HED_BUILD_RUNTIME_COMPILE
from hedron_core.diagnostics import error

__all__ = [
    "assert_runtime_compile_allowed",
    "deny_runtime_compile",
    "force_runtime_compile",
    "is_production_env",
    "RuntimeCompilePolicy",
    "set_runtime_compile_allowed",
    "use_runtime_compile_policy",
]


@dataclass(slots=True)
class RuntimeCompilePolicy:
    """Application-owned permission for mutable runtime build inputs."""

    allowed: bool = True


# Compatibility fallback for core-only callers. Hedron applications bind an owned
# RuntimeCompilePolicy through their runtime context.
_process_allow_runtime_compile: bool = True
_process_denials = 0
_process_lock = threading.RLock()
_force_allow: ContextVar[bool] = ContextVar("hedron_force_runtime_compile", default=False)
_runtime_policy: ContextVar[RuntimeCompilePolicy | None] = ContextVar(
    "hedron_runtime_compile_policy", default=None
)


def is_production_env(*, production: bool | None = None) -> bool:
    if production is not None:
        return production
    # Strip so trailing/leading whitespace from env files / orchestrators cannot
    # silently disable production gates (see #195).
    return os.environ.get("HEDRON_ENV", "").strip().lower() in {"prod", "production"}


def set_runtime_compile_allowed(allowed: bool) -> None:
    """Set the core-only process fallback for runtime build-input compilation."""
    global _process_allow_runtime_compile
    with _process_lock:
        _process_allow_runtime_compile = allowed


@contextmanager
def deny_runtime_compile() -> Generator[None, None, None]:
    """Deny process-fallback compilation until every overlapping scope exits."""
    global _process_denials
    with _process_lock:
        _process_denials += 1
    try:
        yield
    finally:
        with _process_lock:
            _process_denials = max(0, _process_denials - 1)


@contextmanager
def use_runtime_compile_policy(policy: RuntimeCompilePolicy) -> Generator[None, None, None]:
    """Bind an application-owned compile policy for the current execution context."""
    token = _runtime_policy.set(policy)
    try:
        yield
    finally:
        _runtime_policy.reset(token)


@contextmanager
def force_runtime_compile() -> Generator[None, None, None]:
    """Temporarily allow compile APIs (e.g. ``hedron build`` under HEDRON_ENV=production)."""
    token = _force_allow.set(True)
    try:
        yield
    finally:
        _force_allow.reset(token)


def assert_runtime_compile_allowed(*, production: bool | None = None, what: str = "CSS") -> None:
    if _force_allow.get():
        return
    if production is False:
        return
    policy = _runtime_policy.get()
    with _process_lock:
        process_blocked = not _process_allow_runtime_compile or _process_denials > 0
    blocked = (
        production is True
        or (policy is not None and not policy.allowed)
        or (policy is None and process_blocked)
        or is_production_env()
    )
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
