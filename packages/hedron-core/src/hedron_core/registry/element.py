"""Element-definition registry catalog."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Literal

from hedron_core.element_types import ElementFieldOwnership as ElementFieldOwnership

OwnershipMode = Literal["controlled", "local", "draft", "preference"]


@dataclass(frozen=True, slots=True)
class ElementDefinitionMeta:
    """Versioned Web Component ABI record (RFC-0060 / phase 0.36)."""

    logical_id: str
    tag_name: str
    abi_version: int
    module_asset_id: str
    attributes: tuple[str, ...] = ()
    structured_inputs: Mapping[str, str] = field(default_factory=dict)
    properties: tuple[str, ...] = ()
    methods: tuple[str, ...] = ()
    state_ownership: tuple[ElementFieldOwnership, ...] = ()
    events: tuple[str, ...] = ()
    dom_policy: str = "light"
    server_regions: tuple[str, ...] = ()
    form_contract: Mapping[str, object] | None = None  # reserved stub in 0.36
    a11y_contract: Mapping[str, str] = field(default_factory=dict)
    style_contract: Mapping[str, str] = field(default_factory=dict)
    resources: tuple[str, ...] = ()
    lifecycle: Mapping[str, str] = field(default_factory=dict)
    fallback: Mapping[str, str] = field(default_factory=dict)
    parts: tuple[str, ...] = ()
    slots: Mapping[str, str] = field(default_factory=dict)
    tokens: tuple[str, ...] = ()
    maturity: str = "Supported"
    compatibility: Mapping[str, str] = field(default_factory=dict)
    first_party: bool = True


def register_element_definition(
    *,
    logical_id: str,
    tag_name: str,
    abi_version: int,
    module_asset_id: str,
    attributes: Iterable[str] = (),
    structured_inputs: Mapping[str, str] | None = None,
    properties: Iterable[str] = (),
    methods: Iterable[str] = (),
    state_ownership: Iterable[ElementFieldOwnership] = (),
    events: Iterable[str] = (),
    dom_policy: str = "light",
    server_regions: Iterable[str] = (),
    form_contract: Mapping[str, object] | None = None,
    a11y_contract: Mapping[str, str] | None = None,
    style_contract: Mapping[str, str] | None = None,
    resources: Iterable[str] = (),
    lifecycle: Mapping[str, str] | None = None,
    fallback: Mapping[str, str] | None = None,
    parts: Iterable[str] = (),
    slots: Mapping[str, str] | None = None,
    tokens: Iterable[str] = (),
    maturity: str = "Supported",
    compatibility: Mapping[str, str] | None = None,
    first_party: bool = True,
) -> None:
    from hedron_core.registry.builder import active_builder

    active_builder().register_element_definition(
        ElementDefinitionMeta(
            logical_id=logical_id,
            tag_name=tag_name,
            abi_version=abi_version,
            module_asset_id=module_asset_id,
            attributes=tuple(attributes),
            structured_inputs=dict(structured_inputs or {}),
            properties=tuple(properties),
            methods=tuple(methods),
            state_ownership=tuple(state_ownership),
            events=tuple(events),
            dom_policy=dom_policy,
            server_regions=tuple(server_regions),
            form_contract=dict(form_contract) if form_contract is not None else None,
            a11y_contract=dict(a11y_contract or {}),
            style_contract=dict(style_contract or {}),
            resources=tuple(resources),
            lifecycle=dict(lifecycle or {}),
            fallback=dict(fallback or {}),
            parts=tuple(parts),
            slots=dict(slots or {}),
            tokens=tuple(tokens),
            maturity=maturity,
            compatibility=dict(compatibility or {}),
            first_party=first_party,
        )
    )
