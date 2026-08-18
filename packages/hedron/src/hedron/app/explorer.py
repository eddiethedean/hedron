"""Component Explorer settings hint and optional mount helpers."""

from __future__ import annotations

import logging
import warnings
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.params import Depends as DependsParam
from starlette.requests import Request

ExplorerMode = Literal["off", "development", "secured"]
logger = logging.getLogger("hedron")


def _settings_explorer_hint() -> str | None:
    """Read explicit [tool.hedron] explorer from cwd when present."""
    import tomllib

    try:
        cwd = Path.cwd()
        pyproject = cwd / "pyproject.toml"
        if not pyproject.is_file():
            return None
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        tool = data.get("tool") or {}
        hedron = tool.get("hedron") if isinstance(tool, dict) else None
        if not isinstance(hedron, dict) or "explorer" not in hedron:
            return None
        mode = str(hedron["explorer"] or "off")
        if mode in {"off", "development", "secured"}:
            return mode
    except (OSError, TypeError, ValueError, KeyError, tomllib.TOMLDecodeError):
        return None
    return None


def resolve_explorer_mode(
    explorer: ExplorerMode | str | None,
    *,
    explorer_enabled: bool,
    is_prod: bool,
) -> str:
    """Resolve explorer mode from kwargs, pyproject, policy, and production gates."""
    if explorer is None:
        settings_explorer = _settings_explorer_hint()
        if settings_explorer is not None:
            mode = settings_explorer
        else:
            mode = "development" if explorer_enabled else "off"
    else:
        mode = str(explorer)

    if is_prod and mode == "development":
        warnings.warn(
            "Explorer development mode is disabled in production; "
            "use explorer='secured' with explorer_dependencies, or explorer='off'.",
            UserWarning,
            stacklevel=3,
        )
        mode = "off"
    return mode


def _maybe_mount_explorer(
    app: FastAPI,
    *,
    secured: bool,
    explorer_dependencies: Sequence[DependsParam] | None = None,
) -> None:
    """Mount Component Explorer when the optional package is installed."""
    try:
        from hedron_explorer import explorer_router
    except ImportError:
        logger.warning("hedron-explorer is not installed; Explorer was not mounted")
        return
    deps: list[DependsParam] = list(explorer_dependencies or [])
    if secured and not deps:

        async def _require_authenticated(request: Request) -> None:
            if not getattr(request.state, "hedron_authenticated", False):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Explorer requires authentication",
                )

        deps.append(Depends(_require_authenticated))
    app.include_router(
        explorer_router(),
        prefix="/hedron-explorer",
        dependencies=deps or None,
    )
    try:
        from hedron_explorer.services.diff import snapshot_diff_baseline

        snapshot_diff_baseline(app)
    except ImportError:
        logger.debug("hedron-explorer diff snapshot unavailable")


def install_explorer_bridges(app: FastAPI) -> None:
    """Wire injectable explorer settings/CSRF hooks (ADP-005)."""
    app.state.hedron_settings_loader = None
    try:
        from hedron.config import load_hedron_settings

        app.state.hedron_settings_loader = load_hedron_settings
    except ImportError:
        logger.debug("hedron.config unavailable; explorer settings bridge disabled")
    try:
        from hedron.security.csrf import prepare_csrf_from_request, validate_csrf
        from hedron.security.policy import SecurityPolicy

        async def _csrf_validate(request: Request, policy: SecurityPolicy) -> None:
            await prepare_csrf_from_request(request, policy)
            validate_csrf(request, policy)

        app.state.hedron_csrf_validate = _csrf_validate
    except ImportError:
        logger.debug("CSRF helpers unavailable; explorer CSRF bridge disabled")
        app.state.hedron_csrf_validate = None


def mount_explorer_if_enabled(
    app: FastAPI,
    *,
    explorer_mode: str,
    explorer_dependencies: Sequence[DependsParam] | None = None,
) -> None:
    """Mount Explorer for development or secured modes."""
    if explorer_mode == "development":
        _maybe_mount_explorer(
            app,
            secured=False,
            explorer_dependencies=explorer_dependencies,
        )
    elif explorer_mode == "secured":
        _maybe_mount_explorer(
            app,
            secured=True,
            explorer_dependencies=explorer_dependencies,
        )
