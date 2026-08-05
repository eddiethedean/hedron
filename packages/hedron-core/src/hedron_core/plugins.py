"""Plugin metadata and Explorer extension contracts (framework-neutral)."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "ExplorerPanelMeta",
    "PluginCapabilities",
    "PluginMeta",
    "PluginContext",
    "get_explorer_panels",
    "register_explorer_panel",
    "reset_explorer_panels_for_tests",
]


@dataclass(frozen=True, slots=True)
class PluginCapabilities:
    python: bool = True
    browser_js: bool = False
    styles: bool = False
    assets: bool = False
    explorer_panels: bool = False
    routes: bool = False
    remote: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {
            "python": self.python,
            "browser_js": self.browser_js,
            "styles": self.styles,
            "assets": self.assets,
            "explorer_panels": self.explorer_panels,
            "routes": self.routes,
            "remote": self.remote,
        }


@dataclass(frozen=True, slots=True)
class PluginMeta:
    name: str
    version: str
    distribution: str
    hedron_version: str = ">=0.11,<0.12"
    capabilities: PluginCapabilities = field(default_factory=PluginCapabilities)
    depends_on: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "distribution": self.distribution,
            "hedron_version": self.hedron_version,
            "capabilities": self.capabilities.to_dict(),
            "depends_on": list(self.depends_on),
        }


@dataclass(frozen=True, slots=True)
class ExplorerPanelMeta:
    panel_id: str
    title: str
    plugin: str
    description: str = ""
    path: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "panel_id": self.panel_id,
            "title": self.title,
            "plugin": self.plugin,
            "description": self.description,
            "path": self.path,
        }


_panels: dict[str, ExplorerPanelMeta] = {}
_diagnostic_owners: dict[str, str] = {}


def register_explorer_panel(
    *,
    panel_id: str,
    title: str,
    plugin: str,
    description: str = "",
    path: str = "",
) -> None:
    if panel_id in _panels:
        from hedron_core.codes import HED_PLUGIN_DUPLICATE
        from hedron_core.diagnostics import error

        raise error(
            HED_PLUGIN_DUPLICATE,
            title="Duplicate Explorer panel",
            explanation=f"Panel {panel_id!r} is already registered.",
            remediation="Use a unique panel_id per plugin contribution.",
        )
    _panels[panel_id] = ExplorerPanelMeta(
        panel_id=panel_id,
        title=title,
        plugin=plugin,
        description=description,
        path=path,
    )


def get_explorer_panels() -> tuple[ExplorerPanelMeta, ...]:
    return tuple(sorted(_panels.values(), key=lambda p: p.panel_id))


def register_diagnostic_owner(code_prefix: str, owner: str) -> None:
    _diagnostic_owners[code_prefix] = owner


def get_diagnostic_owners() -> Mapping[str, str]:
    return dict(_diagnostic_owners)


def reset_explorer_panels_for_tests() -> None:
    _panels.clear()
    _diagnostic_owners.clear()


class PluginContext:
    """Narrow registration surface passed to plugin entry points."""

    def __init__(self, meta: PluginMeta) -> None:
        self.meta = meta
        self._startup: list[Callable[[], Any]] = []
        self._shutdown: list[Callable[[], Any]] = []

    def register_component(self, **kwargs: Any) -> None:
        from hedron_core.registry import register_component

        register_component(**kwargs)

    def register_browser_module(self, **kwargs: Any) -> None:
        from hedron_core.registry import register_browser_module

        register_browser_module(**kwargs)

    def register_explorer_panel(self, **kwargs: Any) -> None:
        register_explorer_panel(plugin=self.meta.name, **kwargs)

    def register_diagnostic_owner(self, code_prefix: str) -> None:
        register_diagnostic_owner(code_prefix, self.meta.name)

    def on_startup(self, hook: Callable[[], Any]) -> None:
        self._startup.append(hook)

    def on_shutdown(self, hook: Callable[[], Any]) -> None:
        self._shutdown.append(hook)
