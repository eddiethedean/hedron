"""Sealable component registry."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from hedron_core.diagnostics import error
from hedron_core.identifiers import registry_resource_id


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


@dataclass
class RegistryBuilder:
    _components: dict[str, ComponentMeta] = field(default_factory=dict)
    _sealed: bool = False

    def register(self, meta: ComponentMeta) -> None:
        if self._sealed:
            raise error(
                "HED-RENDER-0006",
                title="Registry is sealed",
                explanation="Cannot register components on a sealed registry.",
                remediation="Build a new registry snapshot instead of mutating.",
            )
        key = registry_resource_id("component", meta.logical_id)
        if key in self._components:
            raise error(
                "HED-RENDER-0007",
                title="Duplicate component registration",
                explanation=f"Component {meta.logical_id!r} is already registered.",
                remediation="Use unique logical identifiers.",
            )
        self._components[key] = meta

    def seal(self) -> Registry:
        self._sealed = True
        return Registry(dict(self._components))


@dataclass(frozen=True, slots=True)
class Registry:
    _components: Mapping[str, ComponentMeta]

    def get(self, logical_id: str) -> ComponentMeta | None:
        return self._components.get(registry_resource_id("component", logical_id))

    def components(self) -> Iterable[ComponentMeta]:
        return tuple(sorted(self._components.values(), key=lambda m: m.logical_id))

    def has_route(self, logical_id: str) -> bool:
        meta = self.get(logical_id)
        return bool(meta and meta.route)


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
    return Registry(dict(_builder._components))


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
