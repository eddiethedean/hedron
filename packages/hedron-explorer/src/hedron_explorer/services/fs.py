"""Allowlisted filesystem reads for Explorer source panels."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import cast

from fastapi import Request

_logger = logging.getLogger("hedron.explorer")


def project_component_roots(request: Request | None) -> list[Path]:
    """Trusted roots only: app.state and [tool.hedron] component_roots."""
    roots: list[Path] = []
    if request is None:
        return roots
    configured = getattr(request.app.state, "hedron_component_roots", None)
    if configured:
        roots.extend(Path(str(p)).resolve() for p in cast(list[object], configured))
    project_root = getattr(request.app.state, "hedron_project_root", None)
    if project_root:
        try:
            loader = getattr(request.app.state, "hedron_settings_loader", None)
            if callable(loader):
                settings = loader(Path(project_root))
            else:
                from importlib import import_module

                mod = import_module("hedron.config")
                settings = mod.load_hedron_settings(Path(project_root))
            resolved = getattr(settings, "resolved_roots", None)
            if callable(resolved):
                extra = resolved(base=Path(project_root))
                if isinstance(extra, (list, tuple)):
                    roots.extend(
                        Path(str(p)) for p in cast(list[object] | tuple[object, ...], extra)
                    )
        except Exception as exc:  # noqa: BLE001
            _logger.debug("Explorer component roots from settings unavailable: %s", exc)
    return roots


def allowed_roots(meta: object, request: Request | None = None) -> list[Path]:
    del meta
    return project_component_roots(request)


def hdj_text_under_root(path: Path, root: Path) -> str | None:
    """Read ``*.hdj`` only when the resolved target stays under ``root`` (#275)."""
    try:
        resolved = path.resolve()
        resolved.relative_to(root)
    except (OSError, ValueError):
        return None
    if not resolved.is_file():
        return None
    try:
        return resolved.read_text(encoding="utf-8")
    except OSError:
        return None


def safe_read_text(
    path_str: str | None, meta: object, request: Request | None = None
) -> str | None:
    """Read a file only when it resolves under an allowlisted component root."""
    if not path_str:
        return None
    try:
        candidate = Path(path_str).resolve()
    except OSError:
        return None
    if not candidate.is_file():
        return None
    for root_path in allowed_roots(meta, request):
        try:
            candidate.relative_to(root_path)
        except ValueError:
            continue
        try:
            return candidate.read_text(encoding="utf-8")
        except OSError:
            return None
    return None


_project_component_roots = project_component_roots
_allowed_roots = allowed_roots
_hdj_text_under_root = hdj_text_under_root
_safe_read_text = safe_read_text
