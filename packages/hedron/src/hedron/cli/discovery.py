"""CLI project discovery, app loading, and scaffold pin helpers."""

from __future__ import annotations

import importlib
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

from hedron.config import HedronSettings
from hedron_core.compat import tomllib
from hedron_core.registry import ComponentMeta, get_registry


@lru_cache(maxsize=1)
def release_pin_bounds() -> tuple[str, str]:
    """Return ``(pin_floor, pin_ceiling)`` for scaffold dependency pins.

    Prefer ``docs/release.toml`` when running from a monorepo checkout. Fall back to
    this package's ``__version__`` as the floor (published wheels) and the next
    minor train as the ceiling.
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "docs" / "release.toml"
        if not candidate.is_file():
            continue
        release = tomllib.loads(candidate.read_text(encoding="utf-8")).get("release", {})
        status = str(release.get("registry_status", "")).strip()
        if status == "deferred":
            floor = str(release.get("pypi_pin_floor") or release.get("pin_floor") or "").strip()
            ceiling = str(
                release.get("pypi_pin_ceiling") or release.get("pin_ceiling") or ""
            ).strip()
        else:
            floor = str(release.get("pin_floor", "")).strip()
            ceiling = str(release.get("pin_ceiling", "")).strip()
        if floor and ceiling:
            return floor, ceiling
    from hedron import __version__ as package_version

    return package_version, _next_minor_ceiling(package_version)


def _next_minor_ceiling(package_version: str) -> str:
    parts = package_version.split(".")
    if len(parts) < 2 or not parts[1].isdigit():
        raise RuntimeError(f"cannot derive scaffold pin from version {package_version!r}")
    major = int(parts[0])
    minor = int(parts[1])
    return f"{major}.{minor + 1}"


def scaffold_dep(package: str) -> str:
    floor, ceiling = release_pin_bounds()
    return f"{package}>={floor},<{ceiling}"


def load_app(app_path: str | None) -> Any | None:
    if not app_path:
        return None
    if ":" not in app_path:
        raise SystemExit("--app must look like 'module.path:attribute'")
    module_name, attr = app_path.split(":", 1)
    module = importlib.import_module(module_name)
    target: Any = module
    for part in attr.split("."):
        target = getattr(target, part)
    if _should_invoke_app_factory(target):
        target = target()
    return target


def _should_invoke_app_factory(target: Any) -> bool:
    """Invoke only ASGI/Starlette factories, not Flask apps or WSGI callables."""
    if not callable(target):
        return False
    if hasattr(target, "routes"):
        return False
    if hasattr(target, "wsgi_app"):
        return False
    import inspect

    try:
        if len(inspect.signature(target).parameters) == 2:
            return False
    except (ValueError, TypeError):
        pass
    return True


def registry_empty_hint(*, app: str | None, what: str) -> None:
    if app:
        return
    registry = get_registry()
    if registry.components() or registry.routes() or registry.addressables():
        return
    print(
        f"No {what} found. Pass --app module:attr to load an application "
        "before inspecting the registry.",
        file=sys.stderr,
    )


def apply_project_discovery(base: Path | None = None) -> HedronSettings:
    """Load settings, discover folders, and optionally load configured plugins."""
    from hedron.config import load_hedron_settings
    from hedron.plugins import load_plugins
    from hedron_core.discovery import apply_discovery_to_registry, discover_component_folders

    root = (base or Path.cwd()).resolve()
    settings = load_hedron_settings(root)
    discovered = discover_component_folders(settings.resolved_roots(base=root))
    apply_discovery_to_registry(discovered)
    if settings.plugins is not None:
        try:
            load_plugins(enabled=list(settings.plugins))
        except Exception as exc:
            print(f"Plugin load failed: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
    return settings


def find_component(name: str) -> ComponentMeta | None:
    registry = get_registry()
    aliases = {"NavLink": "HtmxLink"}
    wanted = {name, aliases.get(name, name)}
    for c in registry.components():
        if c.logical_id == name or c.name in wanted or c.logical_id.endswith(f".{name}"):
            return c
        if any(c.logical_id.endswith(f".{alias}") for alias in wanted):
            return c
    return None


_release_pin_bounds = release_pin_bounds
_scaffold_dep = scaffold_dep
_load_app = load_app
_registry_empty_hint = registry_empty_hint
_apply_project_discovery = apply_project_discovery
_find_component = find_component
