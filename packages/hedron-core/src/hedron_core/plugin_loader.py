"""Plugin discovery, compatibility, and lifespan orchestration."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable, Iterable, Sequence
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from hedron_core.codes import (
    HED_PLUGIN_CYCLE,
    HED_PLUGIN_DUPLICATE,
    HED_PLUGIN_FAILED,
    HED_PLUGIN_INCOMPATIBLE,
    HED_PLUGIN_MISSING,
)
from hedron_core.diagnostics import error
from hedron_core.plugins import PluginContext, PluginMeta
from hedron_core.registry import restore_registry_builder, snapshot_registry_builder

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
    _rollback: Callable[[], None] | None = None

    def start(self) -> None:
        started: list[LoadedPlugin] = []
        try:
            for item in self.loaded:
                for hook in item.context._startup:
                    hook()
                started.append(item)
            self._started = True
        except Exception:
            for item in reversed(started):
                for hook in reversed(item.context._shutdown):
                    with suppress(Exception):
                        hook()
            if self._rollback is not None:
                self._rollback()
            self.loaded.clear()
            self._started = False
            raise

    def shutdown(self) -> None:
        errors: list[Exception] = []
        for item in reversed(self.loaded):
            for hook in reversed(item.context._shutdown):
                try:
                    hook()
                except Exception as exc:  # noqa: BLE001
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
    """Return True when ``version`` satisfies the PEP 440 specifier set."""
    try:
        return Version(version) in SpecifierSet(spec)
    except (InvalidSpecifier, InvalidVersion):
        return False


def load_plugins(
    *,
    enabled: Sequence[str] | None = None,
    hedron_version: str | None = None,
    entry_points: Iterable[Any] | None = None,
) -> PluginLoader:
    """Discover and activate plugins into a temporary contribution pass.

    ``enabled`` semantics:
    - ``None``: load every discovered entry point except ``*_experimental``
      (unless ``HEDRON_EXPERIMENTAL_UI`` is truthy — EXTRAS-025 quarantine)
    - empty sequence: load none
    - non-empty: load only named entry points; missing names raise ``HED-PLUGIN-MISSING``

    On failure, registry contributions and Explorer panels are rolled back.
    """
    from hedron_core import __version__ as core_version
    from hedron_core import plugins as plugins_mod

    version = hedron_version or core_version
    registry_snapshot = snapshot_registry_builder()
    panel_snapshot = dict(plugins_mod._panels)
    owner_snapshot = dict(plugins_mod._diagnostic_owners)
    feature_snapshot = dict(plugins_mod._features)
    experimental_env = os.environ.get("HEDRON_EXPERIMENTAL_UI", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    def _rollback() -> None:
        restore_registry_builder(registry_snapshot)
        plugins_mod._panels.clear()
        plugins_mod._panels.update(panel_snapshot)
        plugins_mod._diagnostic_owners.clear()
        plugins_mod._diagnostic_owners.update(owner_snapshot)
        plugins_mod._features.clear()
        plugins_mod._features.update(feature_snapshot)

    discovered = list(entry_points) if entry_points is not None else _discover_entry_points()
    discovered_names: list[str] = []
    metas: dict[str, tuple[Any, PluginMeta]] = {}
    try:
        for ep in discovered:
            name = getattr(ep, "name", None) or str(ep)
            discovered_names.append(name)
            if enabled is not None and name not in enabled:
                continue
            if enabled is None and not experimental_env and str(name).endswith("_experimental"):
                continue
            try:
                target = ep.load() if hasattr(ep, "load") else ep
            except Exception as exc:
                raise error(
                    HED_PLUGIN_MISSING,
                    title="Plugin import failed",
                    explanation=f"Could not load plugin {name!r}: {exc}",
                    remediation="Install the plugin package or fix the entry point.",
                ) from exc
            meta = getattr(target, "PLUGIN_META", None)
            if not isinstance(meta, PluginMeta):
                raise error(
                    HED_PLUGIN_FAILED,
                    title="Plugin missing PLUGIN_META",
                    explanation=(
                        f"Plugin {name!r} must expose PLUGIN_META with an explicit "
                        "hedron_version specifier."
                    ),
                    remediation=(
                        # Example pin must stay aligned with docs/release.toml train bounds.
                        "Attach PluginMeta(..., hedron_version='>=0.42,<0.43') to the "
                        "register entry point."
                    ),
                )
            if not compatible_hedron_version(meta.hedron_version, version):
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

        if enabled is not None:
            missing = [n for n in enabled if n not in discovered_names]
            if missing:
                raise error(
                    HED_PLUGIN_MISSING,
                    title="Enabled plugin not found",
                    explanation=(
                        "Configured plugins were not discovered: "
                        + ", ".join(repr(n) for n in missing)
                    ),
                    remediation="Install the plugin package or fix [tool.hedron] plugins.",
                )

        order = _topo_sort({name: meta.depends_on for name, (_, meta) in metas.items()})
        loader = PluginLoader(_rollback=_rollback)
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
        _rollback()
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
