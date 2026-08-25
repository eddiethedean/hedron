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
from types import MappingProxyType
from typing import Final, Literal

from hedron_core.theme import Theme, default_theme

__all__ = [
    "PRESENTATION_SCHEMA",
    "PresentationContract",
    "PresentationError",
    "PRESENTATION_TOKEN_MANIFEST",
    "MotionRecipe",
    "ResponsiveCondition",
    "ScopedStyleBundle",
    "ScopedStyleRecipe",
    "application_style_hook_data",
    "application_style_hook_manifest",
    "component_presentation_manifest",
    "compile_scoped_styles",
    "presentation_contract",
    "presentation_token_manifest",
    "presentation_tokens",
    "motion_recipe",
    "motion_recipes",
]

PRESENTATION_SCHEMA: Final = "hedron.presentation-contract/1"

_IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
_PART_IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*$")
_TOKEN = re.compile(r"^var\(--hedron-[A-Za-z0-9-]+(?:,\s*[^()]*)?\)$")
_SAFE_VALUE = re.compile(r"^[A-Za-z0-9_ .,#%()/'\"+*/:-]+$")
_BREAKPOINTS: Final = {"sm": "40rem", "md": "56rem", "lg": "72rem", "xl": "90rem"}
_CONTAINER_SIZES: Final = {"sm": "24rem", "md": "40rem", "lg": "56rem"}
_DIRECTIONS: Final = frozenset({"ltr", "rtl", "inherit"})
_WRITING_MODES: Final = frozenset({"horizontal-tb", "vertical-rl", "vertical-lr", "inherit"})
_ACCESSIBILITY: Final = frozenset(
    {"forced-colors", "more-contrast", "reduced-motion", "reduced-transparency", "print"}
)
_CONDITION_ORDER: Final = {
    "viewport": 0,
    "viewport-range": 1,
    "viewport-max": 2,
    "container": 3,
    "container-range": 4,
    "container-max": 5,
    "direction": 6,
    "writing-mode": 7,
    "accessibility": 8,
}
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
    "motion.elevate": "180ms",
    "motion.crossfade": "200ms",
    "motion.easing.standard": "cubic-bezier(0.2, 0, 0, 1)",
    "surface.translucent.opacity": "78%",
    "surface.glass.opacity": "72%",
    "surface.glass.blur": "14px",
    "data.row.hover": "color-mix(in srgb, var(--hedron-color-accent) 8%, transparent)",
    "data.row.selected": "color-mix(in srgb, var(--hedron-color-accent) 14%, transparent)",
    "control.appearance": "auto",
    "control.accent": "var(--hedron-color-accent)",
    "data.table.border": "var(--hedron-color-border)",
    "data.table.radius": "var(--hedron-default-radius)",
    "data.table.header.background": "var(--hedron-color-surface-subtle)",
    "data.table.header.foreground": "var(--hedron-color-fg)",
    "data.table.header.weight": "600",
    "data.table.header.tracking": "0.01em",
    "data.table.row.separator": "var(--hedron-color-border)",
    "data.table.numeric": "tabular-nums",
    "data.table.code": "ui-monospace, SFMono-Regular, Menlo, monospace",
    "data.table.sticky.surface": "var(--hedron-color-surface)",
    "data.table.sticky.elevation": (
        "var(--hedron-elevation-raised, 0 0.25rem 0.75rem rgb(0 0 0 / 12%))"
    ),
    "data.table.density": "1",
    "control.focus": "var(--hedron-color-focus, var(--hedron-color-accent))",
    "control.invalid": "var(--hedron-color-danger, #b42318)",
    "control.busy": "var(--hedron-color-muted, currentColor)",
    "control.disabled": "var(--hedron-color-muted, currentColor)",
    "control.read-only": "var(--hedron-color-muted, currentColor)",
    "control.checked": "var(--hedron-control-accent, var(--hedron-color-accent))",
    "control.selected": "var(--hedron-control-accent, var(--hedron-color-accent))",
    "control.indeterminate": "var(--hedron-control-accent, var(--hedron-color-accent))",
}

_APPLICATION_STYLE_HOOKS: Final[dict[str, dict[str, tuple[str, ...] | tuple[str, ...]]]] = {
    "AppShell": {
        "nav.link": ("default", "hover", "current", "disabled"),
    },
    "ProcessFlow": {
        "step": ("current", "complete", "blocked", "skipped"),
    },
    "Card": {
        "body": ("default", "invalid", "busy"),
        "heading": ("default",),
        "supporting-copy": ("default",),
        "metadata": ("default",),
    },
    "FormField": {
        "control": (
            "default",
            "focus",
            "invalid",
            "busy",
            "disabled",
            "read-only",
            "checked",
            "selected",
            "indeterminate",
        ),
    },
    "SplitView": {
        "separator": ("default", "responsive-collapse"),
    },
}


class PresentationError(ValueError):
    """Raised when a 0.64 presentation contract leaves the closed vocabulary."""


@dataclass(frozen=True, slots=True)
class MotionRecipe:
    """One named motion preset with deterministic no-motion fallbacks."""

    name: str
    duration_token: str
    easing_token: str
    distance: str
    opacity: str
    reduced_motion: str
    print_fallback: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "duration_token": self.duration_token,
            "easing_token": self.easing_token,
            "distance": self.distance,
            "opacity": self.opacity,
            "reduced_motion": self.reduced_motion,
            "print_fallback": self.print_fallback,
        }


_MOTION_RECIPES: Final[dict[str, MotionRecipe]] = {
    name: MotionRecipe(
        name=name,
        duration_token=f"motion.{name}",
        easing_token="motion.easing.standard",
        distance=distance,
        opacity=opacity,
        reduced_motion="preserve-state",
        print_fallback="none",
    )
    for name, distance, opacity in (
        ("instant", "0px", "1"),
        ("standard", "0.25rem", "1"),
        ("emphasized", "0.5rem", "1"),
        ("reveal", "0px", "0"),
        ("elevate", "0.25rem", "1"),
        ("crossfade", "0px", "0"),
    )
}


def motion_recipes() -> dict[str, dict[str, str]]:
    """Return the finite named motion recipe catalog."""
    return {name: recipe.to_dict() for name, recipe in sorted(_MOTION_RECIPES.items())}


def motion_recipe(name: str) -> MotionRecipe:
    try:
        return _MOTION_RECIPES[name]
    except KeyError as exc:
        raise PresentationError(
            f"unknown motion recipe: {name!r}; use {', '.join(sorted(_MOTION_RECIPES))}"
        ) from exc


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise PresentationError(f"{label} must be a safe identifier")
    return value


def _part_identifier(value: str) -> str:
    if not isinstance(value, str) or _PART_IDENTIFIER.fullmatch(value) is None:
        raise PresentationError("part must be a safe identifier")
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


def _freeze_public(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze_public(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_public(item) for item in value)
    return value


def _thaw_public(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw_public(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_public(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class ResponsiveCondition:
    """One finite viewport, container, range, direction, or accessibility condition.

    ``viewport`` and ``container`` are lower bounds for compatibility.  The
    ``*-max`` and ``*-range`` forms add an upper bound without exposing raw
    media queries.  Ranges use names such as ``md-to-lg``.
    """

    kind: Literal[
        "viewport",
        "viewport-max",
        "viewport-range",
        "container",
        "container-max",
        "container-range",
        "direction",
        "writing-mode",
        "accessibility",
    ]
    value: str

    def __post_init__(self) -> None:
        # Accept compact values for integrations that want to keep the axis
        # in ``kind``: ``viewport/max-lg`` and ``viewport/md-to-lg``.
        if self.kind == "viewport" and isinstance(self.value, str):
            if self.value.startswith("max-"):
                object.__setattr__(self, "kind", "viewport-max")
                object.__setattr__(self, "value", self.value.removeprefix("max-"))
            elif "-to-" in self.value:
                object.__setattr__(self, "kind", "viewport-range")
        elif self.kind == "container" and isinstance(self.value, str):
            if self.value.startswith("max-"):
                object.__setattr__(self, "kind", "container-max")
                object.__setattr__(self, "value", self.value.removeprefix("max-"))
            elif "-to-" in self.value:
                object.__setattr__(self, "kind", "container-range")
        if not isinstance(self.kind, str) or self.kind not in (
            "viewport",
            "viewport-max",
            "viewport-range",
            "container",
            "container-max",
            "container-range",
            "direction",
            "writing-mode",
            "accessibility",
        ):
            raise PresentationError(f"unknown responsive condition kind: {self.kind!r}")
        if self.kind in ("viewport", "viewport-max") and (
            not isinstance(self.value, str) or self.value not in _BREAKPOINTS
        ):
            raise PresentationError(f"unknown viewport condition: {self.value!r}")
        if self.kind in ("container", "container-max") and (
            not isinstance(self.value, str) or self.value not in _CONTAINER_SIZES
        ):
            raise PresentationError(f"unknown container condition: {self.value!r}")
        if self.kind in ("viewport-range", "container-range"):
            names = _BREAKPOINTS if self.kind == "viewport-range" else _CONTAINER_SIZES
            parts = self.value.split("-to-") if isinstance(self.value, str) else []
            if (
                len(parts) != 2
                or any(item not in names for item in parts)
                or (len(parts) == 2 and list(names).index(parts[0]) >= list(names).index(parts[1]))
            ):
                raise PresentationError(f"unknown {self.kind} condition: {self.value!r}")
        if self.kind == "direction" and (
            not isinstance(self.value, str) or self.value not in _DIRECTIONS
        ):
            raise PresentationError(f"unknown direction: {self.value!r}")
        if self.kind == "writing-mode" and (
            not isinstance(self.value, str) or self.value not in _WRITING_MODES
        ):
            raise PresentationError(f"unknown writing mode: {self.value!r}")
        if self.kind == "accessibility" and (
            not isinstance(self.value, str) or self.value not in _ACCESSIBILITY
        ):
            raise PresentationError(f"unknown accessibility condition: {self.value!r}")

    @classmethod
    def viewport_max(cls, breakpoint: str) -> ResponsiveCondition:
        return cls("viewport-max", breakpoint)

    @classmethod
    def container_max(cls, size: str) -> ResponsiveCondition:
        return cls("container-max", size)

    @classmethod
    def viewport_range(cls, lower: str, upper: str) -> ResponsiveCondition:
        return cls("viewport-range", f"{lower}-to-{upper}")

    @classmethod
    def container_range(cls, lower: str, upper: str) -> ResponsiveCondition:
        return cls("container-range", f"{lower}-to-{upper}")

    def media_prefix(self) -> str:
        if self.kind == "viewport":
            return f"@media (min-width: {_BREAKPOINTS[self.value]})"
        if self.kind == "viewport-max":
            return f"@media (max-width: {_BREAKPOINTS[self.value]})"
        if self.kind == "viewport-range":
            lower, upper = self.value.split("-to-")
            return (
                f"@media (min-width: {_BREAKPOINTS[lower]}) and (max-width: {_BREAKPOINTS[upper]})"
            )
        if self.kind == "container":
            return f"@container (min-width: {_CONTAINER_SIZES[self.value]})"
        if self.kind == "container-max":
            return f"@container (max-width: {_CONTAINER_SIZES[self.value]})"
        if self.kind == "container-range":
            lower, upper = self.value.split("-to-")
            return (
                f"@container (min-width: {_CONTAINER_SIZES[lower]}) "
                f"and (max-width: {_CONTAINER_SIZES[upper]})"
            )
        if self.kind == "direction":
            return f'[dir="{self.value}"]'
        if self.kind == "writing-mode":
            return f'[style*="writing-mode: {self.value}"]'
        accessibility_prefixes = {
            "forced-colors": "@media (forced-colors: active)",
            "more-contrast": "@media (prefers-contrast: more)",
            "reduced-motion": "@media (prefers-reduced-motion: reduce)",
            "reduced-transparency": "@media (prefers-reduced-transparency: reduce)",
            "print": "@media print",
        }
        if self.kind == "accessibility":
            return accessibility_prefixes[self.value]
        raise PresentationError(f"unknown responsive condition kind: {self.kind!r}")


@dataclass(frozen=True, slots=True)
class ScopedStyleRecipe:
    """A typed style recipe for one declared component part and state."""

    component: str
    part: str
    declarations: Mapping[str, str]
    states: tuple[str, ...] = ()
    conditions: tuple[ResponsiveCondition, ...] = ()
    motion: str | None = None
    layer: Literal["components", "utilities", "overrides"] = "components"

    def __post_init__(self) -> None:
        _identifier(self.component, "component")
        _part_identifier(self.part)
        public_parts = _APPLICATION_STYLE_HOOKS.get(self.component)
        if public_parts is None or self.part not in public_parts:
            raise PresentationError(
                f"unknown public application style hook: {self.component}.{self.part}"
            )
        if self.layer not in _LAYERS:
            raise PresentationError(f"unknown style layer: {self.layer!r}")
        states = tuple(self.states)
        conditions = tuple(self.conditions)
        self._validate_conditions(conditions)
        if self.motion is not None:
            motion_recipe(self.motion)
        for state in states:
            _identifier(state, "state")
            if state not in public_parts[self.part]:
                raise PresentationError(
                    f"unknown public state for {self.component}.{self.part}: {state!r}"
                )
        normalized = dict(self.declarations)
        for property_name, value in self.declarations.items():
            if property_name not in _PROPERTIES:
                raise PresentationError(f"property {property_name!r} is not in the safe allowlist")
            value = _css_value(value, label=f"declarations[{property_name!r}]")
            if "var(--hedron-" in value and not _TOKEN.search(value):
                raise PresentationError("theme references must use a single --hedron token")
            normalized[property_name] = value
        object.__setattr__(self, "declarations", MappingProxyType(normalized))
        object.__setattr__(self, "states", states)
        object.__setattr__(self, "conditions", conditions)

    @property
    def class_name(self) -> str:
        raw = json.dumps(
            {
                "component": self.component,
                "part": self.part,
                "states": self.states,
                "conditions": sorted((item.kind, item.value) for item in self.conditions),
                "motion": self.motion,
                "declarations": sorted(self.declarations.items()),
                "layer": self.layer,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(raw.encode()).hexdigest()[:10]
        return f"hedron-scope-{self.component.lower()}-{self.part.lower()}-{digest}"

    @staticmethod
    def _validate_conditions(conditions: tuple[ResponsiveCondition, ...]) -> None:
        bounds: dict[str, tuple[int | None, int | None]] = {
            "viewport": (None, None),
            "container": (None, None),
        }
        for condition in conditions:
            if condition.kind in ("direction", "writing-mode", "accessibility"):
                continue
            axis = "viewport" if condition.kind.startswith("viewport") else "container"
            names = _BREAKPOINTS if axis == "viewport" else _CONTAINER_SIZES
            lower, upper = bounds[axis]
            if condition.kind == axis:
                value = list(names).index(condition.value)
                lower = value if lower is None else max(lower, value)
            elif condition.kind == f"{axis}-max":
                value = list(names).index(condition.value)
                upper = value if upper is None else min(upper, value)
            else:
                lower_name, upper_name = condition.value.split("-to-")
                low_value, high_value = list(names).index(lower_name), list(names).index(upper_name)
                lower = low_value if lower is None else max(lower, low_value)
                upper = high_value if upper is None else min(upper, high_value)
            if lower is not None and upper is not None and lower > upper:
                raise PresentationError(f"contradictory {axis} responsive conditions")
            bounds[axis] = (lower, upper)

    def to_dict(self) -> dict[str, object]:
        return {
            "component": self.component,
            "part": self.part,
            "class_name": self.class_name,
            "states": list(self.states),
            "conditions": [{"kind": item.kind, "value": item.value} for item in self.conditions],
            "motion": self.motion,
            "declarations": dict(sorted(self.declarations.items())),
            "layer": self.layer,
        }


@dataclass(frozen=True, slots=True)
class ScopedStyleBundle:
    css: str
    recipes: tuple[Mapping[str, object], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "recipes",
            tuple(_freeze_public(recipe) for recipe in self.recipes),
        )

    @property
    def digest(self) -> str:
        return "sha256-" + hashlib.sha256(self.css.encode()).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "hedron.scoped-style-bundle/1",
            "digest": self.digest,
            "recipes": tuple(_thaw_public(recipe) for recipe in self.recipes),
        }


def compile_scoped_styles(recipes: Sequence[ScopedStyleRecipe]) -> ScopedStyleBundle:
    """Compile recipes into deterministic cascade-layer CSS."""
    ordered = tuple(sorted(recipes, key=lambda item: (item.component, item.part, item.class_name)))
    chunks = ["@layer components, utilities, overrides;\n"]
    for recipe in ordered:
        selector = f".{recipe.class_name}"
        if recipe.states:
            state_selectors = ", ".join(
                f'[data-hedron-state~="{state}"]' for state in recipe.states
            )
            selector += f":is({state_selectors})"
        at_rules: list[str] = []
        selector_prefixes: list[str] = []
        for condition in sorted(
            recipe.conditions, key=lambda item: (_CONDITION_ORDER[item.kind], item.value)
        ):
            prefix = condition.media_prefix()
            if prefix.startswith("@"):
                at_rules.append(prefix)
            else:
                selector_prefixes.append(prefix)
        if selector_prefixes:
            selector = " ".join((*selector_prefixes, selector))
        declarations = dict(recipe.declarations)
        if recipe.motion is not None:
            preset = motion_recipe(recipe.motion)
            declarations.setdefault(
                "transition-duration",
                f"var(--hedron-{preset.duration_token.replace('.', '-')})",
            )
            declarations.setdefault(
                "transition-timing-function",
                f"var(--hedron-{preset.easing_token.replace('.', '-')})",
            )
        body = "".join(f"  {key}: {value};\n" for key, value in sorted(declarations.items()))
        rule = f"@layer {recipe.layer} {{\n{selector} {{\n{body}}}\n}}\n"
        for at_rule in reversed(at_rules):
            rule = f"{at_rule} {{\n{rule}}}\n"
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

    def __post_init__(self) -> None:
        for field_name in ("tokens", "breakpoints", "container_sizes", "motion"):
            object.__setattr__(self, field_name, _freeze_public(getattr(self, field_name)))
        object.__setattr__(self, "native_controls", tuple(self.native_controls))
        object.__setattr__(self, "data_chrome", tuple(self.data_chrome))

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


_PRESENTATION_TOKEN_CONSUMERS: Final[dict[str, tuple[str, ...]]] = {
    "type.display.size": ("typography",),
    "type.heading.size": ("typography",),
    "type.body.size": ("typography",),
    "type.supporting.size": ("typography",),
    "type.label.size": ("typography",),
    "type.metadata.size": ("Card.metadata",),
    "type.body.line-height": ("typography",),
    "type.heading.line-height": ("typography",),
    "space.1": ("layout",),
    "space.2": ("layout",),
    "space.3": ("layout",),
    "space.4": ("layout",),
    "space.5": ("layout",),
    "space.6": ("layout",),
    "geometry.control-height": ("controls",),
    "geometry.hit-target": ("controls",),
    "geometry.radius-sm": ("surfaces",),
    "geometry.radius-md": ("surfaces",),
    "geometry.radius-lg": ("surfaces",),
    "geometry.separator": ("data",),
    "motion.instant": ("motion",),
    "motion.standard": ("motion",),
    "motion.emphasized": ("motion",),
    "motion.reveal": ("motion",),
    "motion.elevate": ("motion",),
    "motion.crossfade": ("motion",),
    "motion.easing.standard": ("motion",),
    "surface.translucent.opacity": ("surfaces",),
    "surface.glass.opacity": ("surfaces",),
    "surface.glass.blur": ("surfaces",),
    "data.row.hover": ("data",),
    "data.row.selected": ("data",),
    "control.appearance": ("controls",),
    "control.accent": ("controls",),
    "data.table.border": ("data",),
    "data.table.radius": ("data",),
    "data.table.header.background": ("data",),
    "data.table.header.foreground": ("data",),
    "data.table.header.weight": ("data",),
    "data.table.header.tracking": ("data",),
    "data.table.row.separator": ("data",),
    "data.table.numeric": ("data",),
    "data.table.code": ("data",),
    "data.table.sticky.surface": ("data",),
    "data.table.sticky.elevation": ("data",),
    "data.table.density": ("data",),
    "control.focus": ("controls",),
    "control.invalid": ("controls",),
    "control.busy": ("controls",),
    "control.disabled": ("controls",),
    "control.read-only": ("controls",),
    "control.checked": ("controls",),
    "control.selected": ("controls",),
    "control.indeterminate": ("controls",),
}

PRESENTATION_TOKEN_MANIFEST: Final[dict[str, object]] = {
    "schema": "hedron.presentation-token-manifest/1",
    "declared": tuple(sorted(_PRESENTATION_DEFAULTS)),
    "consumed": {key: value for key, value in sorted(_PRESENTATION_TOKEN_CONSUMERS.items())},
}


def presentation_token_manifest(theme: Theme | None = None) -> dict[str, object]:
    """Return declared, consumed, and theme-overridden presentation tokens."""
    resolved = theme or default_theme()
    declared = tuple(sorted(_PRESENTATION_DEFAULTS))
    consumed = {key: list(_PRESENTATION_TOKEN_CONSUMERS[key]) for key in declared}
    overridden = {
        key: resolved.tokens[key]
        for key in declared
        if key in resolved.tokens and resolved.tokens[key] != _PRESENTATION_DEFAULTS[key]
    }
    try:
        from importlib import resources

        bundled_css = resources.files("hedron_core").joinpath("static/hedron-default.css")
        css = bundled_css.read_text(encoding="utf-8")
        unconsumed = [key for key in declared if f"--hedron-{key.replace('.', '-')}" not in css]
    except (FileNotFoundError, ModuleNotFoundError, OSError):
        # A missing packaged bundle is evidence of an incomplete package, not
        # evidence that all declared tokens are consumed.
        unconsumed = list(declared)
    return {
        "schema": "hedron.presentation-token-manifest/1",
        "declared": list(declared),
        "consumed": consumed,
        "overridden": dict(sorted(overridden.items())),
        "unconsumed": unconsumed,
    }


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
    payload["application_style_hooks"] = application_style_hook_manifest()
    payload["presentation_tokens"] = presentation_token_manifest()
    return payload


def application_style_hook_manifest() -> dict[str, object]:
    """Return the finite public hook vocabulary for application-owned CSS."""
    return {
        component: {
            "parts": {part: {"states": list(states)} for part, states in sorted(parts.items())}
        }
        for component, parts in sorted(_APPLICATION_STYLE_HOOKS.items())
    }


def application_style_hook_data(
    component: str,
    part: str,
    *,
    state: str | None = None,
) -> dict[str, str | bool | int | float | None]:
    """Return validated data attributes for a public application style hook."""
    parts = _APPLICATION_STYLE_HOOKS.get(component)
    if parts is None or part not in parts:
        raise PresentationError(f"unknown application style hook: {component}.{part}")
    if state is not None and state not in parts[part]:
        raise PresentationError(f"unknown state for {component}.{part}: {state!r}")
    data: dict[str, str | bool | int | float | None] = {
        "hedron-component": component,
        "hedron-part": part,
    }
    if state is not None:
        data["hedron-state"] = state
    return data
