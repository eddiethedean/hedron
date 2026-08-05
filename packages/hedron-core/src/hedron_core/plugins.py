"""Plugin metadata and Explorer extension contracts (framework-neutral)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field

from hedron_core.typing_aliases import PluginMetaDict

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
    hedron_version: str = ">=0.13,<0.14"
    capabilities: PluginCapabilities = field(default_factory=PluginCapabilities)
    depends_on: tuple[str, ...] = ()

    def to_dict(self) -> PluginMetaDict:
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
        self._startup: list[Callable[[], None]] = []
        self._shutdown: list[Callable[[], None]] = []

    def register_component(
        self,
        *,
        logical_id: str,
        name: str,
        module: str,
        distribution: str = "hedron-core",
        props_model: str | None = None,
        slots: Mapping[str, str] | None = None,
        examples: Iterable[str] = (),
        docs: str | None = None,
        accessibility_notes: str | None = None,
        styles_path: str | None = None,
        browser_modules: Iterable[str] = (),
        asset_roots: Iterable[str] = (),
        style_symbols: Mapping[str, str] | None = None,
        folder_path: str | None = None,
    ) -> None:
        from hedron_core.registry import register_component

        register_component(
            logical_id=logical_id,
            name=name,
            module=module,
            distribution=distribution,
            props_model=props_model,
            slots=slots,
            examples=examples,
            docs=docs,
            accessibility_notes=accessibility_notes,
            styles_path=styles_path,
            browser_modules=browser_modules,
            asset_roots=asset_roots,
            style_symbols=style_symbols,
            folder_path=folder_path,
        )

    def register_browser_module(
        self,
        *,
        logical_id: str,
        tag_name: str,
        module_path: str,
        observed_attributes: Iterable[str] = (),
        events: Iterable[str] = (),
        shadow_dom: bool = False,
        htmx_lifecycle: bool = True,
    ) -> None:
        from hedron_core.registry import register_browser_module

        register_browser_module(
            logical_id=logical_id,
            tag_name=tag_name,
            module_path=module_path,
            observed_attributes=observed_attributes,
            events=events,
            shadow_dom=shadow_dom,
            htmx_lifecycle=htmx_lifecycle,
        )

    def register_explorer_panel(
        self,
        *,
        panel_id: str,
        title: str,
        description: str = "",
        path: str = "",
    ) -> None:
        register_explorer_panel(
            panel_id=panel_id,
            title=title,
            plugin=self.meta.name,
            description=description,
            path=path,
        )

    def register_diagnostic_owner(self, code_prefix: str) -> None:
        register_diagnostic_owner(code_prefix, self.meta.name)

    def on_startup(self, hook: Callable[[], None]) -> None:
        self._startup.append(hook)

    def on_shutdown(self, hook: Callable[[], None]) -> None:
        self._shutdown.append(hook)
