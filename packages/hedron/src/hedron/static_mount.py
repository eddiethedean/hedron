"""Static asset mounting helpers (no lifespan circular import)."""

from __future__ import annotations

import os
from importlib import resources
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from hedron.fastapi_compat import remove_route

__all__ = ["mount_build_assets", "mount_hedron_static"]


def mount_hedron_static(app: FastAPI, *, path: str = "/hedron-static") -> None:
    """Mount bundled Hedron static assets (HTMX, disclose) on any FastAPI app.

    Assets are owned by ``hedron-core`` so Flask/Django adapters share the same
    files without depending on the FastAPI flagship package.
    """
    from hedron_core.page_assets import static_directory

    static_dir = static_directory()
    if not static_dir.is_dir():
        # Back-compat: older editable installs may still ship assets under hedron.
        legacy = Path(str(resources.files("hedron").joinpath("static")))
        static_dir = legacy if legacy.is_dir() else static_dir
    if not static_dir.is_dir():
        return
    for route in app.routes:
        if getattr(route, "path", None) == path:
            return
    app.mount(path, StaticFiles(directory=str(static_dir)), name="hedron-static")


def mount_build_assets(
    app: FastAPI,
    build_dir: Path | str | None = None,
    *,
    path: str = "/hedron-assets",
) -> Path | None:
    """Mount fingerprinted build assets from a Hedron build directory."""
    if build_dir is None:
        build_dir = os.environ.get("HEDRON_BUILD_DIR", ".hedron/build")
    root = Path(build_dir).resolve()
    assets = root / "assets"
    if not assets.is_dir():
        return None
    existing_dir = getattr(app.state, "hedron_assets_dir", None)
    for idx, route in enumerate(list(app.routes)):
        if getattr(route, "path", None) != path:
            continue
        if existing_dir is not None and Path(existing_dir).resolve() == assets.resolve():
            return assets
        # Different build tree already mounted — replace the mount.
        remove_route(app, idx)
        break
    app.mount(path, StaticFiles(directory=str(assets)), name="hedron-assets")
    app.state.hedron_assets_path = path.rstrip("/") or path
    app.state.hedron_assets_dir = str(assets.resolve())
    app.state.hedron_build_dir = str(root)
    return assets
