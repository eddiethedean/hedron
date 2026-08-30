"""Mutable registry builder, sealed snapshot, and process-wide gate."""

from __future__ import annotations

from collections.abc import Generator, Iterable, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field, replace
from typing import TypedDict

from hedron_core.diagnostics import error
from hedron_core.element_form import validate_form_contract
from hedron_core.element_types import validate_field_ownership
from hedron_core.identifiers import registry_resource_id
from hedron_core.registry.addressable import AddressableMeta
from hedron_core.registry.application_style import ApplicationStyleMeta
from hedron_core.registry.asset import AssetMeta
from hedron_core.registry.browser_module import BrowserModuleMeta
from hedron_core.registry.component import COMPONENT_UPDATE_KEYS, ComponentMeta
from hedron_core.registry.element import ElementDefinitionMeta
from hedron_core.registry.route import RouteKind, RouteMeta
from hedron_core.registry.theme import ThemeMeta

__all__ = [
    "Registry",
    "RegistryBuilder",
    "RegistryBuilderSnapshot",
    "active_builder",
    "bind_compatibility_builder",
    "fork_registry_builder",
    "get_registry",
    "reset_registry_for_tests",
    "restore_registry_builder",
    "seal_registry",
    "snapshot_registry_builder",
    "use_registry_builder",
]


class RegistryBuilderSnapshot(TypedDict):
    """Typed rollback payload for ``snapshot_registry_builder`` / ``restore_registry_builder``."""

    components: dict[str, ComponentMeta]
    addressables: dict[str, AddressableMeta]
    routes: dict[str, RouteMeta]
    themes: dict[str, ThemeMeta]
    assets: dict[str, AssetMeta]
    browser_modules: dict[str, BrowserModuleMeta]
    element_definitions: dict[str, ElementDefinitionMeta]
    application_styles: dict[str, ApplicationStyleMeta]


@dataclass(slots=True)
class RegistryBuilder:
    _components: dict[str, ComponentMeta] = field(default_factory=dict[str, ComponentMeta])
    _addressables: dict[str, AddressableMeta] = field(default_factory=dict[str, AddressableMeta])
    _routes: dict[str, RouteMeta] = field(default_factory=dict[str, RouteMeta])
    _themes: dict[str, ThemeMeta] = field(default_factory=dict[str, ThemeMeta])
    _assets: dict[str, AssetMeta] = field(default_factory=dict[str, AssetMeta])
    _browser_modules: dict[str, BrowserModuleMeta] = field(
        default_factory=dict[str, BrowserModuleMeta]
    )
    _element_definitions: dict[str, ElementDefinitionMeta] = field(
        default_factory=dict[str, ElementDefinitionMeta]
    )
    _application_styles: dict[str, ApplicationStyleMeta] = field(
        default_factory=dict[str, ApplicationStyleMeta]
    )
    _sealed: bool = False

    def register(self, meta: ComponentMeta) -> None:
        self._ensure_open()
        key = registry_resource_id("component", meta.logical_id)
        if key in self._components:
            raise error(
                "HED-RENDER-0007",
                title="Duplicate component registration",
                explanation=f"Component {meta.logical_id!r} is already registered.",
                remediation="Use unique logical identifiers.",
            )
        self._components[key] = meta

    def register_addressable(self, meta: AddressableMeta) -> None:
        self._ensure_open()
        key = registry_resource_id("addressable", meta.logical_id)
        if key in self._addressables:
            raise error(
                "HED-RENDER-0007",
                title="Duplicate addressable registration",
                explanation=f"Addressable {meta.logical_id!r} is already registered.",
                remediation="Use unique logical identifiers.",
            )
        self._addressables[key] = meta

    def register_route(self, meta: RouteMeta) -> None:
        self._ensure_open()
        key = registry_resource_id(meta.kind, meta.logical_id)
        if key in self._routes or any(
            r.operation_id == meta.operation_id for r in self._routes.values()
        ):
            raise error(
                "HED-ROUTE-0001",
                title="Duplicate route registration",
                explanation=(
                    f"Route {meta.logical_id!r} or operation_id "
                    f"{meta.operation_id!r} collides with an existing entry."
                ),
                remediation="Use unique route names and operation IDs.",
            )
        self._routes[key] = meta

    def register_theme(self, meta: ThemeMeta) -> None:
        self._ensure_open()
        key = registry_resource_id("theme", meta.logical_id)
        if key in self._themes:
            raise error(
                "HED-THEME-0004",
                title="Duplicate theme registration",
                explanation=f"Theme {meta.logical_id!r} is already registered.",
                remediation="Use unique theme names.",
            )
        self._themes[key] = meta

    def register_asset(self, meta: AssetMeta) -> None:
        self._ensure_open()
        key = registry_resource_id("asset", meta.logical_id)
        if key in self._assets:
            raise error(
                "HED-ASSET-0005",
                title="Duplicate asset registration",
                explanation=f"Asset {meta.logical_id!r} is already registered.",
                remediation="Use unique asset logical identifiers.",
            )
        self._assets[key] = meta

    def register_application_style(self, meta: ApplicationStyleMeta) -> None:
        self._ensure_open()
        key = registry_resource_id("application-style", meta.logical_id)
        if key in self._application_styles:
            raise error(
                "HED-STYLE-APP-0001",
                title="Duplicate application stylesheet",
                explanation=f"Application stylesheet {meta.name!r} is already registered.",
                remediation="Use one registration per stylesheet name.",
            )
        self._application_styles[key] = meta

    def register_browser_module(self, meta: BrowserModuleMeta) -> None:
        self._ensure_open()
        key = registry_resource_id("asset", meta.logical_id)
        if key in self._browser_modules:
            raise error(
                "HED-ASSET-0010",
                title="Duplicate browser module registration",
                explanation=f"Browser module {meta.logical_id!r} is already registered.",
                remediation="Use unique browser module identifiers.",
            )
        for existing in self._browser_modules.values():
            if existing.tag_name == meta.tag_name:
                raise error(
                    "HED-ASSET-0010",
                    title="Duplicate custom element tag",
                    explanation=f"Custom element tag {meta.tag_name!r} is already registered.",
                    remediation="Use a unique hyphenated custom element name.",
                )
        self._browser_modules[key] = meta

    def register_element_definition(self, meta: ElementDefinitionMeta) -> None:
        self._ensure_open()
        validated_ownership = tuple(
            validate_field_ownership(field) for field in meta.state_ownership
        )
        if validated_ownership != meta.state_ownership:
            meta = replace(meta, state_ownership=validated_ownership)
        key = registry_resource_id("element", meta.logical_id)
        if "-" not in meta.tag_name:
            raise error(
                "HED-ELEMENT-0003",
                title="Invalid element tag",
                explanation=f"Element tag {meta.tag_name!r} must contain a hyphen.",
                remediation="Use a hyphenated custom element name.",
            )
        if meta.first_party and not meta.tag_name.startswith("hedron-"):
            raise error(
                "HED-ELEMENT-0003",
                title="First-party element naming violation",
                explanation=f"First-party tag {meta.tag_name!r} must use the hedron- prefix.",
                remediation="Reserve hedron- for first-party elements.",
            )
        if meta.abi_version < 1:
            raise error(
                "HED-ELEMENT-0002",
                title="Invalid element ABI version",
                explanation=f"ABI version {meta.abi_version} is not supported.",
                remediation="Use a positive integer ABI major.",
            )
        existing = self._element_definitions.get(key)
        if existing is not None:
            if existing == meta:
                return  # idempotent same-definition registration
            raise error(
                "HED-ELEMENT-0001",
                title="Element definition conflict",
                explanation=(
                    f"Element {meta.logical_id!r} already registered with a different definition."
                ),
                remediation=(
                    "Register a compatible identical definition or choose a new logical id."
                ),
            )
        for other in self._element_definitions.values():
            if other.tag_name != meta.tag_name or other.logical_id == meta.logical_id:
                continue
            if other.abi_version != meta.abi_version:
                raise error(
                    "HED-ELEMENT-0002",
                    title="Incompatible element ABI",
                    explanation=(
                        f"Tag {meta.tag_name!r} ABI {meta.abi_version} conflicts with "
                        f"registered ABI {other.abi_version}."
                    ),
                    remediation="Align markup and module ABI majors or use a new tag.",
                )
            if other != meta:
                raise error(
                    "HED-ELEMENT-0001",
                    title="Element tag conflict",
                    explanation=f"Tag {meta.tag_name!r} is already owned by {other.logical_id!r}.",
                    remediation="Use a unique tag or compatible same-definition registration.",
                )
        validate_form_contract(meta.form_contract, tag_name=meta.tag_name)
        self._element_definitions[key] = meta

    def update_component(self, logical_id: str, **updates: object) -> None:
        self._ensure_open()
        key = registry_resource_id("component", logical_id)
        existing = self._components.get(key)
        if existing is None:
            raise error(
                "HED-RENDER-0007",
                title="Unknown component",
                explanation=f"Component {logical_id!r} is not registered.",
                remediation="Register the component before updating metadata.",
            )
        unknown = set(updates) - COMPONENT_UPDATE_KEYS
        if unknown:
            raise TypeError(f"Unknown ComponentMeta fields: {sorted(unknown)}")
        self._components[key] = replace(existing, **updates)

    @property
    def is_sealed(self) -> bool:
        """Return whether this builder no longer accepts registrations."""
        return self._sealed

    def snapshot(self) -> RegistryBuilderSnapshot:
        """Return independent copies of every mutable registry collection."""
        return {
            "components": dict(self._components),
            "addressables": dict(self._addressables),
            "routes": dict(self._routes),
            "themes": dict(self._themes),
            "assets": dict(self._assets),
            "browser_modules": dict(self._browser_modules),
            "element_definitions": dict(self._element_definitions),
            "application_styles": dict(self._application_styles),
        }

    def restore(self, snapshot: RegistryBuilderSnapshot) -> None:
        """Restore a previously captured snapshot while the builder is open."""
        self._ensure_open()
        self._components = dict(snapshot["components"])
        self._addressables = dict(snapshot["addressables"])
        self._routes = dict(snapshot["routes"])
        self._themes = dict(snapshot["themes"])
        self._assets = dict(snapshot["assets"])
        self._browser_modules = dict(snapshot["browser_modules"])
        self._element_definitions = dict(snapshot.get("element_definitions", {}))
        self._application_styles = dict(snapshot.get("application_styles", {}))

    def registry_snapshot(self) -> Registry:
        """Build an immutable registry view without sealing the builder."""
        return Registry(
            dict(self._components),
            dict(self._addressables),
            dict(self._routes),
            dict(self._themes),
            dict(self._assets),
            dict(self._browser_modules),
            dict(self._element_definitions),
            dict(self._application_styles),
        )

    def fork(self) -> RegistryBuilder:
        """Create an open builder seeded from this builder's current snapshot.

        Application runtimes use this to inherit package registrations without
        sharing mutable route/plugin state with another application.
        """
        snapshot = self.snapshot()
        return RegistryBuilder(
            _components=dict(snapshot["components"]),
            _addressables=dict(snapshot["addressables"]),
            _routes=dict(snapshot["routes"]),
            _themes=dict(snapshot["themes"]),
            _assets=dict(snapshot["assets"]),
            _browser_modules=dict(snapshot["browser_modules"]),
            _element_definitions=dict(snapshot["element_definitions"]),
            _application_styles=dict(snapshot["application_styles"]),
        )

    def seal(self) -> Registry:
        self._sealed = True
        return Registry(
            dict(self._components),
            dict(self._addressables),
            dict(self._routes),
            dict(self._themes),
            dict(self._assets),
            dict(self._browser_modules),
            dict(self._element_definitions),
            dict(self._application_styles),
        )

    def _ensure_open(self) -> None:
        if self._sealed:
            raise error(
                "HED-RENDER-0006",
                title="Registry is sealed",
                explanation="Cannot register on a sealed registry.",
                remediation="Build a new registry snapshot instead of mutating.",
            )


@dataclass(frozen=True, slots=True)
class Registry:
    _components: Mapping[str, ComponentMeta]
    _addressables: Mapping[str, AddressableMeta] = field(default_factory=dict[str, AddressableMeta])
    _routes: Mapping[str, RouteMeta] = field(default_factory=dict[str, RouteMeta])
    _themes: Mapping[str, ThemeMeta] = field(default_factory=dict[str, ThemeMeta])
    _assets: Mapping[str, AssetMeta] = field(default_factory=dict[str, AssetMeta])
    _browser_modules: Mapping[str, BrowserModuleMeta] = field(
        default_factory=dict[str, BrowserModuleMeta]
    )
    _element_definitions: Mapping[str, ElementDefinitionMeta] = field(
        default_factory=dict[str, ElementDefinitionMeta]
    )
    _application_styles: Mapping[str, ApplicationStyleMeta] = field(
        default_factory=dict[str, ApplicationStyleMeta]
    )

    def get(self, logical_id: str) -> ComponentMeta | None:
        return self._components.get(registry_resource_id("component", logical_id))

    def components(self) -> Iterable[ComponentMeta]:
        return tuple(sorted(self._components.values(), key=lambda m: m.logical_id))

    def get_addressable(self, logical_id: str) -> AddressableMeta | None:
        return self._addressables.get(registry_resource_id("addressable", logical_id))

    def addressables(self) -> Iterable[AddressableMeta]:
        return tuple(sorted(self._addressables.values(), key=lambda m: m.logical_id))

    def get_route(self, kind: RouteKind, logical_id: str) -> RouteMeta | None:
        return self._routes.get(registry_resource_id(kind, logical_id))

    def routes(self) -> Iterable[RouteMeta]:
        return tuple(sorted(self._routes.values(), key=lambda m: m.operation_id))

    def has_route(self, logical_id: str) -> bool:
        meta = self.get(logical_id)
        if meta and meta.route:
            return True
        return any(r.logical_id == logical_id for r in self._routes.values())

    def get_theme(self, name: str) -> ThemeMeta | None:
        return self._themes.get(registry_resource_id("theme", name))

    def themes(self) -> Iterable[ThemeMeta]:
        return tuple(sorted(self._themes.values(), key=lambda m: m.logical_id))

    def assets(self) -> Iterable[AssetMeta]:
        return tuple(sorted(self._assets.values(), key=lambda m: m.logical_id))

    def browser_modules(self) -> Iterable[BrowserModuleMeta]:
        return tuple(sorted(self._browser_modules.values(), key=lambda m: m.logical_id))

    def get_element_definition(self, logical_id: str) -> ElementDefinitionMeta | None:
        return self._element_definitions.get(registry_resource_id("element", logical_id))

    def element_definitions(self) -> Iterable[ElementDefinitionMeta]:
        return tuple(sorted(self._element_definitions.values(), key=lambda m: m.logical_id))

    def application_styles(self) -> Iterable[ApplicationStyleMeta]:
        return tuple(sorted(self._application_styles.values(), key=lambda m: m.logical_id))


_builder = RegistryBuilder()
_active: Registry | None = None
_compatibility_builder: RegistryBuilder | None = None
_scoped_builder: ContextVar[RegistryBuilder | None] = ContextVar(
    "hedron_registry_builder", default=None
)


def active_builder() -> RegistryBuilder:
    return _scoped_builder.get() or _compatibility_builder or _builder


def bind_compatibility_builder(builder: RegistryBuilder | None) -> None:
    """Bind the legacy no-context helpers to the most recently attached app.

    This is intentionally a migration bridge. New code should use
    ``use_registry_builder`` or an application runtime explicitly.
    """
    global _compatibility_builder
    _compatibility_builder = builder


def fork_registry_builder() -> RegistryBuilder:
    """Return an open application builder seeded from the process template."""
    return _builder.fork()


@contextmanager
def use_registry_builder(builder: RegistryBuilder) -> Generator[None, None, None]:
    """Temporarily make ``builder`` the active registration target."""
    token = _scoped_builder.set(builder)
    try:
        yield
    finally:
        _scoped_builder.reset(token)


def seal_registry() -> Registry:
    """Seal the builder. Idempotent: returns the existing snapshot if already sealed."""
    scoped = _scoped_builder.get() or _compatibility_builder
    if scoped is not None:
        return scoped.seal()
    global _active
    if _builder.is_sealed and _active is not None:
        return _active
    _active = _builder.seal()
    return _active


def get_registry() -> Registry:
    """Return the sealed registry, or an unsealed snapshot of current registrations."""
    scoped = _scoped_builder.get() or _compatibility_builder
    if scoped is not None:
        return scoped.registry_snapshot()
    global _active
    if _active is not None:
        return _active
    return _builder.registry_snapshot()


def snapshot_registry_builder() -> RegistryBuilderSnapshot:
    """Capture mutable builder maps for plugin-load rollback."""
    return active_builder().snapshot()


def restore_registry_builder(snapshot: RegistryBuilderSnapshot) -> None:
    """Restore builder maps from ``snapshot_registry_builder``."""
    active_builder().restore(snapshot)


def reset_registry_for_tests() -> None:
    """Test helper: replace the module-level builder/registry."""
    global _builder, _active, _compatibility_builder
    _builder = RegistryBuilder()
    _active = None
    _compatibility_builder = None
    from hedron_core.updates import reset_handles_for_tests

    reset_handles_for_tests()
