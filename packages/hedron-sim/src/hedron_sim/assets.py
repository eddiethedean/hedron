"""Locate and copy packaged JS/CSS assets into a docs tree."""

from __future__ import annotations

from importlib import resources
from pathlib import Path, PurePosixPath

from hedron_core.diagnostics import error

__all__ = ["asset_path", "copy_assets", "css_text", "javascript_text"]


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
            "HED-SIM-ASSET-0001",
            title="Invalid packaged asset name",
            explanation=f"Asset name {name!r} escapes the package static directory.",
            remediation="Pass a single basename under hedron_sim/static/.",
        )
    return raw.name


def asset_path(name: str) -> Path:
    """Return a filesystem path to a packaged static asset by basename."""
    safe = _sanitize_asset_name(name)
    root = resources.files("hedron_sim").joinpath("static")
    with resources.as_file(root) as base:
        target = (Path(base) / safe).resolve()
        try:
            target.relative_to(Path(base).resolve())
        except ValueError as exc:
            raise error(
                "HED-SIM-ASSET-0001",
                title="Invalid packaged asset name",
                explanation=f"Asset name {name!r} escapes the package static directory.",
                remediation="Pass a single basename under hedron_sim/static/.",
            ) from exc
        if not target.is_file():
            raise error(
                "HED-SIM-ASSET-0002",
                title="Packaged asset missing",
                explanation=f"Asset {safe!r} was not found under static/.",
                remediation="Use a filename that ships in hedron_sim/static/.",
            )
        return target


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
