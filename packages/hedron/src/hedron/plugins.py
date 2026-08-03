"""Plugin discovery, compatibility, and lifespan orchestration."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

from hedron_core.codes import (
    HED_PLUGIN_CYCLE,
    HED_PLUGIN_DUPLICATE,
    HED_PLUGIN_FAILED,
    HED_PLUGIN_INCOMPATIBLE,
    HED_PLUGIN_MISSING,
)
from hedron_core.diagnostics import error
from hedron_core.plugins import PluginContext, PluginMeta

logger = logging.getLogger("hedron.plugins")

ENTRY_POINT_GROUP = "hedron.plugins"

__all__ = [
    "ENTRY_POINT_GROUP",
    "LoadedPlugin",
    "PluginLoader",
    "load_plugins",
    "compatible_hedron_version",
]


@dataclass
class LoadedPlugin:
    meta: PluginMeta
    context: PluginContext
    entry_point: str


@dataclass
class PluginLoader:
    loaded: list[LoadedPlugin] = field(default_factory=list)
    _started: bool = False

    def start(self) -> None:
        for item in self.loaded:
            for hook in item.context._startup:
                hook()
        self._started = True

    def shutdown(self) -> None:
        errors: list[Exception] = []
        for item in reversed(self.loaded):
            for hook in reversed(item.context._shutdown):
                try:
                    hook()
                except Exception as exc:  # noqa: BLE001 — aggregate shutdown failures
                    errors.append(exc)
        self._started = False
        if errors:
            raise error(
                HED_PLUGIN_FAILED,
                title="Plugin shutdown failed",
                explanation="; ".join(str(e) for e in errors),
                remediation="Inspect plugin shutdown hooks.",
            )


def compatible_hedron_version(spec: str, version: str) -> bool:
    """Minimal ``>=X.Y,<A.B`` checker used by the plugin loader."""
    parts = [p.strip() for p in spec.split(",") if p.strip()]
    major_minor = tuple(int(x) for x in version.split(".")[:2])
    for part in parts:
        if part.startswith(">="):
            floor = tuple(int(x) for x in part[2:].split(".")[:2])
            if major_minor < floor:
                return False
        elif part.startswith("<"):
            ceil = tuple(int(x) for x in part[1:].split(".")[:2])
            if major_minor >= ceil:
                return False
        elif part.startswith("=="):
            if version != part[2:]:
                return False
    return True


def load_plugins(
    *,
    enabled: Sequence[str] | None = None,
    hedron_version: str | None = None,
    entry_points: Iterable[Any] | None = None,
) -> PluginLoader:
    """Discover and activate plugins into a temporary contribution pass.

    On failure the loader leaves no partially started hooks. Contributions that
    register into the global registry are expected to run before ``seal_registry``.
    """
    from hedron_core import __version__ as core_version

    version = hedron_version or core_version
    # Snapshot panel state for rollback of panel contributions only.
    from hedron_core import plugins as plugins_mod

    panel_snapshot = dict(plugins_mod._panels)
    owner_snapshot = dict(plugins_mod._diagnostic_owners)

    discovered = list(entry_points) if entry_points is not None else _discover_entry_points()
    metas: dict[str, tuple[Any, PluginMeta]] = {}
    for ep in discovered:
        name = getattr(ep, "name", None) or str(ep)
        if enabled is not None and name not in enabled and enabled:
            continue
        try:
            target = ep.load() if hasattr(ep, "load") else ep
        except Exception as exc:  # noqa: BLE001
            raise error(
                HED_PLUGIN_MISSING,
                title="Plugin import failed",
                explanation=f"Could not load plugin {name!r}: {exc}",
                remediation="Install the plugin package or fix the entry point.",
            ) from exc
        meta = getattr(target, "PLUGIN_META", None)
        if not isinstance(meta, PluginMeta):
            # Callable that returns meta+register
            if not callable(target):
                raise error(
                    HED_PLUGIN_FAILED,
                    title="Invalid plugin entry point",
                    explanation=f"Plugin {name!r} must be callable or expose PLUGIN_META.",
                    remediation="Export a register(ctx) callable.",
                )
            # Deferred meta via attribute on wrapper
            meta = PluginMeta(
                name=name,
                version="0.0.0",
                distribution=name,
            )
        if not compatible_hedron_version(meta.hedron_version, version):
            # Rollback panels
            plugins_mod._panels.clear()
            plugins_mod._panels.update(panel_snapshot)
            plugins_mod._diagnostic_owners.clear()
            plugins_mod._diagnostic_owners.update(owner_snapshot)
            raise error(
                HED_PLUGIN_INCOMPATIBLE,
                title="Incompatible plugin",
                explanation=(
                    f"Plugin {meta.name!r} requires Hedron {meta.hedron_version}, "
                    f"running {version}."
                ),
                remediation="Upgrade/downgrade the plugin or Hedron.",
            )
        if meta.name in metas:
            raise error(
                HED_PLUGIN_DUPLICATE,
                title="Duplicate plugin",
                explanation=f"Plugin {meta.name!r} discovered more than once.",
                remediation="Remove the duplicate entry point.",
            )
        metas[meta.name] = (target, meta)

    order = _topo_sort({name: meta.depends_on for name, (_, meta) in metas.items()})
    loader = PluginLoader()
    try:
        for name in order:
            target, meta = metas[name]
            ctx = PluginContext(meta)
            register = target if callable(target) else getattr(target, "register", None)
            if register is None:
                raise error(
                    HED_PLUGIN_FAILED,
                    title="Plugin missing register",
                    explanation=f"Plugin {name!r} has no register callable.",
                    remediation="Provide register(ctx: PluginContext).",
                )
            register(ctx)
            loader.loaded.append(LoadedPlugin(meta=meta, context=ctx, entry_point=name))
    except Exception:
        plugins_mod._panels.clear()
        plugins_mod._panels.update(panel_snapshot)
        plugins_mod._diagnostic_owners.clear()
        plugins_mod._diagnostic_owners.update(owner_snapshot)
        raise

    return loader


def _discover_entry_points() -> list[Any]:
    try:
        from importlib.metadata import entry_points
    except ImportError:  # pragma: no cover
        return []
    eps = entry_points()
    if hasattr(eps, "select"):
        return list(eps.select(group=ENTRY_POINT_GROUP))
    return list(eps.get(ENTRY_POINT_GROUP, []))  # type: ignore[arg-type]


def _topo_sort(deps: dict[str, tuple[str, ...]]) -> list[str]:
    seen: set[str] = set()
    stack: set[str] = set()
    ordered: list[str] = []

    def visit(name: str) -> None:
        if name in seen:
            return
        if name in stack:
            raise error(
                HED_PLUGIN_CYCLE,
                title="Plugin dependency cycle",
                explanation=f"Cycle detected at plugin {name!r}.",
                remediation="Remove cyclic depends_on edges.",
            )
        stack.add(name)
        for dep in deps.get(name, ()):
            if dep not in deps:
                raise error(
                    HED_PLUGIN_MISSING,
                    title="Missing plugin dependency",
                    explanation=f"Plugin requires {dep!r} which was not discovered.",
                    remediation="Install or enable the dependency plugin.",
                )
            visit(dep)
        stack.remove(name)
        seen.add(name)
        ordered.append(name)

    for name in sorted(deps):
        visit(name)
    return ordered
