"""Serve bundled Hedron static assets from ``hedron-core`` on Flask apps."""

from __future__ import annotations

from flask import Flask, Response, send_from_directory

from hedron_core.page_assets import DEFAULT_STATIC_PREFIX, static_directory

__all__ = ["mount_hedron_static"]

_ENDPOINT = "hedron_static"


def mount_hedron_static(app: Flask, *, path: str = DEFAULT_STATIC_PREFIX) -> None:
    """Register ``/hedron-static/<path>`` serving core-bundled HTMX assets."""
    prefix = path.rstrip("/") or DEFAULT_STATIC_PREFIX
    rule = f"{prefix}/<path:asset_path>"
    # Idempotent: skip if already registered for this app.
    if any(getattr(r, "endpoint", None) == _ENDPOINT for r in app.url_map.iter_rules()):
        return

    static_root = static_directory()

    def hedron_static(asset_path: str) -> Response:
        return send_from_directory(static_root, asset_path)

    app.add_url_rule(rule, endpoint=_ENDPOINT, view_func=hedron_static)
