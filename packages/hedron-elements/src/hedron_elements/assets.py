"""Locate packaged element static assets."""

from __future__ import annotations

from importlib import resources
from pathlib import PurePosixPath

from hedron_core.diagnostics import error

__all__ = ["asset_path", "bridge_path", "example_css_path", "example_module_path", "asset_bytes"]


def _sanitize_asset_name(name: str) -> str:
    raw = PurePosixPath(name)
    if (
        raw.is_absolute()
        or ".." in raw.parts
        or "/" in name
        or "\\" in name
        or name.startswith("~")
        or not name
    ):
        raise error(
            "HED-ELEMENT-ASSET-0001",
            title="Invalid packaged asset name",
            explanation=f"Asset name {name!r} escapes the package static directory.",
            remediation="Pass a single basename under hedron_elements/static/.",
        )
    return raw.name


def asset_bytes(name: str) -> bytes:
    """Read a packaged static asset by basename (safe under zipimport)."""
    safe = _sanitize_asset_name(name)
    target = resources.files("hedron_elements").joinpath("static").joinpath(safe)
    return target.read_bytes()


def asset_path(name: str):
    """Resolve a packaged static asset path by basename.

    Names must be single path segments under ``static/``. Absolute paths,
    ``..``, and separators are rejected. Prefer :func:`asset_bytes` when
    reading content under zipimport.
    """
    from pathlib import Path

    safe = _sanitize_asset_name(name)
    root = resources.files("hedron_elements").joinpath("static")
    with resources.as_file(root) as base:
        target = (Path(base) / safe).resolve()
        try:
            target.relative_to(Path(base).resolve())
        except ValueError as exc:
            raise error(
                "HED-ELEMENT-ASSET-0001",
                title="Invalid packaged asset name",
                explanation=f"Asset name {name!r} escapes the package static directory.",
                remediation="Pass a single basename under hedron_elements/static/.",
            ) from exc
        if not target.is_file():
            raise error(
                "HED-ELEMENT-ASSET-0002",
                title="Packaged asset missing",
                explanation=f"Asset {safe!r} was not found under static/.",
                remediation="Use a filename that ships in hedron_elements/static/.",
            )
        return target


def bridge_path():
    return asset_path("hedron-bridge.mjs")


def example_module_path():
    return asset_path("hedron-example.mjs")


def example_css_path():
    return asset_path("hedron-example.css")
