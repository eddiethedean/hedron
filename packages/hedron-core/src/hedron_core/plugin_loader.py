"""Plugin discovery, compatibility, and lifespan orchestration.

Plugin entry points are discovered process-wide, while successful registrations
are written to the active application runtime. Failures restore the active
runtime snapshots via rollback.
"""

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
    loaded: list[LoadedPlugin] = field(default_factory=list[LoadedPlugin])
    _started: bool = False
    _rollback: Callable[[], None] | None = None

    def start(self) -> None:
        started: list[LoadedPlugin] = []
        try:
            for item in self.loaded:
                for hook in item.context.startup_hooks:
                    hook()
                started.append(item)
            self._started = True
        except Exception:
            # Broad catch: plugin startup hooks are an untrusted boundary.
            for item in reversed(started):
                for hook in reversed(item.context.shutdown_hooks):
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
            for hook in reversed(item.context.shutdown_hooks):
                try:
                    hook()
                except Exception as exc:  # noqa: BLE001 — plugin shutdown boundary
                    logger.warning("Plugin shutdown hook failed: %s", exc)
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
      and except ``*_sandbox`` (unless ``HEDRON_EXTRAS_SANDBOX`` is truthy)
    - empty sequence: load none
    - non-empty: load only named entry points; missing names raise ``HED-PLUGIN-MISSING``

    On failure, registry contributions and Explorer panels are rolled back.
    """
    from hedron_core import __version__ as core_version
    from hedron_core.bundles import restore_bundles, snapshot_bundles

    version = hedron_version or core_version
    rollback = _snapshot_rollback(snapshot_bundles, restore_bundles)
    discovered = list(entry_points) if entry_points is not None else _discover_entry_points()

    try:
        metas, discovered_names = _collect_plugin_metas(
            discovered,
            enabled=enabled,
            version=version,
        )
        _require_enabled_present(enabled, discovered_names)
        order = _topo_sort({name: meta.depends_on for name, (_, meta) in metas.items()})
        loader = PluginLoader(_rollback=rollback)
        _activate_plugins(order, metas, loader)
    except Exception:
        rollback()
        raise

    return loader


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _snapshot_rollback(
    snapshot_bundles: Callable[[], tuple[Any, ...]],
    restore_bundles: Callable[..., None],
) -> Callable[[], None]:
    """Capture process-global plugin contribution state for fail-closed restore."""
    registry_snapshot = snapshot_registry_builder()
    from hedron_core.plugins.explorer import restore_plugin_state, snapshot_plugin_state

    plugin_snapshot = snapshot_plugin_state()
    bundle_snapshot = snapshot_bundles()

    def _rollback() -> None:
        restore_registry_builder(registry_snapshot)
        restore_plugin_state(plugin_snapshot)
        restore_bundles(*bundle_snapshot)

    return _rollback


def _should_load_name(
    name: str,
    *,
    enabled: Sequence[str] | None,
    experimental_env: bool,
    sandbox_env: bool,
) -> bool:
    if enabled is not None:
        return name in enabled
    if not experimental_env and str(name).endswith("_experimental"):
        return False
    return sandbox_env or not str(name).endswith("_sandbox")


def _import_entry_point(ep: Any, name: str) -> Any:
    try:
        return ep.load() if hasattr(ep, "load") else ep
    except Exception as exc:
        # Broad catch: entry-point import is an untrusted plugin boundary.
        raise error(
            HED_PLUGIN_MISSING,
            title="Plugin import failed",
            explanation=f"Could not load plugin {name!r}: {exc}",
            remediation="Install the plugin package or fix the entry point.",
        ) from exc


def _require_plugin_meta(target: Any, name: str) -> PluginMeta:
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
                "Attach PluginMeta(..., hedron_version='>=1.0,<1.1') to the register entry point."
            ),
        )
    return meta


def _require_compatible(meta: PluginMeta, version: str) -> None:
    if compatible_hedron_version(meta.hedron_version, version):
        return
    try:
        SpecifierSet(meta.hedron_version)
        Version(version)
    except (InvalidSpecifier, InvalidVersion) as exc:
        raise error(
            HED_PLUGIN_FAILED,
            title="Plugin version specifier is invalid",
            explanation=(
                f"Plugin {meta.name!r} hedron_version={meta.hedron_version!r} "
                f"or running version {version!r} is not a valid PEP 440 value."
            ),
            remediation="Fix PluginMeta.hedron_version to a PEP 440 specifier set.",
        ) from exc
    raise error(
        HED_PLUGIN_INCOMPATIBLE,
        title="Incompatible plugin",
        explanation=(
            f"Plugin {meta.name!r} requires Hedron {meta.hedron_version}, running {version}."
        ),
        remediation="Upgrade/downgrade the plugin or Hedron.",
    )


def _collect_plugin_metas(
    discovered: Sequence[Any],
    *,
    enabled: Sequence[str] | None,
    version: str,
) -> tuple[dict[str, tuple[Any, PluginMeta]], list[str]]:
    experimental_env = _env_flag("HEDRON_EXPERIMENTAL_UI")
    sandbox_env = _env_flag("HEDRON_EXTRAS_SANDBOX")
    discovered_names: list[str] = []
    metas: dict[str, tuple[Any, PluginMeta]] = {}
    for ep in discovered:
        name = getattr(ep, "name", None) or str(ep)
        discovered_names.append(name)
        if not _should_load_name(
            name,
            enabled=enabled,
            experimental_env=experimental_env,
            sandbox_env=sandbox_env,
        ):
            continue
        target = _import_entry_point(ep, name)
        meta = _require_plugin_meta(target, name)
        _require_compatible(meta, version)
        if meta.name in metas:
            raise error(
                HED_PLUGIN_DUPLICATE,
                title="Duplicate plugin",
                explanation=f"Plugin {meta.name!r} discovered more than once.",
                remediation="Remove the duplicate entry point.",
            )
        metas[meta.name] = (target, meta)
    return metas, discovered_names


def _require_enabled_present(
    enabled: Sequence[str] | None,
    discovered_names: Sequence[str],
) -> None:
    if enabled is None:
        return
    missing = [n for n in enabled if n not in discovered_names]
    if missing:
        raise error(
            HED_PLUGIN_MISSING,
            title="Enabled plugin not found",
            explanation=(
                "Configured plugins were not discovered: " + ", ".join(repr(n) for n in missing)
            ),
            remediation="Install the plugin package or fix [tool.hedron] plugins.",
        )


def _activate_plugins(
    order: Sequence[str],
    metas: dict[str, tuple[Any, PluginMeta]],
    loader: PluginLoader,
) -> None:
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
