"""Production compile gates for HDN/CSS."""

from __future__ import annotations

import os
from typing import Any

from hedron_core.codes import HED_BUILD_RUNTIME_COMPILE
from hedron_core.diagnostics import error

__all__ = [
    "assert_runtime_compile_allowed",
    "is_production_env",
    "production_compile_guard",
]


def is_production_env(*, production: bool | None = None) -> bool:
    if production is not None:
        return production
    return os.environ.get("HEDRON_ENV", "").lower() in {"prod", "production"}


def assert_runtime_compile_allowed(
    *, production: bool | None = None, what: str = "HDN/CSS"
) -> None:
    if is_production_env(production=production):
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
