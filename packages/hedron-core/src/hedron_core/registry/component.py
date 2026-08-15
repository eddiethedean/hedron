"""Component registry catalog."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, fields


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


_COMPONENT_UPDATE_KEYS = frozenset(f.name for f in fields(ComponentMeta)) - {"logical_id"}


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
    from hedron_core.registry.builder import active_builder

    active_builder().register(
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


def update_component_meta(logical_id: str, **updates: object) -> None:
    from hedron_core.registry.builder import active_builder

    active_builder().update_component(logical_id, **updates)


def component_meta_from_class(cls: type[object]) -> ComponentMeta:
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
