"""Sealable component and resource registry."""

from __future__ import annotations

from hedron_core.registry.addressable import AddressableMeta, register_addressable
from hedron_core.registry.application_style import (
    ApplicationStyleMeta,
    register_application_style,
)
from hedron_core.registry.asset import AssetMeta, register_asset
from hedron_core.registry.browser_module import BrowserModuleMeta, register_browser_module
from hedron_core.registry.builder import (
    Registry,
    RegistryBuilder,
    RegistryBuilderSnapshot,
    fork_registry_builder,
    get_registry,
    reset_registry_for_tests,
    restore_registry_builder,
    seal_registry,
    snapshot_registry_builder,
    use_registry_builder,
)
from hedron_core.registry.component import (
    ComponentMeta,
    component_meta_from_class,
    register_component,
    update_component_meta,
)
from hedron_core.registry.element import ElementDefinitionMeta, register_element_definition
from hedron_core.registry.element import ElementFieldOwnership as ElementFieldOwnership
from hedron_core.registry.route import RouteKind, RouteMeta, register_route
from hedron_core.registry.theme import ThemeMeta, register_theme

__all__ = [
    "AddressableMeta",
    "AssetMeta",
    "ApplicationStyleMeta",
    "BrowserModuleMeta",
    "ElementDefinitionMeta",
    "ElementFieldOwnership",
    "ComponentMeta",
    "RouteKind",
    "RouteMeta",
    "ThemeMeta",
    "Registry",
    "RegistryBuilder",
    "RegistryBuilderSnapshot",
    "fork_registry_builder",
    "get_registry",
    "register_addressable",
    "register_asset",
    "register_application_style",
    "register_browser_module",
    "register_element_definition",
    "register_component",
    "register_route",
    "register_theme",
    "reset_registry_for_tests",
    "restore_registry_builder",
    "seal_registry",
    "snapshot_registry_builder",
    "use_registry_builder",
    "component_meta_from_class",
    "update_component_meta",
]
