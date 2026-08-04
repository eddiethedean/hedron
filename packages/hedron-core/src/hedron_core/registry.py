"""Sealable component and resource registry."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from hedron_core.diagnostics import error
from hedron_core.identifiers import registry_resource_id

__all__ = [
    "AddressableMeta",
    "AssetMeta",
    "BrowserModuleMeta",
    "ComponentMeta",
    "RouteMeta",
    "ThemeMeta",
    "Registry",
    "RegistryBuilder",
    "get_registry",
    "register_addressable",
    "register_asset",
    "register_browser_module",
    "register_component",
    "register_route",
    "register_theme",
    "reset_registry_for_tests",
    "restore_registry_builder",
    "seal_registry",
    "snapshot_registry_builder",
    "component_meta_from_class",
    "update_component_meta",
]


@dataclass(frozen=True, slots=True)
class ComponentMeta:
    logical_id: str
    name: str
    module: str
    distribution: str
    props_model: str | None
    slots: Mapping[str, str]
    examples: tuple[str, ...] = ()
    docs: str | None = None
    route: str | None = None
    accessibility_notes: str | None = None
    styles_path: str | None = None
    browser_modules: tuple[str, ...] = ()
    asset_roots: tuple[str, ...] = ()
    style_symbols: Mapping[str, str] = field(default_factory=dict)
    folder_path: str | None = None


@dataclass(frozen=True, slots=True)
class AddressableMeta:
    logical_id: str
    name: str
    module: str
    distribution: str
    methods: tuple[str, ...]
    include_in_schema: bool
    cache_private: bool
    tags: tuple[str, ...]
    docs: str | None
    factory: Callable[..., Any] | None = None
    route: str | None = None


@dataclass(frozen=True, slots=True)
class RouteMeta:
    """Adapter-populated page/action/component route metadata."""

    kind: str  # page | component | action
    logical_id: str
    name: str
    path: str
    methods: tuple[str, ...]
    operation_id: str
    include_in_schema: bool
    module: str
    tags: tuple[str, ...] = ()
    docs: str | None = None
    endpoint: Callable[..., Any] | None = None
    htmx_inference: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ThemeMeta:
    logical_id: str
    name: str
    tokens: Mapping[str, str]
    modes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    variants: Mapping[str, Mapping[str, str]] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AssetMeta:
    logical_id: str
    kind: str
    path: str
    digest: str
    content_type: str
    attributes: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BrowserModuleMeta:
    logical_id: str
    tag_name: str
    module_path: str
    observed_attributes: tuple[str, ...] = ()
    events: tuple[str, ...] = ()
    shadow_dom: bool = False
    htmx_lifecycle: bool = True


@dataclass
class RegistryBuilder:
    _components: dict[str, ComponentMeta] = field(default_factory=dict)
    _addressables: dict[str, AddressableMeta] = field(default_factory=dict)
    _routes: dict[str, RouteMeta] = field(default_factory=dict)
    _themes: dict[str, ThemeMeta] = field(default_factory=dict)
    _assets: dict[str, AssetMeta] = field(default_factory=dict)
    _browser_modules: dict[str, BrowserModuleMeta] = field(default_factory=dict)
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

    def update_component(self, logical_id: str, **updates: Any) -> None:
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
        data = {
            "logical_id": existing.logical_id,
            "name": existing.name,
            "module": existing.module,
            "distribution": existing.distribution,
            "props_model": existing.props_model,
            "slots": dict(existing.slots),
            "examples": existing.examples,
            "docs": existing.docs,
            "route": existing.route,
            "accessibility_notes": existing.accessibility_notes,
            "styles_path": existing.styles_path,
            "browser_modules": existing.browser_modules,
            "asset_roots": existing.asset_roots,
            "style_symbols": dict(existing.style_symbols),
            "folder_path": existing.folder_path,
        }
        data.update(updates)
        self._components[key] = ComponentMeta(**data)  # type: ignore[arg-type]

    def seal(self) -> Registry:
        self._sealed = True
        return Registry(
            dict(self._components),
            dict(self._addressables),
            dict(self._routes),
            dict(self._themes),
            dict(self._assets),
            dict(self._browser_modules),
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
    _addressables: Mapping[str, AddressableMeta] = field(default_factory=dict)
    _routes: Mapping[str, RouteMeta] = field(default_factory=dict)
    _themes: Mapping[str, ThemeMeta] = field(default_factory=dict)
    _assets: Mapping[str, AssetMeta] = field(default_factory=dict)
    _browser_modules: Mapping[str, BrowserModuleMeta] = field(default_factory=dict)

    def get(self, logical_id: str) -> ComponentMeta | None:
        return self._components.get(registry_resource_id("component", logical_id))

    def components(self) -> Iterable[ComponentMeta]:
        return tuple(sorted(self._components.values(), key=lambda m: m.logical_id))

    def get_addressable(self, logical_id: str) -> AddressableMeta | None:
        return self._addressables.get(registry_resource_id("addressable", logical_id))

    def addressables(self) -> Iterable[AddressableMeta]:
        return tuple(sorted(self._addressables.values(), key=lambda m: m.logical_id))

    def get_route(self, kind: str, logical_id: str) -> RouteMeta | None:
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


_builder = RegistryBuilder()
_active: Registry | None = None


def register_component(
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
    _builder.register(
        ComponentMeta(
            logical_id=logical_id,
            name=name,
            module=module,
            distribution=distribution,
            props_model=props_model,
            slots=dict(slots or {}),
            examples=tuple(examples),
            docs=docs,
            route=None,
            accessibility_notes=accessibility_notes,
            styles_path=styles_path,
            browser_modules=tuple(browser_modules),
            asset_roots=tuple(asset_roots),
            style_symbols=dict(style_symbols or {}),
            folder_path=folder_path,
        )
    )


def update_component_meta(logical_id: str, **updates: Any) -> None:
    _builder.update_component(logical_id, **updates)


def register_addressable(
    *,
    logical_id: str,
    name: str,
    module: str,
    distribution: str = "hedron-core",
    methods: tuple[str, ...] = ("GET",),
    include_in_schema: bool = False,
    cache_private: bool = True,
    tags: tuple[str, ...] = (),
    docs: str | None = None,
    factory: Callable[..., Any] | None = None,
    route: str | None = None,
) -> None:
    _builder.register_addressable(
        AddressableMeta(
            logical_id=logical_id,
            name=name,
            module=module,
            distribution=distribution,
            methods=methods,
            include_in_schema=include_in_schema,
            cache_private=cache_private,
            tags=tags,
            docs=docs,
            factory=factory,
            route=route,
        )
    )


def register_route(
    *,
    kind: str,
    logical_id: str,
    name: str,
    path: str,
    methods: tuple[str, ...],
    operation_id: str,
    include_in_schema: bool,
    module: str,
    tags: tuple[str, ...] = (),
    docs: str | None = None,
    endpoint: Callable[..., Any] | None = None,
    htmx_inference: Mapping[str, str] | None = None,
) -> None:
    _builder.register_route(
        RouteMeta(
            kind=kind,
            logical_id=logical_id,
            name=name,
            path=path,
            methods=methods,
            operation_id=operation_id,
            include_in_schema=include_in_schema,
            module=module,
            tags=tags,
            docs=docs,
            endpoint=endpoint,
            htmx_inference=dict(htmx_inference or {}),
        )
    )


def register_theme(
    *,
    logical_id: str,
    name: str,
    tokens: Mapping[str, str],
    modes: Mapping[str, Mapping[str, str]] | None = None,
    variants: Mapping[str, Mapping[str, str]] | None = None,
) -> None:
    _builder.register_theme(
        ThemeMeta(
            logical_id=logical_id,
            name=name,
            tokens=dict(tokens),
            modes={k: dict(v) for k, v in (modes or {}).items()},
            variants={k: dict(v) for k, v in (variants or {}).items()},
        )
    )


def register_asset(
    *,
    logical_id: str,
    kind: str,
    path: str,
    digest: str,
    content_type: str,
    attributes: Mapping[str, str] | None = None,
) -> None:
    _builder.register_asset(
        AssetMeta(
            logical_id=logical_id,
            kind=kind,
            path=path,
            digest=digest,
            content_type=content_type,
            attributes=dict(attributes or {}),
        )
    )


def register_browser_module(
    *,
    logical_id: str,
    tag_name: str,
    module_path: str,
    observed_attributes: Iterable[str] = (),
    events: Iterable[str] = (),
    shadow_dom: bool = False,
    htmx_lifecycle: bool = True,
) -> None:
    if "-" not in tag_name:
        raise error(
            "HED-ASSET-0011",
            title="Invalid custom element tag",
            explanation=f"Custom element tag {tag_name!r} must contain a hyphen.",
            remediation="Use a hyphenated custom element name.",
        )
    _builder.register_browser_module(
        BrowserModuleMeta(
            logical_id=logical_id,
            tag_name=tag_name,
            module_path=module_path,
            observed_attributes=tuple(observed_attributes),
            events=tuple(events),
            shadow_dom=shadow_dom,
            htmx_lifecycle=htmx_lifecycle,
        )
    )


def seal_registry() -> Registry:
    """Seal the builder. Idempotent: returns the existing snapshot if already sealed."""
    global _active
    if _builder._sealed and _active is not None:
        return _active
    _active = _builder.seal()
    return _active


def get_registry() -> Registry:
    """Return the sealed registry, or an unsealed snapshot of current registrations."""
    global _active
    if _active is not None:
        return _active
    return Registry(
        dict(_builder._components),
        dict(_builder._addressables),
        dict(_builder._routes),
        dict(_builder._themes),
        dict(_builder._assets),
        dict(_builder._browser_modules),
    )


def snapshot_registry_builder() -> dict[str, dict[str, Any]]:
    """Capture mutable builder maps for plugin-load rollback."""
    return {
        "components": dict(_builder._components),
        "addressables": dict(_builder._addressables),
        "routes": dict(_builder._routes),
        "themes": dict(_builder._themes),
        "assets": dict(_builder._assets),
        "browser_modules": dict(_builder._browser_modules),
    }


def restore_registry_builder(snapshot: dict[str, dict[str, Any]]) -> None:
    """Restore builder maps from ``snapshot_registry_builder``."""
    if _builder._sealed:
        raise error(
            "HED-RENDER-0006",
            title="Registry is sealed",
            explanation="Cannot restore builder state on a sealed registry.",
            remediation="Roll back plugins before seal_registry().",
        )
    _builder._components = dict(snapshot["components"])
    _builder._addressables = dict(snapshot["addressables"])
    _builder._routes = dict(snapshot["routes"])
    _builder._themes = dict(snapshot["themes"])
    _builder._assets = dict(snapshot["assets"])
    _builder._browser_modules = dict(snapshot["browser_modules"])


def reset_registry_for_tests() -> None:
    """Test helper: replace the module-level builder/registry."""
    global _builder, _active
    _builder = RegistryBuilder()
    _active = None


def component_meta_from_class(cls: type[Any]) -> ComponentMeta:
    logical_id = (
        f"{getattr(cls, 'distribution', 'hedron-core')}:"
        f"{cls.__module__}.{getattr(cls, 'logical_name', cls.__name__)}"
    )
    props_type = getattr(cls, "props_type", None)
    return ComponentMeta(
        logical_id=logical_id,
        name=getattr(cls, "logical_name", cls.__name__) or cls.__name__,
        module=cls.__module__,
        distribution=getattr(cls, "distribution", "hedron-core"),
        props_model=props_type.__name__ if props_type else None,
        slots=dict(getattr(cls, "slots", {}) or {}),
        route=None,
    )
