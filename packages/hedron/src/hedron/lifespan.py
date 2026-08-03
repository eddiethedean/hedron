"""Lifespan composition, registry sealing, and production manifest loading."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from hedron_core.registry import seal_registry
from hedron_core.theme import ensure_default_theme_registered

__all__ = ["compose_lifespan"]

Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def compose_lifespan(
    user_lifespan: Lifespan | None = None,
    *,
    production: bool | None = None,
    build_dir: str | Path | None = None,
    theme: str | None = "default",
) -> Lifespan:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        ensure_default_theme_registered()
        app.state.hedron_theme = theme or getattr(app.state, "hedron_theme", "default")

        is_production = production
        if is_production is None:
            is_production = os.environ.get("HEDRON_ENV", "").lower() in {
                "prod",
                "production",
            }

        resolved_build = Path(
            build_dir
            or getattr(app.state, "hedron_build_dir", None)
            or os.environ.get("HEDRON_BUILD_DIR", ".hedron/build")
        )
        manifest_path = resolved_build / "manifest.json"
        if is_production:
            if not manifest_path.is_file():
                from hedron_core.codes import HED_BUILD_MISSING_MANIFEST
                from hedron_core.diagnostics import error

                raise error(
                    HED_BUILD_MISSING_MANIFEST,
                    title="Production build manifest missing",
                    explanation=(
                        f"Production mode requires {manifest_path}. "
                        "Runtime HDN/CSS compilation is disabled."
                    ),
                    remediation="Run `hedron build` and set HEDRON_BUILD_DIR if needed.",
                )
            from hedron.app import mount_build_assets
            from hedron.build import load_build_manifest

            manifest = load_build_manifest(resolved_build)
            app.state.hedron_build_manifest = manifest
            mount_build_assets(app, resolved_build)
        elif manifest_path.is_file():
            from hedron.app import mount_build_assets
            from hedron.build import load_build_manifest

            app.state.hedron_build_manifest = load_build_manifest(resolved_build)
            mount_build_assets(app, resolved_build)

        seal_registry()
        if user_lifespan is not None:
            async with user_lifespan(app):
                yield
        else:
            yield

    return lifespan
