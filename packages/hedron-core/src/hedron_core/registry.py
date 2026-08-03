"""Sealable component and resource registry."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from hedron_core.diagnostics import error
from hedron_core.identifiers import registry_resource_id

__all__ = [
    "AddressableMeta",
    "ComponentMeta",
    "RouteMeta",
    "Registry",
    "RegistryBuilder",
    "get_registry",
    "register_addressable",
    "register_component",
    "register_route",
    "reset_registry_for_tests",
    "seal_registry",
    "component_meta_from_class",
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


@dataclass
class RegistryBuilder:
    _components: dict[str, ComponentMeta] = field(default_factory=dict)
    _addressables: dict[str, AddressableMeta] = field(default_factory=dict)
    _routes: dict[str, RouteMeta] = field(default_factory=dict)
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

    def seal(self) -> Registry:
        self._sealed = True
        return Registry(
            dict(self._components),
            dict(self._addressables),
            dict(self._routes),
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
        )
    )


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
    )


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
