"""Bounded presentation contracts for phase 0.64.

The public objects in this module are intentionally data-only.  They provide a
small, deterministic vocabulary for theme scales, responsive conditions,
component parts/states, motion, and application-owned component styling.  A
recipe can only address a generated class and a declared state; callers never
provide raw selectors or arbitrary at-rules.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final, Literal

from hedron_core.theme import Theme, default_theme

__all__ = [
    "PRESENTATION_SCHEMA",
    "PresentationContract",
    "PresentationError",
    "ResponsiveCondition",
    "ScopedStyleBundle",
    "ScopedStyleRecipe",
    "component_presentation_manifest",
    "compile_scoped_styles",
    "presentation_contract",
    "presentation_tokens",
]

PRESENTATION_SCHEMA: Final = "hedron.presentation-contract/1"

_IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
_TOKEN = re.compile(r"^var\(--hedron-[A-Za-z0-9-]+(?:,\s*[^()]*)?\)$")
_SAFE_VALUE = re.compile(r"^[A-Za-z0-9_ .,#%()/'\"+*/:-]+$")
_BREAKPOINTS: Final = {"sm": "40rem", "md": "56rem", "lg": "72rem", "xl": "90rem"}
_CONTAINER_SIZES: Final = {"sm": "24rem", "md": "40rem", "lg": "56rem"}
_DIRECTIONS: Final = frozenset({"ltr", "rtl", "inherit"})
_WRITING_MODES: Final = frozenset({"horizontal-tb", "vertical-rl", "vertical-lr", "inherit"})
_ACCESSIBILITY: Final = frozenset(
    {"forced-colors", "more-contrast", "reduced-motion", "reduced-transparency", "print"}
)
_LAYERS: Final = frozenset({"components", "utilities", "overrides"})
_PROPERTIES: Final = frozenset(
    {
        "accent-color",
        "background",
        "background-color",
        "border",
        "border-color",
        "border-radius",
        "box-shadow",
        "color",
        "column-gap",
        "font-family",
        "font-size",
        "font-weight",
        "gap",
        "inline-size",
        "letter-spacing",
        "line-height",
        "margin-block",
        "margin-inline",
        "max-inline-size",
        "min-block-size",
        "min-inline-size",
        "opacity",
        "outline",
        "outline-offset",
        "padding-block",
        "padding-inline",
        "row-gap",
        "text-decoration-thickness",
        "transition",
        "transition-duration",
        "transition-timing-function",
    }
)

# These are the public scales consumed by built-ins and safe application recipes.
_PRESENTATION_DEFAULTS: Final[dict[str, str]] = {
    "type.display.size": "clamp(2rem, 5vw, 4rem)",
    "type.heading.size": "clamp(1.5rem, 3vw, 2.25rem)",
    "type.body.size": "1rem",
    "type.supporting.size": "0.875rem",
    "type.label.size": "0.875rem",
    "type.metadata.size": "0.75rem",
    "type.body.line-height": "1.5",
    "type.heading.line-height": "1.2",
    "space.1": "0.25rem",
    "space.2": "0.5rem",
    "space.3": "0.75rem",
    "space.4": "1rem",
    "space.5": "1.5rem",
    "space.6": "2rem",
    "geometry.control-height": "2.5rem",
    "geometry.hit-target": "2.75rem",
    "geometry.radius-sm": "0.375rem",
    "geometry.radius-md": "0.625rem",
    "geometry.radius-lg": "1rem",
    "geometry.separator": "1px",
    "motion.instant": "0ms",
    "motion.standard": "150ms",
    "motion.emphasized": "300ms",
    "motion.reveal": "220ms",
    "motion.easing.standard": "cubic-bezier(0.2, 0, 0, 1)",
    "surface.translucent.opacity": "78%",
    "surface.glass.opacity": "72%",
    "surface.glass.blur": "14px",
    "data.row.hover": "color-mix(in srgb, var(--hedron-color-accent) 8%, transparent)",
    "data.row.selected": "color-mix(in srgb, var(--hedron-color-accent) 14%, transparent)",
    "control.appearance": "auto",
    "control.accent": "var(--hedron-color-accent)",
}


class PresentationError(ValueError):
    """Raised when a 0.64 presentation contract leaves the closed vocabulary."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise PresentationError(f"{label} must be a safe identifier")
    return value


def _css_value(value: str, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PresentationError(f"{label} must be a non-empty CSS value")
    value = value.strip()
    if any(bad in value.lower() for bad in ("url(", "expression(", "javascript:", "@import")):
        raise PresentationError(f"{label} cannot contain URLs, scripts, or imports")
    if any(char in value for char in "<>{};\\") or not _SAFE_VALUE.fullmatch(value):
        raise PresentationError(f"{label} contains an unsafe CSS value")
    return value


@dataclass(frozen=True, slots=True)
class ResponsiveCondition:
    """One finite viewport, container, direction, or accessibility condition."""

    kind: Literal["viewport", "container", "direction", "writing-mode", "accessibility"]
    value: str

    def __post_init__(self) -> None:
        if self.kind == "viewport" and self.value not in _BREAKPOINTS:
            raise PresentationError(f"unknown viewport condition: {self.value!r}")
        if self.kind == "container" and self.value not in _CONTAINER_SIZES:
            raise PresentationError(f"unknown container condition: {self.value!r}")
        if self.kind == "direction" and self.value not in _DIRECTIONS:
            raise PresentationError(f"unknown direction: {self.value!r}")
        if self.kind == "writing-mode" and self.value not in _WRITING_MODES:
            raise PresentationError(f"unknown writing mode: {self.value!r}")
        if self.kind == "accessibility" and self.value not in _ACCESSIBILITY:
            raise PresentationError(f"unknown accessibility condition: {self.value!r}")

    def media_prefix(self) -> str:
        if self.kind == "viewport":
            return f"@media (min-width: {_BREAKPOINTS[self.value]})"
        if self.kind == "container":
            return f"@container (min-width: {_CONTAINER_SIZES[self.value]})"
        if self.kind == "direction":
            return f'[dir="{self.value}"]'
        if self.kind == "writing-mode":
            return f'[style*="writing-mode: {self.value}"]'
        if self.value == "forced-colors":
            return "@media (forced-colors: active)"
        if self.value == "more-contrast":
            return "@media (prefers-contrast: more)"
        if self.value == "reduced-motion":
            return "@media (prefers-reduced-motion: reduce)"
        if self.value == "reduced-transparency":
            return "@media (prefers-reduced-transparency: reduce)"
        return "@media print"


@dataclass(frozen=True, slots=True)
class ScopedStyleRecipe:
    """A typed style recipe for one declared component part and state."""

    component: str
    part: str
    declarations: Mapping[str, str]
    states: tuple[str, ...] = ()
    conditions: tuple[ResponsiveCondition, ...] = ()
    layer: Literal["components", "utilities", "overrides"] = "components"

    def __post_init__(self) -> None:
        _identifier(self.component, "component")
        _identifier(self.part, "part")
        if self.layer not in _LAYERS:
            raise PresentationError(f"unknown style layer: {self.layer!r}")
        for state in self.states:
            _identifier(state, "state")
        normalized = dict(self.declarations)
        for property_name, value in self.declarations.items():
            if property_name not in _PROPERTIES:
                raise PresentationError(f"property {property_name!r} is not in the safe allowlist")
            value = _css_value(value, label=f"declarations[{property_name!r}]")
            if "var(--hedron-" in value and not _TOKEN.search(value):
                raise PresentationError("theme references must use a single --hedron token")
            normalized[property_name] = value
        object.__setattr__(self, "declarations", normalized)

    @property
    def class_name(self) -> str:
        raw = f"{self.component}:{self.part}:{','.join(self.states)}:{self.layer}"
        digest = hashlib.sha256(raw.encode()).hexdigest()[:10]
        return f"hedron-scope-{self.component.lower()}-{self.part.lower()}-{digest}"

    def to_dict(self) -> dict[str, object]:
        return {
            "component": self.component,
            "part": self.part,
            "class_name": self.class_name,
            "states": list(self.states),
            "conditions": [{"kind": item.kind, "value": item.value} for item in self.conditions],
            "declarations": dict(sorted(self.declarations.items())),
            "layer": self.layer,
        }


@dataclass(frozen=True, slots=True)
class ScopedStyleBundle:
    css: str
    recipes: tuple[dict[str, object], ...]

    @property
    def digest(self) -> str:
        return "sha256-" + hashlib.sha256(self.css.encode()).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "hedron.scoped-style-bundle/1",
            "digest": self.digest,
            "recipes": self.recipes,
        }


def compile_scoped_styles(recipes: Sequence[ScopedStyleRecipe]) -> ScopedStyleBundle:
    """Compile recipes into deterministic cascade-layer CSS."""
    ordered = tuple(sorted(recipes, key=lambda item: (item.component, item.part, item.class_name)))
    chunks = ["@layer components, utilities, overrides;\n"]
    for recipe in ordered:
        selector = f".{recipe.class_name}"
        if recipe.states:
            selector += "".join(f'[data-hedron-state~="{state}"]' for state in recipe.states)
        body = "".join(f"  {key}: {value};\n" for key, value in sorted(recipe.declarations.items()))
        rule = f"@layer {recipe.layer} {{\n{selector} {{\n{body}}}\n}}\n"
        for condition in recipe.conditions:
            prefix = condition.media_prefix()
            rule = f"{prefix} {{\n{rule}}}\n" if prefix.startswith("@") else f"{prefix} {rule}"
        chunks.append(rule)
    return ScopedStyleBundle("".join(chunks), tuple(item.to_dict() for item in ordered))


@dataclass(frozen=True, slots=True)
class PresentationContract:
    """Resolved theme presentation facts used by manifests and diagnostics."""

    theme: str
    tokens: Mapping[str, str]
    direction: str
    writing_mode: str
    breakpoints: Mapping[str, str]
    container_sizes: Mapping[str, str]
    motion: Mapping[str, str]
    native_controls: tuple[str, ...]
    data_chrome: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema": PRESENTATION_SCHEMA,
            "theme": self.theme,
            "tokens": dict(sorted(self.tokens.items())),
            "direction": self.direction,
            "writing_mode": self.writing_mode,
            "breakpoints": dict(sorted(self.breakpoints.items())),
            "container_sizes": dict(sorted(self.container_sizes.items())),
            "motion": dict(sorted(self.motion.items())),
            "native_controls": list(self.native_controls),
            "data_chrome": list(self.data_chrome),
        }
        payload["digest"] = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return payload


def presentation_tokens(theme: Theme | None = None) -> dict[str, str]:
    """Return the closed 0.64 semantic scale resolved against a theme."""
    resolved = theme or default_theme()
    values = dict(_PRESENTATION_DEFAULTS)
    values.update({key: value for key, value in resolved.tokens.items() if key in values})
    return dict(sorted(values.items()))


def presentation_contract(theme: Theme | None = None) -> PresentationContract:
    resolved = theme or default_theme()
    tokens = presentation_tokens(resolved)
    return PresentationContract(
        theme=resolved.name,
        tokens=tokens,
        direction="inherit",
        writing_mode="horizontal-tb",
        breakpoints=_BREAKPOINTS,
        container_sizes=_CONTAINER_SIZES,
        motion={
            key.removeprefix("motion."): value
            for key, value in tokens.items()
            if key.startswith("motion.")
        },
        native_controls=("checkbox", "radio", "select", "range", "file", "date", "time", "number"),
        data_chrome=(
            "table",
            "row",
            "header",
            "separator",
            "hover",
            "selected",
            "numeric",
            "sticky",
        ),
    )


def component_presentation_manifest() -> dict[str, object]:
    """Stable manifest of the 0.64 public presentation vocabulary."""
    contract = presentation_contract()
    payload = contract.to_dict()
    payload["parts_and_states"] = {
        "AppShell": {"parts": ["nav", "main", "header", "footer"], "states": ["collapsed", "busy"]},
        "Card": {"parts": ["header", "body", "footer"], "states": ["selected", "busy", "error"]},
        "FormField": {
            "parts": ["label", "control", "help", "error"],
            "states": ["invalid", "disabled", "busy"],
        },
        "SplitView": {
            "parts": ["primary", "secondary", "divider"],
            "states": ["collapsed", "busy"],
        },
        "ProcessFlow": {
            "parts": ["step", "connector", "status"],
            "states": ["current", "complete", "blocked"],
        },
    }
    return payload
