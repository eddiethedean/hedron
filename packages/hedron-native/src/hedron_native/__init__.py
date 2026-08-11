"""Optional Rust-accelerated HTML escaping with pure-Python fallback."""

from __future__ import annotations

import html as html_stdlib
import os
from collections.abc import Callable

__version__ = "0.1.1"

# Process-start disable for NATIVE-028 fallback injection (ops / evidence).
_DISABLE_ENV = "HEDRON_NATIVE_DISABLE"


def _env_disables_native() -> bool:
    raw = os.environ.get(_DISABLE_ENV, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _py_escape_text(value: str) -> str:
    return html_stdlib.escape(value.replace("\x00", ""), quote=False)


def _py_escape_attr(value: str) -> str:
    return html_stdlib.escape(value.replace("\x00", ""), quote=True)


def _resolve_impls() -> tuple[Callable[[str], str], Callable[[str], str], bool]:
    if _env_disables_native():
        return _py_escape_text, _py_escape_attr, False
    try:
        from hedron_native._native import escape_attr as native_attr
        from hedron_native._native import escape_text as native_text

        return native_text, native_attr, True
    except Exception:  # noqa: BLE001
        return _py_escape_text, _py_escape_attr, False


_escape_text_impl, _escape_attr_impl, _native_loaded = _resolve_impls()


def native_available() -> bool:
    """Return True when the compiled Rust extension is loaded and not disabled."""
    return _native_loaded


def native_disabled_by_env() -> bool:
    """Return True when HEDRON_NATIVE_DISABLE forces the Python path."""
    return _env_disables_native()


def escape_text(value: str) -> str:
    """Escape text for HTML body nodes (NUL stripped)."""
    return _escape_text_impl(value)


def escape_attr(value: str) -> str:
    """Escape text for HTML attribute values (NUL stripped)."""
    return _escape_attr_impl(value)


def escape_text_python(value: str) -> str:
    """Pure-Python reference path (always available)."""
    return _py_escape_text(value)


def escape_attr_python(value: str) -> str:
    """Pure-Python reference path (always available)."""
    return _py_escape_attr(value)


__all__ = [
    "__version__",
    "escape_attr",
    "escape_attr_python",
    "escape_text",
    "escape_text_python",
    "native_available",
    "native_disabled_by_env",
]
