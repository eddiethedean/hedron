"""Optional Rust-accelerated HTML escaping with pure-Python fallback."""

from __future__ import annotations

import html as html_stdlib
from collections.abc import Callable

__version__ = "0.1.0"


def _py_escape_text(value: str) -> str:
    return html_stdlib.escape(value.replace("\x00", ""), quote=False)


def _py_escape_attr(value: str) -> str:
    return html_stdlib.escape(value.replace("\x00", ""), quote=True)


def _resolve_impls() -> tuple[Callable[[str], str], Callable[[str], str], bool]:
    try:
        from hedron_native._native import escape_attr as native_attr
        from hedron_native._native import escape_text as native_text

        return native_text, native_attr, True
    except Exception:  # noqa: BLE001
        return _py_escape_text, _py_escape_attr, False


_escape_text_impl, _escape_attr_impl, _native_loaded = _resolve_impls()


def native_available() -> bool:
    """Return True when the compiled Rust extension is loaded."""
    return _native_loaded


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
]
