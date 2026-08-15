"""Plugin capability and identity metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from hedron_core.typing_aliases import PluginMetaDict

StabilityLabel = Literal["stable", "beta", "experimental", "recipe"]


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
    hedron_version: str
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
