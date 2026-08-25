"""App-scoped registry and interaction binding for HDJ (phase 0.66)."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from importlib import import_module
from types import MappingProxyType
from typing import Any, cast

from hedron_core import AssetRef, Component
from hedron_core.catalog import compile_interaction_catalog
from hedron_core.codes import HED_PROJECTION_0005, HED_UPDATE_0003
from hedron_core.diagnostics import error
from hedron_core.registry import Registry, get_registry
from hedron_core.type_schema import type_schema_from_descriptor
from hedron_core.typing_aliases import JsonObject
from hedron_core.updates import (
    BaseHandleDescriptor,
    descriptor_fingerprint,
    list_handle_descriptors,
)
from hedron_jinja.providers import ProviderManifest

_ALIAS_RE = re.compile(r"^[A-Z][A-Za-z0-9_.-]*$")


@dataclass(frozen=True, slots=True)
class ApplicationStyleFact:
    """Redacted, render-safe facts for one registered application stylesheet."""

    logical_id: str
    name: str
    owner: str
    scope: str | None
    layer: str
    global_: bool
    media: tuple[str, ...]
    digest: str
    provenance: str

    def as_mapping(self) -> JsonObject:
        return {
            "logical_id": self.logical_id,
            "name": self.name,
            "owner": self.owner,
            "scope": self.scope,
            "layer": self.layer,
            "global": self.global_,
            "media": list(self.media),
            "digest": self.digest,
            "provenance": self.provenance,
        }


def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class JinjaBinding:
    """One immutable application projection consumed by :class:`HedronJinja`.

    Component classes and live handle objects remain explicit trusted inputs. Registry
    metadata, assets, themes, and application-style facts may be captured from the
    sealed core registry without importing ``hedron`` or a framework adapter.
    """

    app_id: str
    components: Mapping[str, type[Component[Any]]] = field(default_factory=dict)
    assets: Mapping[str, AssetRef] = field(default_factory=dict)
    handles: Mapping[str, object] = field(default_factory=dict)
    providers: Mapping[str, ProviderManifest] = field(default_factory=dict)
    themes: tuple[str, ...] = ()
    application_styles: tuple[ApplicationStyleFact, ...] = ()

    def __post_init__(self) -> None:
        token = self.app_id.strip()
        if not token:
            raise ValueError("JinjaBinding.app_id must be non-empty")
        object.__setattr__(self, "app_id", token)
        for alias, component in self.components.items():
            if not _ALIAS_RE.fullmatch(alias):
                raise ValueError(f"invalid HDJ component alias: {alias!r}")
            if not isinstance(component, type) or not issubclass(component, Component):
                raise TypeError(f"HDJ component {alias!r} must be a Component subclass")
        for logical_id, handle in self.handles.items():
            actual = getattr(handle, "logical_id", None)
            handle_app_id = getattr(handle, "app_id", self.app_id)
            if actual != logical_id:
                raise ValueError(
                    f"handle mapping key {logical_id!r} does not match logical_id {actual!r}"
                )
            if handle_app_id != self.app_id:
                raise ValueError(
                    f"handle {logical_id!r} belongs to app {handle_app_id!r}, not {self.app_id!r}"
                )
        for feature_id, manifest in self.providers.items():
            if not isinstance(manifest, ProviderManifest):
                raise TypeError(f"HDJ provider {feature_id!r} must be a ProviderManifest")
            if manifest.feature_id != feature_id:
                raise ValueError(
                    f"provider mapping key {feature_id!r} does not match "
                    f"feature_id {manifest.feature_id!r}"
                )
        object.__setattr__(self, "components", _freeze_mapping(self.components))
        object.__setattr__(self, "assets", _freeze_mapping(self.assets))
        object.__setattr__(self, "handles", _freeze_mapping(self.handles))
        object.__setattr__(self, "providers", _freeze_mapping(self.providers))
        object.__setattr__(self, "themes", tuple(dict.fromkeys(self.themes)))
        object.__setattr__(self, "application_styles", tuple(self.application_styles))

    @classmethod
    def from_registry(
        cls,
        *,
        app_id: str,
        registry: Registry | None = None,
        components: Mapping[str, type[Component[Any]]] | None = None,
        handles: Mapping[str, object] | None = None,
        assets: Mapping[str, AssetRef] | None = None,
        asset_hrefs: Mapping[str, str] | None = None,
        providers: Sequence[ProviderManifest] = (),
        import_registered_components: bool = True,
    ) -> JinjaBinding:
        """Capture a deterministic core-registry projection for one HDJ environment.

        Registry asset paths are package/source locations, so they are projected only
        when the application supplies an explicit public URL in ``asset_hrefs``.
        """
        resolved_registry = registry or get_registry()
        component_map = dict(components or {})
        if import_registered_components:
            for meta in resolved_registry.components():
                module = import_module(meta.module)
                candidate = getattr(module, meta.name, None)
                if not isinstance(candidate, type) or not issubclass(candidate, Component):
                    raise error(
                        HED_PROJECTION_0005,
                        title="Registered HDJ component cannot be imported",
                        explanation=(
                            f"Registry component {meta.logical_id!r} does not resolve to "
                            f"{meta.module}.{meta.name}."
                        ),
                        remediation=(
                            "Correct the trusted registry metadata or bind the class explicitly."
                        ),
                    )
                alias = candidate.__name__
                previous = component_map.get(alias)
                if previous is not None and previous is not candidate:
                    raise error(
                        HED_PROJECTION_0005,
                        title="Registered HDJ component alias collision",
                        explanation=f"More than one component resolves to alias {alias!r}.",
                        remediation="Pass an explicit component alias mapping for the application.",
                    )
                component_map[alias] = cast(type[Component[Any]], candidate)

        asset_map = dict(assets or {})
        public_asset_hrefs = dict(asset_hrefs or {})
        registered_asset_ids: set[str] = set()
        for meta in resolved_registry.assets():
            registered_asset_ids.add(meta.logical_id)
            public_href = public_asset_hrefs.get(meta.logical_id)
            if public_href is not None:
                asset_map.setdefault(
                    meta.logical_id,
                    AssetRef(kind=meta.kind, href=public_href, attributes=meta.attributes),
                )
        unknown_asset_ids = sorted(set(public_asset_hrefs) - registered_asset_ids)
        if unknown_asset_ids:
            raise ValueError(
                "asset_hrefs contains IDs absent from the registry: " + ", ".join(unknown_asset_ids)
            )
        style_facts = tuple(
            ApplicationStyleFact(
                logical_id=meta.logical_id,
                name=meta.name,
                owner=meta.owner,
                scope=meta.scope,
                layer=meta.layer,
                global_=meta.global_,
                media=meta.media,
                digest=meta.source_digest,
                provenance=meta.provenance,
            )
            for meta in resolved_registry.application_styles()
        )
        provider_map = {manifest.feature_id: manifest for manifest in providers}
        return cls(
            app_id=app_id,
            components=component_map,
            assets=asset_map,
            handles=dict(handles or {}),
            providers=provider_map,
            themes=tuple(meta.name for meta in resolved_registry.themes()),
            application_styles=style_facts,
        )

    @property
    def fingerprint(self) -> str:
        payload = {
            "app_id": self.app_id,
            "components": {
                alias: f"{component.__module__}.{component.__qualname__}"
                for alias, component in sorted(self.components.items())
            },
            "assets": {
                logical_id: {
                    "kind": asset.kind,
                    "href": asset.href,
                    "attributes": dict(asset.attributes),
                }
                for logical_id, asset in sorted(self.assets.items())
            },
            "handles": {
                logical_id: descriptor_fingerprint(self.descriptor(logical_id))
                for logical_id in sorted(self.handles)
            },
            "providers": {
                feature_id: manifest.as_mapping()
                for feature_id, manifest in sorted(self.providers.items())
            },
            "themes": list(self.themes),
            "application_styles": [item.as_mapping() for item in self.application_styles],
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()

    def resolve_handle(self, logical_id: str) -> object:
        """Resolve an app-scoped live handle after verifying the catalog descriptor."""
        token = str(logical_id).strip()
        catalog = compile_interaction_catalog(app_id=self.app_id)
        catalog.require(token)
        handle = self.handles.get(token)
        if handle is None:
            raise error(
                HED_UPDATE_0003,
                title="HDJ live handle is not bound",
                explanation=(
                    f"{token!r} is registered in app {self.app_id!r}, but this JinjaBinding "
                    "contains no live handle object for it."
                ),
                remediation="Add the handle to JinjaBinding(handles={logical_id: handle}).",
            )
        return handle

    def descriptor(self, logical_id: str) -> BaseHandleDescriptor:
        matches = [
            item
            for item in list_handle_descriptors(app_id=self.app_id)
            if item.logical_id == logical_id or item.name == logical_id
        ]
        if len(matches) != 1:
            raise error(
                HED_UPDATE_0003,
                title="HDJ handle descriptor is not registered",
                explanation=f"No unique descriptor exists for {logical_id!r} in {self.app_id!r}.",
                remediation="Register and seal the application handle before rendering HDJ.",
            )
        return matches[0]

    def catalog_facts(self, logical_id: str) -> JsonObject:
        entry = compile_interaction_catalog(app_id=self.app_id).require(logical_id)
        return entry.as_mapping(profile="production")

    def type_schema(self, logical_id: str) -> JsonObject | None:
        schema = type_schema_from_descriptor(self.descriptor(logical_id))
        return schema.as_mapping() if schema is not None else None

    def feature_bundles(self) -> tuple[object, ...]:
        from hedron_core.bundles import included_bundles

        return included_bundles(app_id=self.app_id)

    def view(self, target: object, **bind_kwargs: Any) -> object:
        from hedron_jinja.handles import catalog_view

        return catalog_view(target, binding=self, **bind_kwargs)

    def command_form(
        self,
        target: object,
        *,
        fields: Sequence[object] | None = None,
        **form_kwargs: Any,
    ) -> object:
        from hedron_jinja.handles import catalog_command_form

        return catalog_command_form(target, fields=fields, binding=self, **form_kwargs)


__all__ = ["ApplicationStyleFact", "JinjaBinding"]
