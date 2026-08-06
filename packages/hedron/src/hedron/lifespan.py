"""Lifespan composition, registry sealing, and production manifest loading."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from hedron_core.compile_gate import is_production_env, set_runtime_compile_allowed
from hedron_core.registry import seal_registry
from hedron_core.theme import ensure_default_theme_registered

__all__ = ["compose_lifespan"]

Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def _settings_root(app: FastAPI, resolved_build: Path) -> Path:
    """Prefer an explicit project root, then build parent, then cwd."""
    explicit = getattr(app.state, "hedron_project_root", None)
    if explicit:
        return Path(explicit).resolve()
    build_parent = resolved_build.resolve().parent
    # `.hedron/build` → project root is parent of `.hedron`
    if build_parent.name == ".hedron":
        return build_parent.parent
    cwd = Path.cwd()
    if (cwd / "pyproject.toml").is_file():
        return cwd
    if (resolved_build.parent / "pyproject.toml").is_file():
        return resolved_build.parent.resolve()
    return cwd


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

        is_production = is_production_env(production=production)
        app.state.hedron_production = is_production
        if is_production:
            set_runtime_compile_allowed(False)

        resolved_build = Path(
            build_dir
            or getattr(app.state, "hedron_build_dir", None)
            or os.environ.get("HEDRON_BUILD_DIR", ".hedron/build")
        )
        manifest_path = resolved_build / "manifest.json"
        from hedron.static_mount import mount_build_assets

        try:
            if is_production:
                if not manifest_path.is_file():
                    from hedron_core.codes import HED_BUILD_MISSING_MANIFEST
                    from hedron_core.diagnostics import error

                    raise error(
                        HED_BUILD_MISSING_MANIFEST,
                        title="Production build manifest missing",
                        explanation=(
                            f"Production mode requires {manifest_path}. "
                            "Runtime CSS compilation is disabled."
                        ),
                        remediation="Run `hedron build` and set HEDRON_BUILD_DIR if needed.",
                    )
                try:
                    from hedron.build import load_build_manifest

                    manifest = load_build_manifest(resolved_build)
                except Exception as exc:
                    from hedron_core.codes import HED_BUILD_MISSING_MANIFEST
                    from hedron_core.diagnostics import HedronError, error

                    if isinstance(exc, HedronError):
                        raise
                    raise error(
                        HED_BUILD_MISSING_MANIFEST,
                        title="Production build manifest invalid",
                        explanation=f"Failed to load {manifest_path}: {exc}",
                        remediation="Run `hedron build` to regenerate a valid manifest.",
                    ) from exc
                app.state.hedron_build_manifest = manifest
                app.state.hedron_build_dir = str(resolved_build.resolve())
                mount_build_assets(app, resolved_build)
            elif manifest_path.is_file():
                from hedron.build import load_build_manifest

                try:
                    app.state.hedron_build_manifest = load_build_manifest(resolved_build)
                    app.state.hedron_build_dir = str(resolved_build.resolve())
                    mount_build_assets(app, resolved_build)
                except FileNotFoundError:
                    # Race: manifest disappeared between exists check and load.
                    pass
                except Exception as exc:
                    import logging

                    logging.getLogger("hedron.lifespan").warning(
                        "Ignoring corrupt non-production build manifest at %s: %s",
                        manifest_path,
                        exc,
                    )

            from hedron.config import HedronSettings, load_hedron_settings
            from hedron.plugins import load_plugins

            settings_root = _settings_root(app, resolved_build)
            app.state.hedron_project_root = str(settings_root)
            if (settings_root / "pyproject.toml").is_file():
                settings = load_hedron_settings(settings_root)
            else:
                settings = HedronSettings()
            app.state.hedron_component_roots = [
                str(p) for p in settings.resolved_roots(base=settings_root)
            ]
            enabled = None if settings.plugins is None else list(settings.plugins)
            plugin_loader = load_plugins(enabled=enabled)
            app.state.hedron_plugin_loader = plugin_loader
            try:
                plugin_loader.start()
            except Exception:
                # Keep loader on app.state so finally still runs shutdown hooks.
                raise

            seal_registry()
            if is_production:
                from hedron_core.production_gate import assert_durable_backends

                assert_durable_backends(production=True)
            if user_lifespan is not None:
                async with user_lifespan(app):
                    yield
            else:
                yield
        finally:
            loader = getattr(app.state, "hedron_plugin_loader", None)
            if loader is not None:
                from contextlib import suppress

                with suppress(Exception):
                    loader.shutdown()
            if is_production:
                set_runtime_compile_allowed(True)

    return lifespan
