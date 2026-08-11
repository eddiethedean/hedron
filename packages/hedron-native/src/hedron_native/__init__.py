"""Optional Rust-accelerated HTML escaping with pure-Python fallback."""

from __future__ import annotations

import html as html_stdlib
import os
from collections.abc import Callable

__version__ = "0.1.2"

# Ops / evidence disable (NATIVE-028). Honored on every escape / availability call.
_DISABLE_ENV = "HEDRON_NATIVE_DISABLE"


def _env_disables_native() -> bool:
    raw = os.environ.get(_DISABLE_ENV, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _py_escape_text(value: str) -> str:
    return html_stdlib.escape(value.replace("\x00", ""), quote=False)


def _py_escape_attr(value: str) -> str:
    return html_stdlib.escape(value.replace("\x00", ""), quote=True)


def _load_extension() -> tuple[Callable[[str], str] | None, Callable[[str], str] | None]:
    try:
        from hedron_native._native import escape_attr as native_attr
        from hedron_native._native import escape_text as native_text

        return native_text, native_attr
    except Exception:  # noqa: BLE001
        return None, None


_native_text_impl, _native_attr_impl = _load_extension()
_extension_present = _native_text_impl is not None and _native_attr_impl is not None


def native_available() -> bool:
    """Return True when the Rust extension is loaded and not disabled by env."""
    return _extension_present and not _env_disables_native()


def native_disabled_by_env() -> bool:
    """Return True when HEDRON_NATIVE_DISABLE forces the Python path."""
    return _env_disables_native()


def escape_text(value: str) -> str:
    """Escape text for HTML body nodes (NUL stripped)."""
    if native_available() and _native_text_impl is not None:
        return _native_text_impl(value)
    return _py_escape_text(value)


def escape_attr(value: str) -> str:
    """Escape text for HTML attribute values (NUL stripped)."""
    if native_available() and _native_attr_impl is not None:
        return _native_attr_impl(value)
    return _py_escape_attr(value)


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
