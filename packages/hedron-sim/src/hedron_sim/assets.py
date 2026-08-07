"""Locate and copy packaged JS/CSS assets into a docs tree."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

__all__ = ["asset_path", "copy_assets", "css_text", "javascript_text"]


def asset_path(name: str) -> Path:
    """Return a filesystem path to a packaged static asset (may be inside a zip)."""
    target = resources.files("hedron_sim").joinpath("static").joinpath(name)
    with resources.as_file(target) as path:
        return Path(path)


def javascript_text() -> str:
    return (
        resources.files("hedron_sim").joinpath("static/hedron-sim.js").read_text(encoding="utf-8")
    )


def css_text() -> str:
    return (
        resources.files("hedron_sim").joinpath("static/hedron-sim.css").read_text(encoding="utf-8")
    )


def copy_assets(
    javascript_dir: Path | str,
    stylesheets_dir: Path | str | None = None,
) -> tuple[Path, Path | None]:
    """Copy ``hedron-sim.js`` (and optional CSS) into docs asset directories.

    Returns:
        Paths to the written JS file and CSS file (CSS may be ``None`` when skipped).
    """
    js_dir = Path(javascript_dir)
    js_dir.mkdir(parents=True, exist_ok=True)
    js_dest = js_dir / "hedron-sim.js"
    js_dest.write_text(javascript_text(), encoding="utf-8")

    css_dest: Path | None = None
    if stylesheets_dir is not None:
        css_dir = Path(stylesheets_dir)
        css_dir.mkdir(parents=True, exist_ok=True)
        css_dest = css_dir / "hedron-sim.css"
        css_dest.write_text(css_text(), encoding="utf-8")
    return js_dest, css_dest
