"""PluginContext DIP facade — forwards to registry catalogs and explorer types."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from hedron_core.plugins.explorer import (
    FeatureManifest,
    register_diagnostic_owner,
    register_explorer_panel,
    register_feature,
)
from hedron_core.plugins.meta import PluginMeta, StabilityLabel


class PluginContext:
    """Narrow registration surface passed to plugin entry points."""

    def __init__(self, meta: PluginMeta) -> None:
        self.meta = meta
        self._startup: list[Callable[[], None]] = []
        self._shutdown: list[Callable[[], None]] = []

    def register_component(self, **kwargs: Any) -> None:
        from hedron_core.registry import register_component

        register_component(**kwargs)

    def register_browser_module(self, **kwargs: Any) -> None:
        from hedron_core.registry import register_browser_module

        register_browser_module(**kwargs)

    def register_asset(self, **kwargs: Any) -> None:
        from hedron_core.registry import register_asset

        register_asset(**kwargs)

    def register_element_definition(self, **kwargs: Any) -> None:
        from hedron_core.registry import register_element_definition

        # Plugins are third-party unless they opt into first_party=True.
        kwargs.setdefault("first_party", False)
        register_element_definition(**kwargs)

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

    def register_feature(
        self,
        *,
        name: str,
        stability: StabilityLabel = "beta",
        dependencies: Iterable[str] = (),
        assets: Iterable[str] = (),
        a11y_notes: str = "",
        security_notes: str = "",
        http_fallback: bool = True,
        description: str = "",
    ) -> None:
        register_feature(
            FeatureManifest(
                name=name,
                plugin=self.meta.name,
                stability=stability,
                dependencies=tuple(dependencies),
                assets=tuple(assets),
                a11y_notes=a11y_notes,
                security_notes=security_notes,
                http_fallback=http_fallback,
                description=description,
            )
        )

    def on_startup(self, hook: Callable[[], None]) -> None:
        self._startup.append(hook)

    def on_shutdown(self, hook: Callable[[], None]) -> None:
        self._shutdown.append(hook)

    def register_projection_provider(self, provider: Any) -> None:
        from hedron_core.catalog import register_projection_provider

        register_projection_provider(provider, plugin=self.meta.name)

    def register_feature_bundle(self, bundle: Any, *, app_id: str = "") -> None:
        """Include a FeatureBundle through the public 0.46 API. Do not reuse register_feature."""
        from hedron_core.bundles import include_bundle, resolve_feature

        resolved = resolve_feature(bundle)
        include_bundle(
            resolved,
            app_id=app_id or self.meta.name,
            capabilities={self.meta.distribution or self.meta.name: True},
            allow_privileged=False,
        )
