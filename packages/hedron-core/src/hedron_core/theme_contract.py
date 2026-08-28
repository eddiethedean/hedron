"""Phase 0.63 theme authority, export, and component evidence.

This module deliberately stays data-only.  Runtime CSS, JSON exports, CLI
inspection, and state-matrix tooling all consume the same resolved theme and
registry-derived component records.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from hedron_core.registry import get_registry
from hedron_core.theme import (
    Theme,
    compatibility_theme_vars,
    default_theme,
    derived_theme_tokens,
    emit_theme_css,
)
from hedron_core.theme_platform import (
    ThemeSpec,
    conformance_report,
    registered_component_theme_contracts,
    validate_theme_spec,
)

__all__ = [
    "ComponentStateMatrix",
    "StateMatrixEntry",
    "ThemeExport",
    "ThemeResolution",
    "build_state_matrix",
    "component_contract_manifest",
    "element_metadata_manifest",
    "export_theme",
    "inspect_theme_css",
    "package_identity_manifest",
    "resolve_theme",
    "theme_contract_report",
]

THEME_RESOLUTION_SCHEMA = "hedron.theme-resolution/1"
THEME_EXPORT_SCHEMA = "hedron.theme-export/1"
COMPONENT_MANIFEST_SCHEMA = "hedron.component-theme-manifest/1"
STATE_MATRIX_SCHEMA = "hedron.component-state-matrix/1"

_DEFAULT_VIEWPORTS = ("320", "390", "1440")
_DEFAULT_MODES = ("light", "dark")
_DEFAULT_ACCESSIBILITY_MODES = (
    "none",
    "forced-colors",
    "high-contrast",
    "reduced-motion",
    "reduced-transparency",
    "print",
)
_DEFAULT_STATES = ("default",)
_DEFAULT_CONSUMER = re.compile(r"var\(\s*(--hedron-default-[A-Za-z0-9-]+)")


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


def _as_theme(value: Theme | ThemeSpec) -> Theme:
    return value.to_theme() if isinstance(value, ThemeSpec) else value


@dataclass(frozen=True, slots=True)
class ThemeResolution:
    """One deterministic, serializable view of a resolved theme."""

    name: str
    tokens: Mapping[str, str]
    derived: Mapping[str, str] = field(default_factory=dict)
    modes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    variants: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    accessibility_modes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    aliases: Mapping[str, str] = field(default_factory=dict)
    groups: Mapping[str, str] = field(default_factory=dict)
    recipes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    content_width: str | None = None
    typography_features: Mapping[str, int] = field(default_factory=dict)
    typography_role_features: Mapping[str, Mapping[str, int]] = field(default_factory=dict)
    provenance: tuple[Mapping[str, Any], ...] = ()
    source_schema: str = "hedron.theme/1"

    @property
    def fingerprint(self) -> str:
        return _digest(self.to_dict(include_fingerprint=False))

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "schema": THEME_RESOLUTION_SCHEMA,
            "name": self.name,
            "tokens": dict(sorted(self.tokens.items())),
            "derived": dict(sorted(self.derived.items())),
            "modes": {
                key: dict(sorted(value.items())) for key, value in sorted(self.modes.items())
            },
            "variants": {
                key: dict(sorted(value.items())) for key, value in sorted(self.variants.items())
            },
            "accessibility_modes": {
                key: dict(sorted(value.items()))
                for key, value in sorted(self.accessibility_modes.items())
            },
            "aliases": dict(sorted(self.aliases.items())),
            "groups": dict(sorted(self.groups.items())),
            "recipes": {
                key: dict(sorted(value.items())) for key, value in sorted(self.recipes.items())
            },
            "content_width": self.content_width,
            "typography_features": dict(sorted(self.typography_features.items())),
            "typography_role_features": {
                key: dict(sorted(value.items()))
                for key, value in sorted(self.typography_role_features.items())
            },
            "provenance": [dict(item) for item in self.provenance],
            "source_schema": self.source_schema,
        }
        if include_fingerprint:
            result["fingerprint"] = self.fingerprint
        return result


def resolve_theme(theme: Theme | ThemeSpec) -> ThemeResolution:
    """Resolve a legacy ``Theme`` or immutable ``ThemeSpec`` once for all tools."""

    source = theme
    resolved = _as_theme(theme)
    compatibility = compatibility_theme_vars(resolved)
    provenance: tuple[Mapping[str, Any], ...]
    if isinstance(source, ThemeSpec):
        provenance = tuple(source.provenance) + (
            {"source": "ThemeSpec", "fingerprint": source.fingerprint},
        )
        source_schema = source.schema
    else:
        provenance = ({"source": "Theme", "name": resolved.name, "parent": resolved.parent},)
        source_schema = "hedron.theme/1"
    return ThemeResolution(
        name=resolved.name,
        tokens={**derived_theme_tokens(resolved), **dict(resolved.tokens)},
        derived={key.removeprefix("--hedron-"): value for key, value in compatibility.items()},
        modes={key: dict(value) for key, value in resolved.modes.items()},
        variants={key: dict(value) for key, value in resolved.variants.items()},
        accessibility_modes={
            key: dict(value) for key, value in resolved.accessibility_modes.items()
        },
        aliases=dict(getattr(source, "aliases", {})),
        groups=dict(getattr(source, "groups", {})),
        recipes={key: dict(value) for key, value in getattr(source, "recipes", {}).items()},
        content_width=resolved.content_width,
        typography_features=dict(resolved.typography_features),
        typography_role_features={
            key: dict(value) for key, value in resolved.typography_role_features.items()
        },
        provenance=provenance,
        source_schema=source_schema,
    )


def _contract_dict(contract: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "logical_id": contract.logical_id,
        "kind": "component",
        "parts": list(contract.parts),
        "states": list(contract.states),
        "variants": list(contract.variants),
        "required_tokens": list(contract.required_tokens),
        "roles": list(contract.roles),
        "contrast_relationships": [dict(item) for item in contract.contrast_relationships],
        "accessibility_behavior": dict(contract.accessibility_behavior),
        "fallback_policy": dict(contract.fallback_policy),
        "profile": contract.profile,
    }
    for component in get_registry().components():
        if component.name == contract.logical_id:
            entry["slots"] = dict(sorted(component.slots.items()))
            entry["distribution"] = component.distribution
            entry["accessibility_notes"] = component.accessibility_notes
            break
    else:
        entry["slots"] = {}
    return entry


def component_contract_manifest() -> dict[str, Any]:
    """Project theme contracts and element ABI metadata into one stable manifest."""

    entries = [_contract_dict(item) for item in registered_component_theme_contracts()]
    contract_names = {item["logical_id"] for item in entries}
    for component in get_registry().components():
        if component.name in contract_names:
            continue
        entries.append(
            {
                "logical_id": component.logical_id,
                "name": component.name,
                "kind": "registered-component",
                "parts": [],
                "slots": dict(sorted(component.slots.items())),
                "states": ["default"],
                "variants": ["default"],
                "required_tokens": [],
                "roles": [],
                "accessibility_notes": component.accessibility_notes,
                "style_symbols": dict(sorted(component.style_symbols.items())),
                "distribution": component.distribution,
            }
        )
    for element in get_registry().element_definitions():
        entries.append(
            {
                "logical_id": element.logical_id,
                "kind": "element",
                "tag_name": element.tag_name,
                "abi_version": element.abi_version,
                "module_asset_id": element.module_asset_id,
                "parts": list(element.parts),
                "slots": dict(sorted(element.slots.items())),
                "required_tokens": list(element.tokens),
                "states": [field.name for field in element.state_ownership],
                "events": list(element.events),
                "a11y_contract": dict(element.a11y_contract),
                "style_contract": dict(element.style_contract),
                "lifecycle": dict(element.lifecycle),
                "fallback": dict(element.fallback),
                "maturity": element.maturity,
                "compatibility": dict(element.compatibility),
            }
        )
    entries.sort(key=lambda item: (str(item["kind"]), str(item["logical_id"])))
    return {
        "schema": COMPONENT_MANIFEST_SCHEMA,
        "version": 1,
        "components": entries,
        "digest": _digest(entries),
    }


def element_metadata_manifest() -> dict[str, Any]:
    """Return the element-only projection used by custom-element consumers."""

    elements = [
        item
        for item in component_contract_manifest()["components"]
        if item.get("kind") == "element"
    ]
    return {
        "schema": "hedron.element-metadata/1",
        "version": 1,
        "elements": elements,
        "digest": _digest(elements),
    }


def package_identity_manifest() -> dict[str, Any]:
    """Return registry/package identity facts without importing satellite packages."""

    component_manifest = component_contract_manifest()
    distributions: dict[str, str | None] = {}
    names = {
        "hedron",
        "hedron-core",
        *(str(item.get("distribution", "")) for item in component_manifest["components"]),
    }
    for name in sorted(item for item in names if item):
        try:
            distributions[name] = version(name)
        except PackageNotFoundError:
            distributions[name] = None
    components = [
        {
            "logical_id": item["logical_id"],
            "distribution": item.get("distribution", "hedron-core"),
            "maturity": item.get("maturity", "Supported"),
            "compatibility": item.get("compatibility", {}),
        }
        for item in component_manifest["components"]
    ]
    payload: dict[str, Any] = {
        "schema": "hedron.package-identity/1",
        "runtime": "python-no-node",
        "distributions": distributions,
        "components": components,
        "metadata_digest": element_metadata_manifest()["digest"],
        "component_manifest_digest": component_manifest["digest"],
    }
    payload["digest"] = _digest(payload)
    return payload


@dataclass(frozen=True, slots=True)
class StateMatrixEntry:
    """One bounded component state/viewport/mode case."""

    case_id: str
    component: str
    state: str
    variant: str
    mode: str
    viewport: str
    accessibility_mode: str = "none"

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.case_id,
            "component": self.component,
            "state": self.state,
            "variant": self.variant,
            "mode": self.mode,
            "viewport": self.viewport,
            "accessibility_mode": self.accessibility_mode,
        }


@dataclass(frozen=True, slots=True)
class ComponentStateMatrix:
    entries: tuple[StateMatrixEntry, ...]

    @property
    def digest(self) -> str:
        return _digest([entry.to_dict() for entry in self.entries])

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": STATE_MATRIX_SCHEMA,
            "version": 1,
            "entries": [entry.to_dict() for entry in self.entries],
            "count": len(self.entries),
            "digest": self.digest,
        }


def build_state_matrix(
    *,
    components: Iterable[str] | None = None,
    viewports: Iterable[str] = _DEFAULT_VIEWPORTS,
    modes: Iterable[str] = _DEFAULT_MODES,
    accessibility_modes: Iterable[str] = ("none",),
) -> ComponentStateMatrix:
    """Build a deterministic, bounded state matrix from the registry manifest."""

    wanted = set(components) if components is not None else None

    def viewport_key(value: str) -> tuple[int, str]:
        return (0, f"{int(value):08d}") if value.isdigit() else (1, value)

    entries: list[StateMatrixEntry] = []
    for item in component_contract_manifest()["components"]:
        component = str(item["logical_id"])
        if wanted is not None and component not in wanted:
            continue
        states = tuple(str(value) for value in item.get("states", ())) or _DEFAULT_STATES
        variants = tuple(str(value) for value in item.get("variants", ())) or _DEFAULT_STATES
        for state in sorted(set(states)):
            for variant in sorted(set(variants)):
                for mode in sorted(set(str(value) for value in modes)):
                    for accessibility_mode in sorted(
                        set(str(value) for value in accessibility_modes)
                    ):
                        for viewport in sorted(
                            set(str(value) for value in viewports), key=viewport_key
                        ):
                            case_id = ":".join((component, state, variant, mode, viewport))
                            if accessibility_mode != "none":
                                case_id = f"{case_id}:{accessibility_mode}"
                            entries.append(
                                StateMatrixEntry(
                                    case_id,
                                    component,
                                    state,
                                    variant,
                                    mode,
                                    viewport,
                                    accessibility_mode,
                                )
                            )
    return ComponentStateMatrix(tuple(entries))


@dataclass(frozen=True, slots=True)
class ThemeExport:
    resolution: ThemeResolution
    css: str
    json: str
    conformance: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": THEME_EXPORT_SCHEMA,
            "theme": self.resolution.to_dict(),
            "css": self.css,
            "design_tokens": json.loads(self.json),
            "conformance": dict(self.conformance),
        }


def export_theme(theme: Theme | ThemeSpec, *, profile: str = "core") -> ThemeExport:
    """Export one theme to matching CSS and design-token JSON."""

    resolution = resolve_theme(theme)
    spec = (
        theme
        if isinstance(theme, ThemeSpec)
        else ThemeSpec(
            name=theme.name,
            tokens=dict(theme.tokens),
            modes={key: dict(value) for key, value in theme.modes.items()},
            accessibility_modes={
                key: dict(value) for key, value in theme.accessibility_modes.items()
            },
            content_width=theme.content_width,
            typography_features=dict(theme.typography_features),
            typography_role_features={
                key: dict(value) for key, value in theme.typography_role_features.items()
            },
            metadata={"source": "Theme", "parent": theme.parent},
        )
    )
    report = validate_theme_spec(spec, profile=profile, strict=False)
    if report.errors:
        raise ValueError(f"theme export rejected: {report.errors!r}")
    payload = resolution.to_dict()
    payload["component_manifest_digest"] = component_contract_manifest()["digest"]
    return ThemeExport(
        resolution=resolution,
        css=emit_theme_css(_as_theme(theme)),
        json=json.dumps(payload, indent=2, sort_keys=True) + "\n",
        conformance=conformance_report(spec, profile=profile),
    )


def inspect_theme_css(css: str) -> dict[str, Any]:
    """Report legacy stylesheet consumers and whether the bridge covers them."""

    consumers = sorted(set(_DEFAULT_CONSUMER.findall(css)))
    available = set(compatibility_theme_vars(default_theme()))
    unbridged = sorted(set(consumers) - available)
    return {
        "schema": "hedron.theme-inspection/1",
        "legacy_consumers": consumers,
        "bridged": not unbridged,
        "unbridged": unbridged,
        "consumer_count": len(consumers),
    }


def theme_contract_report(theme: Theme | ThemeSpec, *, css: str | None = None) -> dict[str, Any]:
    """Return the machine-readable Required theme-contract evidence packet."""

    exported = export_theme(theme)
    report: dict[str, Any] = {
        "schema": "hedron.theme-contract/1",
        "theme": exported.resolution.to_dict(),
        "component_manifest": component_contract_manifest(),
        "state_matrix": build_state_matrix(
            accessibility_modes=_DEFAULT_ACCESSIBILITY_MODES
        ).to_dict(),
        "conformance": dict(exported.conformance),
    }
    if css is not None:
        report["stylesheet"] = inspect_theme_css(css)
    report["digest"] = _digest(report)
    return report
