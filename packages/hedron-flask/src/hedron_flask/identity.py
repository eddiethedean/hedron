"""Process-local Hedron app identity for Flask ownership checks."""

from __future__ import annotations

from typing import Any

__all__ = ["expected_hedron_app_id"]


def expected_hedron_app_id(extension: object | None = None) -> str | None:
    """Return the bound HedronFlask app id, if one is installed on this request."""
    if extension is None:
        try:
            from flask import current_app, has_app_context
        except ImportError:  # pragma: no cover - flask is a hard adapter dep
            return None
        if has_app_context():
            extension = current_app.extensions.get("hedron")
    value: Any = getattr(extension, "hedron_app_id", None)
    return str(value) if value else None
