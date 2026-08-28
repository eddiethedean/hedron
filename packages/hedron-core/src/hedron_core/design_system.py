"""Portable DesignSystem, brand compilation, and semantic style recipes (phase 0.58)."""

from __future__ import annotations

import colorsys
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from dataclasses import replace as dc_replace
from typing import Any, Final, Literal, TypeVar, cast

from hedron_core.builtins.appearance import (
    APPEARANCES,
    BREAKPOINTS,
    DENSITIES,
    ELEVATIONS,
    EMPHASES,
    OVERFLOW_MODES,
    PADDINGS,
    RESPONSIVE_POLICIES,
    SIZES,
    TEXT_WRAPS,
    TRACKING,
    TYPE_EFFECTS,
    TYPE_MEASURES,
    TYPOGRAPHY_ROLES,
    WIDTHS,
    Appearance,
    Density,
    Elevation,
    Emphasis,
    OverflowMode,
    Padding,
    ResponsivePolicy,
    Size,
    TypographyEffect,
    TypographyMeasure,
    TypographyRole,
    Width,
    require_choice,
)
from hedron_core.codes import (
    HED_BRAND_0001,
    HED_BRAND_0002,
    HED_BRAND_0003,
    HED_DESIGN_0001,
    HED_DESIGN_0002,
    HED_DESIGN_0003,
    HED_RECIPE_0001,
    HED_RECIPE_0002,
    HED_RECIPE_0003,
    HED_RECIPE_0004,
)
from hedron_core.component import Component
from hedron_core.diagnostics import DiagnosticSeverity, error
from hedron_core.theme import (
    Theme,
    compile_palette,
    contrast_diagnostics,
    contrast_ratio,
    default_theme,
)
from hedron_core.theme_platform import (
    Color,
    RecipeFamily,
    register_recipe_family,
    registered_recipe_families,
)

__all__ = [
    "BUILTIN_RECIPES",
    "FEATURE_ROLES",
    "RECIPE_FAMILIES",
    "DesignSystem",
    "DesignSystemPlan",
    "StyleRecipe",
    "GeometryPreset",
    "TypographyPreset",
    "ElevationPreset",
    "MotionPreset",
    "NavigationPreset",
    "StyleFamily",
    "RecipeFamily",
    "register_recipe_family",
    "registered_recipe_families",
]

StyleFamily = str
GeometryPreset = Literal["square", "soft", "rounded"]
TypographyPreset = Literal["system-sans", "system-serif", "system-mono"]
ElevationPreset = Literal["flat", "subtle", "layered"]
MotionPreset = Literal["standard", "calm", "none"]
NavigationPreset = Literal["compact", "default", "wide"]

ComponentT = TypeVar("ComponentT", bound=Component[Any])

PLAN_SCHEMA_ID: Final = "hedron.design-system-plan/1"
BRAND_ALGORITHM: Final = "hedron.brand-palette/2"
RECIPE_FAMILIES: Final[tuple[StyleFamily, ...]] = (
    "control",
    "surface",
    "data",
    "status",
    "content",
)

_HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
_MAX_RECIPE_DEPTH = 4

_FAMILY_FIELDS: Final[Mapping[StyleFamily, frozenset[str]]] = {
    "control": frozenset({"size", "appearance", "emphasis", "width"}),
    "surface": frozenset({"appearance", "density", "padding", "elevation"}),
    "data": frozenset({"density", "responsive"}),
    "status": frozenset({"size", "appearance"}),
    "content": frozenset({"role", "overflow", "measure", "effect", "tracking", "wrap"}),
}

_FAMILY_COMPONENTS: Final[Mapping[StyleFamily, frozenset[str]]] = {
    "control": frozenset({"Button", "LinkButton", "IconButton"}),
    "surface": frozenset({"Surface", "Card"}),
    "data": frozenset({"Table", "DescriptionList", "PageHeader", "FormGrid"}),
    "status": frozenset({"Badge", "Alert", "Status"}),
    "content": frozenset({"Text", "Heading", "PageHeader"}),
}

# Intersection of family fields and optional props that default to None.
_COMPONENT_FIELDS: Final[Mapping[str, frozenset[str]]] = {
    "Button": frozenset({"size", "appearance", "emphasis", "width"}),
    "LinkButton": frozenset({"size", "appearance", "emphasis"}),
    "IconButton": frozenset({"size", "appearance", "emphasis"}),
    "Surface": frozenset({"appearance", "density", "padding", "elevation"}),
    "Card": frozenset({"appearance", "density", "padding", "elevation"}),
    "Table": frozenset({"density", "responsive"}),
    "DescriptionList": frozenset({"density"}),
    "PageHeader": frozenset({"density", "measure", "effect", "tracking", "wrap"}),
    "FormGrid": frozenset({"density"}),
    "Badge": frozenset({"size", "appearance"}),
    "Alert": frozenset({"size", "appearance"}),
    "Status": frozenset({"size", "appearance"}),
    "Text": frozenset({"role", "overflow", "measure", "effect", "tracking", "wrap"}),
    "Heading": frozenset({"role", "overflow", "measure", "effect", "tracking", "wrap"}),
}

_GEOMETRY_SHAPE: Final[Mapping[GeometryPreset, Mapping[str, str]]] = {
    "square": {"radius": "0", "radius-lg": "0"},
    "soft": {"radius": "0.5rem", "radius-lg": "0.75rem"},
    "rounded": {"radius": "0.75rem", "radius-lg": "1.25rem"},
}

_TYPOGRAPHY_FONT: Final[Mapping[TypographyPreset, str]] = {
    "system-sans": "system-ui, sans-serif",
    "system-serif": 'ui-serif, Georgia, "Times New Roman", serif',
    "system-mono": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
}

_ELEVATION_MAP: Final[Mapping[ElevationPreset, Mapping[str, str]]] = {
    "flat": {"raised": "none"},
    "subtle": {"raised": "0 1px 2px rgb(15 23 42 / 8%)"},
    "layered": {
        "raised": "0 1px 2px rgb(15 23 42 / 8%), 0 8px 24px rgb(15 23 42 / 12%)",
    },
}

_MOTION_DURATION: Final[Mapping[MotionPreset, str]] = {
    "standard": "150ms",
    "calm": "250ms",
    "none": "0ms",
}

_NAV_WIDTH: Final[Mapping[NavigationPreset, str]] = {
    "compact": "12rem",
    "default": "15rem",
    "wide": "18rem",
}

_FIELD_VOCABULARIES: Final[Mapping[str, tuple[str, ...]]] = {
    "size": SIZES,
    "appearance": APPEARANCES,
    "emphasis": EMPHASES,
    "width": WIDTHS,
    "density": DENSITIES,
    "padding": PADDINGS,
    "elevation": ELEVATIONS,
    "responsive": RESPONSIVE_POLICIES,
    "role": TYPOGRAPHY_ROLES,
    "overflow": OVERFLOW_MODES,
    "measure": TYPE_MEASURES,
    "effect": TYPE_EFFECTS,
    "tracking": TRACKING,
    "wrap": TEXT_WRAPS,
}

_RESPONSIVE_RECIPE_FIELDS: Final[Mapping[str, tuple[str, ...]]] = {
    "density": DENSITIES,
    "size": SIZES,
    "appearance": APPEARANCES,
    "emphasis": EMPHASES,
    "width": WIDTHS,
    "padding": PADDINGS,
    "elevation": ELEVATIONS,
    "responsive": RESPONSIVE_POLICIES,
}


def _family_fields(family: str) -> frozenset[str]:
    builtin = _FAMILY_FIELDS.get(family)  # type: ignore[arg-type]
    if builtin is not None:
        return builtin
    for candidate in registered_recipe_families():
        if candidate.name == family:
            return frozenset(candidate.fields)
    return frozenset()


def _family_components(family: str) -> frozenset[str]:
    builtin = _FAMILY_COMPONENTS.get(family)  # type: ignore[arg-type]
    if builtin is not None:
        return builtin
    for candidate in registered_recipe_families():
        if candidate.name == family:
            return frozenset(candidate.components)
    return frozenset()


def _family_vocabularies(family: str) -> Mapping[str, tuple[str, ...]]:
    values: dict[str, tuple[str, ...]] = {
        key: _FIELD_VOCABULARIES[key]
        for key in _family_fields(family)
        if key in _FIELD_VOCABULARIES
    }
    for candidate in registered_recipe_families():
        if candidate.name == family:
            values.update(candidate.fields)
    return values


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _normalize_name(name: str, *, label: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise error(
            HED_DESIGN_0001,
            title=f"Invalid {label} name",
            explanation=f"{label} name must be a non-empty string.",
            remediation="Use a simple alphanumeric identifier such as 'acme'.",
        )
    normalized = name.strip().lower().replace(" ", "-")
    if not _NAME_RE.match(normalized):
        raise error(
            HED_DESIGN_0001,
            title=f"Invalid {label} name",
            explanation=f"{label} name {name!r} is not a safe identifier.",
            remediation="Use letters, digits, hyphens, or underscores starting with a letter.",
        )
    return normalized


def _normalize_hex(value: str | Color) -> str:
    """Normalize legacy hex and safe 0.60 absolute colors to sRGB hex."""
    if isinstance(value, Color):
        return value.to_hex()[:7]
    if not isinstance(value, str) or not _HEX_COLOR.match(value.strip()):
        raise error(
            HED_BRAND_0001,
            title="Invalid brand accent",
            explanation=(
                f"Accent {value!r} is not a 3- or 6-digit hex color. "
                "Named colors and CSS expressions are rejected."
            ),
            remediation="Pass a hex accent such as '#2f6fed' or '#06f'.",
        )
    raw = value.strip()
    digits = raw[1:]
    if len(digits) == 3:
        digits = "".join(ch * 2 for ch in digits)
    return f"#{digits.lower()}"


def _parse_hex(value: str) -> tuple[float, float, float]:
    normalized = _normalize_hex(value)
    digits = normalized[1:]
    return tuple(int(digits[index : index + 2], 16) / 255 for index in (0, 2, 4))  # type: ignore[return-value]


def _to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(max(0.0, min(1.0, channel)) * 255):02x}" for channel in rgb)


def _with_lightness(hue: float, saturation: float, lightness: float) -> str:
    return _to_hex(colorsys.hls_to_rgb(hue, lightness, saturation))


def _search_lightness(
    hue: float,
    saturation: float,
    against: str,
    target: float,
    start: float,
    *,
    direction: Literal["darker", "lighter"],
) -> str | None:
    """Walk lightness until contrast clears ``target``; None if unsatisfied."""
    lightness = start
    step = -0.01 if direction == "darker" else 0.01
    best: str | None = None
    for _ in range(101):
        candidate = _with_lightness(hue, saturation, max(0.0, min(1.0, lightness)))
        if contrast_ratio(candidate, against) >= target:
            if best is None or candidate < best:
                best = candidate
            # Prefer nearest first hit; keep searching for lexically lower ties at same step.
            # Nearest-candidate: return the first that clears, then only replace on equal
            # contrast distance with lower hex — for v1 return first clearing candidate.
            return candidate
        lightness += step
        if lightness < 0.0 or lightness > 1.0:
            break
    return best


def compile_dark_palette(seed: str) -> dict[str, str]:
    """Compile a dark-mode semantic palette sharing hue with ``seed``."""
    hue, _seed_l, saturation = colorsys.rgb_to_hls(*_parse_hex(seed))
    saturation = max(saturation, 0.35)
    background = _with_lightness(hue, min(saturation, 0.35), 0.08)
    surface = _with_lightness(hue, min(saturation, 0.35), 0.12)
    surface_muted = _with_lightness(hue, min(saturation, 0.35), 0.16)
    border = _with_lightness(hue, min(saturation, 0.3), 0.28)

    foreground = _search_lightness(
        hue, min(saturation, 0.25), background, 7.0, 0.92, direction="lighter"
    )
    muted = _search_lightness(hue, min(saturation, 0.2), background, 4.5, 0.72, direction="lighter")
    accent = _search_lightness(hue, saturation, background, 4.5, 0.62, direction="lighter")
    focus = _search_lightness(hue, saturation, background, 3.0, 0.62, direction="lighter")
    danger = _search_lightness(0.995, 0.55, background, 4.5, 0.65, direction="lighter")
    on_accent = _search_lightness(
        hue, min(saturation, 0.4), accent or background, 4.5, 0.12, direction="darker"
    )
    on_danger = _search_lightness(0.995, 0.4, danger or background, 4.5, 0.12, direction="darker")

    missing = [
        name
        for name, value in (
            ("color.fg", foreground),
            ("color.muted", muted),
            ("color.accent", accent),
            ("color.focus", focus),
            ("color.danger", danger),
            ("color.on-accent", on_accent),
            ("color.on-danger", on_danger),
        )
        if value is None
    ]
    if missing:
        raise error(
            HED_BRAND_0002,
            title="Brand dark palette unsatisfied",
            explanation=(
                "Could not satisfy contrast targets for dark-mode tokens: "
                + ", ".join(missing)
                + f" (seed={seed!r})."
            ),
            remediation="Choose a different hex accent, or author an explicit Theme.",
            context={"missing": missing, "seed": seed, "mode": "dark"},
        )

    assert foreground and muted and accent and focus and danger and on_accent and on_danger
    return {
        "color.bg": background,
        "color.surface": surface,
        "color.surface-muted": surface_muted,
        "color.fg": foreground,
        "color.muted": muted,
        "color.border": border,
        "color.accent": accent,
        "color.accent-soft": _with_lightness(hue, min(saturation, 0.45), 0.22),
        "color.on-accent": on_accent,
        "color.focus": focus,
        "color.danger": danger,
        "color.on-danger": on_danger,
    }


def _theme_summary(theme: Theme) -> dict[str, object]:
    return {
        "name": theme.name,
        "tokens": dict(sorted(theme.tokens.items())),
        "modes": {
            mode: dict(sorted(values.items())) for mode, values in sorted(theme.modes.items())
        },
        "accessibility_modes": {
            mode: dict(sorted(values.items()))
            for mode, values in sorted(theme.accessibility_modes.items())
        },
        "palette": dict(sorted(theme.palette.items())),
        "density": theme.density,
        "shape": dict(sorted(theme.shape.items())),
        "nav_width": theme.nav_width,
        "content_width": theme.content_width,
        "typography_features": dict(sorted(theme.typography_features.items())),
        "typography_role_features": {
            key: dict(sorted(value.items()))
            for key, value in sorted(theme.typography_role_features.items())
        },
        "elevation": dict(sorted(theme.elevation.items())),
        "parent": theme.parent,
    }


def _clone_component(component: ComponentT, props: object) -> ComponentT:
    bound = component.__class__.__new__(component.__class__)
    Component.__init__(bound, props)
    for attr_name, attr_value in vars(component).items():
        if attr_name in {"_props", "_children", "_slot_values", "_key"}:
            continue
        setattr(bound, attr_name, attr_value)
    # Copy containers so DesignSystem.apply does not share mutable structure.
    target = cast(Any, bound)
    target._children = list(component._children)
    target._slot_values = {
        key: (list(value) if isinstance(value, list) else value)
        for key, value in component._slot_values.items()
    }
    target._key = component._key
    return bound


@dataclass(frozen=True, slots=True)
class StyleRecipe:
    """Immutable named presentation defaults for one recipe family."""

    name: str
    family: StyleFamily
    extends: str | None = None
    values: Mapping[str, str] = field(default_factory=dict)
    responsive: Mapping[str, Mapping[str, str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized_name = _normalize_name(self.name, label="recipe")
        if normalized_name != self.name:
            object.__setattr__(self, "name", normalized_name)
        if self.family not in RECIPE_FAMILIES and not _family_fields(self.family):
            raise error(
                HED_RECIPE_0004,
                title="Unknown recipe family",
                explanation=f"Family {self.family!r} is not registered in the recipe catalog.",
                remediation="Register a bounded RecipeFamily or use a built-in family.",
            )
        allowed = _family_fields(self.family)
        vocabularies = _family_vocabularies(self.family)
        cleaned: dict[str, str] = {}
        for key, value in self.values.items():
            if key not in allowed:
                raise error(
                    HED_RECIPE_0002,
                    title="Unlisted recipe field",
                    explanation=(f"Field {key!r} is not catalogued for family {self.family!r}."),
                    remediation=f"Use one of: {', '.join(sorted(allowed))}.",
                )
            vocab = vocabularies.get(key)
            if vocab is None:
                raise error(
                    HED_RECIPE_0002,
                    title="Recipe field vocabulary missing",
                    explanation=(
                        f"Field {key!r} has no bounded vocabulary in family {self.family!r}."
                    ),
                    remediation="Declare a finite field vocabulary on RecipeFamily.",
                )
            require_choice(value, vocab, label=key)
            cleaned[key] = value
        object.__setattr__(self, "values", dict(sorted(cleaned.items())))
        normalized_responsive: dict[str, dict[str, str]] = {}
        for field_name, conditions in self.responsive.items():
            if field_name not in _RESPONSIVE_RECIPE_FIELDS or field_name not in allowed:
                raise error(
                    HED_RECIPE_0002,
                    title="Unlisted responsive recipe field",
                    explanation=(
                        f"Field {field_name!r} is not supported for family {self.family!r}."
                    ),
                    remediation=f"Use one of: {', '.join(sorted(allowed))}.",
                )
            if not conditions:
                raise error(
                    HED_RECIPE_0002,
                    title="Empty responsive recipe field",
                    explanation=f"Responsive field {field_name!r} must declare a condition.",
                    remediation="Use base, sm, md, lg, or xl presentation conditions.",
                )
            normalized_conditions: dict[str, str] = {}
            for breakpoint, value in conditions.items():
                if breakpoint not in BREAKPOINTS:
                    raise error(
                        HED_RECIPE_0002,
                        title="Unknown responsive recipe breakpoint",
                        explanation=f"Breakpoint {breakpoint!r} is not supported.",
                        remediation=f"Use one of: {', '.join(BREAKPOINTS)}.",
                    )
                require_choice(value, _RESPONSIVE_RECIPE_FIELDS[field_name], label=field_name)
                normalized_conditions[breakpoint] = value
            normalized_responsive[field_name] = {
                key: normalized_conditions[key]
                for key in BREAKPOINTS
                if key in normalized_conditions
            }
        object.__setattr__(self, "responsive", dict(sorted(normalized_responsive.items())))
        if self.extends is not None:
            object.__setattr__(
                self, "extends", _normalize_name(self.extends, label="recipe parent")
            )

    @classmethod
    def control(
        cls,
        name: str,
        *,
        extends: str | None = None,
        size: Size | None = None,
        appearance: Appearance | None = None,
        emphasis: Emphasis | None = None,
        width: Width | None = None,
        responsive: Mapping[str, Mapping[str, str]] | None = None,
    ) -> StyleRecipe:
        values = {
            key: value
            for key, value in (
                ("size", size),
                ("appearance", appearance),
                ("emphasis", emphasis),
                ("width", width),
            )
            if value is not None
        }
        return cls(
            name=name, family="control", extends=extends, values=values, responsive=responsive or {}
        )

    @classmethod
    def surface(
        cls,
        name: str,
        *,
        extends: str | None = None,
        appearance: Appearance | None = None,
        density: Density | None = None,
        padding: Padding | None = None,
        elevation: Elevation | None = None,
        responsive: Mapping[str, Mapping[str, str]] | None = None,
    ) -> StyleRecipe:
        values = {
            key: value
            for key, value in (
                ("appearance", appearance),
                ("density", density),
                ("padding", padding),
                ("elevation", elevation),
            )
            if value is not None
        }
        return cls(
            name=name, family="surface", extends=extends, values=values, responsive=responsive or {}
        )

    @classmethod
    def data(
        cls,
        name: str,
        *,
        extends: str | None = None,
        density: Density | None = None,
        responsive: ResponsivePolicy | None = None,
        conditions: Mapping[str, Mapping[str, str]] | None = None,
    ) -> StyleRecipe:
        values = {
            key: value
            for key, value in (("density", density), ("responsive", responsive))
            if value is not None
        }
        return cls(
            name=name, family="data", extends=extends, values=values, responsive=conditions or {}
        )

    @classmethod
    def status(
        cls,
        name: str,
        *,
        extends: str | None = None,
        size: Size | None = None,
        appearance: Appearance | None = None,
    ) -> StyleRecipe:
        values = {
            key: value
            for key, value in (("size", size), ("appearance", appearance))
            if value is not None
        }
        return cls(name=name, family="status", extends=extends, values=values)

    @classmethod
    def content(
        cls,
        name: str,
        *,
        extends: str | None = None,
        role: TypographyRole | None = None,
        overflow: OverflowMode | None = None,
        measure: TypographyMeasure | None = None,
        effect: TypographyEffect | None = None,
        tracking: str | None = None,
        wrap: str | None = None,
    ) -> StyleRecipe:
        values = {
            key: value
            for key, value in (
                ("role", role),
                ("overflow", overflow),
                ("measure", measure),
                ("effect", effect),
                ("tracking", tracking),
                ("wrap", wrap),
            )
            if value is not None
        }
        return cls(name=name, family="content", extends=extends, values=values)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "family": self.family,
            "extends": self.extends,
            "values": dict(self.values),
            "responsive": {key: dict(value) for key, value in sorted(self.responsive.items())},
        }

    def responsive_markers(self) -> dict[str, str]:
        """Return stable data markers for provider-neutral responsive adapters."""

        return {
            f"hedron-recipe-{field_name}-{breakpoint}": value
            for field_name, conditions in sorted(self.responsive.items())
            for breakpoint, value in conditions.items()
        }


def _parse_catalog_values(raw: Sequence[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in raw:
        key, sep, value = item.partition("=")
        if not sep or not key or not value:
            raise error(
                HED_DESIGN_0001,
                title="Invalid builtin recipe value",
                explanation=f"Catalog entry {item!r} is not key=value.",
                remediation="Fix style-recipe-catalog-058.toml values.",
            )
        values[key] = value
    return values


def _build_builtin_catalog() -> tuple[dict[str, StyleRecipe], dict[str, str]]:
    specs: tuple[tuple[str, StyleFamily, tuple[str, ...], tuple[str, ...]], ...] = (
        (
            "primary_action",
            "control",
            ("appearance=solid", "emphasis=primary", "size=md"),
            (
                "form.primary_action",
                "workspace.create_action",
                "auth.login_action",
                "upload.submit_action",
                "task.submit_action",
            ),
        ),
        (
            "secondary_action",
            "control",
            ("appearance=outline", "emphasis=secondary", "size=md"),
            ("screen.secondary_action", "workspace.edit_action", "task.cancel_action"),
        ),
        (
            "destructive_action",
            "control",
            ("appearance=solid", "emphasis=danger", "size=md"),
            ("workspace.delete_action", "auth.logout_action"),
        ),
        (
            "page_surface",
            "surface",
            ("appearance=plain", "padding=md"),
            ("screen.surface",),
        ),
        (
            "form_surface",
            "surface",
            ("appearance=raised", "padding=md", "elevation=sm"),
            ("form.surface", "auth.form_surface", "upload.form_surface"),
        ),
        (
            "data_surface",
            "surface",
            ("appearance=plain", "padding=sm"),
            ("workspace.list_surface", "workspace.detail_surface"),
        ),
        (
            "dashboard_panel",
            "surface",
            ("appearance=raised", "padding=md", "elevation=sm"),
            ("dashboard.panel_surface",),
        ),
        (
            "dense_data",
            "data",
            ("density=compact", "responsive=scroll"),
            ("workspace.list_data", "dashboard.table_data"),
        ),
        (
            "inline_status",
            "status",
            ("appearance=soft", "size=sm"),
            ("task.status", "upload.status", "form.status"),
        ),
        (
            "metadata",
            "content",
            ("role=caption", "overflow=wrap"),
            ("screen.metadata", "workspace.metadata", "task.metadata"),
        ),
    )
    recipes: dict[str, StyleRecipe] = {}
    roles: dict[str, str] = {}
    for name, family, raw_values, facade_roles in specs:
        recipes[name] = StyleRecipe(
            name=name, family=family, values=_parse_catalog_values(raw_values)
        )
        for role in facade_roles:
            roles[role] = name
    return recipes, roles


_BUILTIN_RECIPES, _FEATURE_ROLES = _build_builtin_catalog()
BUILTIN_RECIPES: Final[Mapping[str, StyleRecipe]] = _BUILTIN_RECIPES
FEATURE_ROLES: Final[Mapping[str, str]] = _FEATURE_ROLES


@dataclass(frozen=True, slots=True)
class DesignSystemPlan:
    """Canonical ``hedron.design-system-plan/1`` explanation payload."""

    schema: str
    logical_id: str
    name: str
    base_theme: str
    inputs: Mapping[str, object]
    theme: Mapping[str, object]
    groups: Mapping[str, str]
    recipes: tuple[Mapping[str, object], ...]
    provenance: tuple[Mapping[str, object], ...]
    adjustments: tuple[Mapping[str, object], ...]
    assets: tuple[Mapping[str, object], ...]
    compatibility: Mapping[str, object]
    limitations: tuple[str, ...]
    digest: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "logical_id": self.logical_id,
            "name": self.name,
            "base_theme": self.base_theme,
            "inputs": dict(self.inputs),
            "theme": dict(self.theme),
            "groups": dict(self.groups),
            "recipes": list(self.recipes),
            "provenance": list(self.provenance),
            "adjustments": list(self.adjustments),
            "assets": list(self.assets),
            "compatibility": dict(self.compatibility),
            "limitations": list(self.limitations),
            "digest": self.digest,
        }


@dataclass(frozen=True, slots=True)
class DesignSystem:
    """Immutable portable design: Theme bridge plus named style recipes."""

    name: str
    _theme: Theme
    recipes: tuple[StyleRecipe, ...] = ()
    base_theme: str = "default"
    inputs: Mapping[str, object] = field(default_factory=dict)
    groups: Mapping[str, str] = field(default_factory=dict)
    provenance: tuple[Mapping[str, object], ...] = ()
    adjustments: tuple[Mapping[str, object], ...] = ()
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _normalize_name(self.name, label="design"))
        object.__setattr__(self, "recipes", tuple(self.recipes))
        object.__setattr__(self, "inputs", dict(self.inputs))
        object.__setattr__(self, "groups", dict(sorted(self.groups.items())))
        object.__setattr__(self, "provenance", tuple(dict(item) for item in self.provenance))
        object.__setattr__(self, "adjustments", tuple(dict(item) for item in self.adjustments))
        object.__setattr__(self, "limitations", tuple(self.limitations))
        seen: set[str] = set()
        for recipe in self.recipes:
            if recipe.name in seen:
                raise error(
                    HED_DESIGN_0002,
                    title="Duplicate recipe name",
                    explanation=f"Recipe {recipe.name!r} appears more than once.",
                    remediation="Pass replace=True via with_recipes, or rename the recipe.",
                )
            seen.add(recipe.name)

    @property
    def logical_id(self) -> str:
        return f"design:{self.name}"

    @classmethod
    def brand(
        cls,
        name: str,
        *,
        accent: str | Color,
        base: Theme | None = None,
        density: Density = "comfortable",
        geometry: GeometryPreset = "soft",
        typography: TypographyPreset = "system-sans",
        elevation: ElevationPreset = "subtle",
        motion: MotionPreset = "standard",
        navigation: NavigationPreset = "default",
        content_width: str = "default",
        recipes: Sequence[StyleRecipe] = (),
    ) -> DesignSystem:
        design_name = _normalize_name(name, label="design")
        try:
            requested_color = Color.parse(accent)
            if requested_color.alpha != 1.0:
                raise ValueError("brand accents must be opaque")
            seed = requested_color.to_hex()[:7]
        except (TypeError, ValueError) as exc:
            raise error(
                HED_BRAND_0001,
                title="Invalid brand accent",
                explanation=(
                    f"Accent {accent!r} is not a supported absolute color. "
                    "Use hex, rgb(), hsl(), or OKLCH input."
                ),
                remediation="Pass a safe absolute color such as '#2f6fed' or Color.oklch(...).",
            ) from exc
        require_choice(density, DENSITIES, label="density")
        if content_width not in ("narrow", "default", "wide", "full"):
            raise error(
                HED_DESIGN_0001,
                title="Invalid content width preset",
                explanation=f"content_width={content_width!r} is not supported.",
                remediation="Use narrow, default, wide, or full.",
            )
        if geometry not in _GEOMETRY_SHAPE:
            raise error(
                HED_DESIGN_0001,
                title="Invalid geometry preset",
                explanation=f"geometry={geometry!r} is not supported.",
                remediation=f"Use one of: {', '.join(_GEOMETRY_SHAPE)}.",
            )
        if typography not in _TYPOGRAPHY_FONT:
            raise error(
                HED_DESIGN_0001,
                title="Invalid typography preset",
                explanation=f"typography={typography!r} is not supported.",
                remediation=f"Use one of: {', '.join(_TYPOGRAPHY_FONT)}.",
            )
        if elevation not in _ELEVATION_MAP:
            raise error(
                HED_DESIGN_0001,
                title="Invalid elevation preset",
                explanation=f"elevation={elevation!r} is not supported.",
                remediation=f"Use one of: {', '.join(_ELEVATION_MAP)}.",
            )
        if motion not in _MOTION_DURATION:
            raise error(
                HED_DESIGN_0001,
                title="Invalid motion preset",
                explanation=f"motion={motion!r} is not supported.",
                remediation=f"Use one of: {', '.join(_MOTION_DURATION)}.",
            )
        if navigation not in _NAV_WIDTH:
            raise error(
                HED_DESIGN_0001,
                title="Invalid navigation preset",
                explanation=f"navigation={navigation!r} is not supported.",
                remediation=f"Use one of: {', '.join(_NAV_WIDTH)}.",
            )

        base_theme = base if base is not None else default_theme()
        light = compile_palette(seed)
        dark = compile_dark_palette(seed)

        adjustments: list[dict[str, object]] = []
        if light["color.accent"].lower() != seed.lower():
            adjustments.append(
                {
                    "target": "color.accent",
                    "requested": seed,
                    "resolved": light["color.accent"],
                    "reason": "contrast_search",
                    "measured_pairs": [["color.on-accent", "color.accent"]],
                    "code": HED_BRAND_0003,
                }
            )

        tokens = {
            **dict(base_theme.tokens),
            **light,
            "font.family": _TYPOGRAPHY_FONT[typography],
            "motion.duration": _MOTION_DURATION[motion],
            "focus.ring": f"3px solid {light['color.focus']}",
        }
        dark_mode = {
            **dark,
            "focus.ring": f"3px solid {dark['color.focus']}",
        }
        try:
            theme = Theme(
                name=design_name,
                tokens=tokens,
                modes={"dark": dark_mode},
                variants=dict(base_theme.variants),
                palette={
                    **dict(base_theme.palette),
                    "brand.seed": seed,
                    "brand.soft": light["color.accent-soft"],
                },
                density=density,
                shape=dict(_GEOMETRY_SHAPE[geometry]),
                nav_width=_NAV_WIDTH[navigation],
                content_width=content_width,
                elevation=dict(_ELEVATION_MAP[elevation]),
                parent=base_theme.name,
            )
        except Exception as exc:
            raise error(
                HED_DESIGN_0003,
                title="DesignSystem theme bridge failed",
                explanation=f"Could not build Theme for design {design_name!r}: {exc}",
                remediation="Correct brand inputs or start from a valid base Theme.",
            ) from exc

        contrast_findings = [
            item
            for item in contrast_diagnostics(theme)
            if item.severity == DiagnosticSeverity.ERROR
        ]
        if contrast_findings:
            raise error(
                HED_BRAND_0002,
                title="Brand contrast unsatisfied",
                explanation=(
                    f"Design {design_name!r} still has unsatisfied contrast pairs after search."
                ),
                remediation="Choose a different hex accent or author an explicit Theme.",
                context={
                    "findings": [item.code for item in contrast_findings],
                    "seed": seed,
                },
            )

        provenance: list[dict[str, object]] = [
            {
                "target": "palette.brand.seed",
                "source": "brand_input",
                "source_id": seed,
                "adjusted": bool(adjustments),
                "reason": "hedron.brand-palette/2",
            },
            {
                "target": "tokens.light",
                "source": "generated",
                "source_id": BRAND_ALGORITHM,
                "adjusted": bool(adjustments),
                "reason": "compile_palette",
            },
            {
                "target": "tokens.dark",
                "source": "generated",
                "source_id": BRAND_ALGORITHM,
                "adjusted": False,
                "reason": "compile_dark_palette",
            },
            {
                "target": "groups",
                "source": "preset",
                "source_id": "typed_groups",
                "adjusted": False,
                "reason": "finite_presets",
            },
        ]
        if base is not None:
            provenance.append(
                {
                    "target": "base_theme",
                    "source": "base_theme",
                    "source_id": base_theme.name,
                    "adjusted": False,
                    "reason": "explicit_base",
                }
            )
        else:
            provenance.append(
                {
                    "target": "base_theme",
                    "source": "builtin",
                    "source_id": "default",
                    "adjusted": False,
                    "reason": "default_theme",
                }
            )

        groups = {
            "density": density,
            "geometry": geometry,
            "typography": typography,
            "elevation": elevation,
            "motion": motion,
            "navigation": navigation,
        }
        return cls(
            name=design_name,
            _theme=theme,
            recipes=tuple(recipes),
            base_theme=base_theme.name,
            inputs={
                "accent": seed,
                "accent_requested": requested_color.to_css(fallback=False),
                "accent_space": requested_color.space,
                "palette_schema": "hedron.brand-palette/2",
                "algorithm": BRAND_ALGORITHM,
                "density": density,
                "geometry": geometry,
                "typography": typography,
                "elevation": elevation,
                "motion": motion,
                "navigation": navigation,
                "content_width": content_width,
            },
            groups=groups,
            provenance=tuple(provenance),
            adjustments=tuple(adjustments),
            limitations=(
                "absolute_color_brand_accent",
                "finite_typed_groups",
                "no_remote_fonts",
                "no_scope_recipe_defaults",
            ),
        )

    @classmethod
    def from_theme(
        cls,
        theme: Theme,
        *,
        recipes: Sequence[StyleRecipe] = (),
    ) -> DesignSystem:
        if not isinstance(theme, Theme):
            raise error(
                HED_DESIGN_0003,
                title="Invalid theme bridge input",
                explanation=f"from_theme expected Theme, got {type(theme).__name__}.",
                remediation="Pass a Theme instance from hedron_core.theme.",
            )
        return cls(
            name=theme.name,
            _theme=theme,
            recipes=tuple(recipes),
            base_theme=theme.parent or theme.name,
            inputs={"source": "theme", "theme": theme.name},
            groups={
                key: value
                for key, value in (
                    ("density", theme.density),
                    ("nav_width", theme.nav_width),
                    ("content_width", theme.content_width),
                    (
                        "typography_features",
                        ",".join(f"{k}={v}" for k, v in sorted(theme.typography_features.items()))
                        or None,
                    ),
                    (
                        "typography_role_features",
                        ";".join(
                            f"{role}:" + ",".join(f"{k}={v}" for k, v in sorted(values.items()))
                            for role, values in sorted(theme.typography_role_features.items())
                        )
                        or None,
                    ),
                )
                if value is not None
            },
            provenance=(
                {
                    "target": "theme",
                    "source": "base_theme",
                    "source_id": theme.name,
                    "adjusted": False,
                    "reason": "from_theme",
                },
            ),
            adjustments=(),
            limitations=("passthrough_theme",),
        )

    def to_theme(self) -> Theme:
        return self._theme

    def with_recipes(self, *recipes: StyleRecipe, replace: bool = False) -> DesignSystem:
        merged: dict[str, StyleRecipe] = {item.name: item for item in self.recipes}
        for recipe in recipes:
            if not isinstance(recipe, StyleRecipe):
                raise error(
                    HED_DESIGN_0001,
                    title="Invalid recipe",
                    explanation=f"Expected StyleRecipe, got {type(recipe).__name__}.",
                    remediation="Construct recipes with StyleRecipe.control/surface/...",
                )
            conflict = recipe.name in merged or recipe.name in BUILTIN_RECIPES
            if conflict and not replace:
                raise error(
                    HED_RECIPE_0004,
                    title="Duplicate recipe without replace",
                    explanation=(
                        f"Recipe {recipe.name!r} already exists "
                        f"({'builtin' if recipe.name in BUILTIN_RECIPES else 'design'}). "
                        "Pass replace=True to override."
                    ),
                    remediation="Call with_recipes(..., replace=True).",
                )
            merged[recipe.name] = recipe
        # Builtins stay available via catalog lookup; instance list stores overrides/customs.
        return dc_replace(self, recipes=tuple(merged.values()))

    def _recipe_catalog(self) -> dict[str, StyleRecipe]:
        catalog = dict(BUILTIN_RECIPES)
        for recipe in self.recipes:
            catalog[recipe.name] = recipe
        return catalog

    def _resolve_recipe(self, recipe: str | StyleRecipe) -> StyleRecipe:
        if isinstance(recipe, StyleRecipe):
            leaf = recipe
        else:
            catalog = self._recipe_catalog()
            name = _normalize_name(recipe, label="recipe")
            if name not in catalog:
                raise error(
                    HED_RECIPE_0001,
                    title="Unknown style recipe",
                    explanation=f"Recipe {recipe!r} is not in the design or builtin catalog.",
                    remediation="Define it with StyleRecipe.* or use a builtin name.",
                )
            leaf = catalog[name]
        return self._resolve_inheritance(leaf)

    def _resolve_inheritance(self, leaf: StyleRecipe) -> StyleRecipe:
        catalog = self._recipe_catalog()
        chain: list[StyleRecipe] = []
        current: StyleRecipe | None = leaf
        seen: set[str] = set()
        while current is not None:
            if current.name in seen:
                raise error(
                    HED_RECIPE_0003,
                    title="Recipe inheritance cycle",
                    explanation=f"Recipe {leaf.name!r} has a cyclic extends chain.",
                    remediation="Remove the cycle; inheritance must be acyclic.",
                )
            if len(chain) >= _MAX_RECIPE_DEPTH:
                raise error(
                    HED_RECIPE_0001,
                    title="Recipe inheritance too deep",
                    explanation=(
                        f"Recipe {leaf.name!r} exceeds the maximum inheritance depth "
                        f"of {_MAX_RECIPE_DEPTH}."
                    ),
                    remediation="Flatten the extends chain.",
                )
            seen.add(current.name)
            chain.append(current)
            parent_name = current.extends
            if parent_name is None:
                break
            parent = catalog.get(parent_name)
            if parent is None:
                raise error(
                    HED_RECIPE_0001,
                    title="Missing recipe parent",
                    explanation=(
                        f"Recipe {current.name!r} extends unknown parent {parent_name!r}."
                    ),
                    remediation="Define the parent recipe or remove extends.",
                )
            if parent.family != current.family:
                raise error(
                    HED_RECIPE_0002,
                    title="Cross-family recipe inheritance",
                    explanation=(
                        f"Recipe {current.name!r} ({current.family}) cannot extend "
                        f"{parent.name!r} ({parent.family})."
                    ),
                    remediation="Inherit only within the same recipe family.",
                )
            current = parent

        merged: dict[str, str] = {}
        responsive: dict[str, dict[str, str]] = {}
        for item in reversed(chain):
            merged.update(item.values)
            for field_name, conditions in item.responsive.items():
                responsive.setdefault(field_name, {}).update(conditions)
        return StyleRecipe(
            name=leaf.name,
            family=leaf.family,
            extends=leaf.extends,
            values=merged,
            responsive=responsive,
        )

    def apply(self, recipe: str | StyleRecipe, component: ComponentT, /) -> ComponentT:
        if not isinstance(component, Component):
            raise error(
                HED_RECIPE_0002,
                title="Recipe apply target invalid",
                explanation=f"apply() requires a Component, got {type(component).__name__}.",
                remediation="Pass a Hedron Component instance.",
            )
        resolved = self._resolve_recipe(recipe)
        component_name = component.logical_name or component.__class__.__name__
        compatible_components = _family_components(resolved.family)
        if component_name not in compatible_components:
            raise error(
                HED_RECIPE_0002,
                title="Incompatible recipe component",
                explanation=(
                    f"Recipe family {resolved.family!r} cannot apply to {component_name!r}."
                ),
                remediation=("Use one of: " + ", ".join(sorted(compatible_components)) + "."),
            )
        props = component.props
        eligible = set(_COMPONENT_FIELDS.get(component_name, frozenset()))
        # Registered extension families may target first-party or application
        # components whose optional props are not in the built-in map. The
        # family remains the authority for fields; the props model is the
        # second boundary that prevents arbitrary mutation.
        eligible.update(key for key in resolved.values if key in props.__class__.model_fields)
        fields = props.__class__.model_fields
        updates: dict[str, object] = {}
        for key, value in resolved.values.items():
            if key not in eligible or key not in fields:
                raise error(
                    HED_RECIPE_0002,
                    title="Incompatible recipe field",
                    explanation=(
                        f"Field {key!r} is not eligible on {component_name!r} "
                        f"for family {resolved.family!r}."
                    ),
                    remediation="Remove the field or choose a compatible component.",
                )
            existing = getattr(props, key, None)
            if existing is not None:
                # Explicit component value wins; do not overwrite.
                continue
            updates[key] = value
        if not updates:
            return _clone_component(component, props)
        new_props = props.model_copy(update=updates)
        return _clone_component(component, new_props)

    def explain(self) -> DesignSystemPlan:
        # Prefer instance overrides in declared order; otherwise list builtins.
        declared = [recipe.to_dict() for recipe in self.recipes]
        if not declared:
            declared = [BUILTIN_RECIPES[name].to_dict() for name in sorted(BUILTIN_RECIPES)]
        inputs: Mapping[str, object] = dict(sorted(self.inputs.items()))
        theme: Mapping[str, object] = _theme_summary(self._theme)
        groups: Mapping[str, str] = dict(sorted(self.groups.items()))
        provenance: tuple[Mapping[str, object], ...] = tuple(dict(item) for item in self.provenance)
        adjustments: tuple[Mapping[str, object], ...] = tuple(
            dict(item) for item in self.adjustments
        )
        compatibility: Mapping[str, object] = {
            "families": list(RECIPE_FAMILIES),
            "components": {
                family: sorted(components) for family, components in _FAMILY_COMPONENTS.items()
            },
            "feature_roles": dict(sorted(FEATURE_ROLES.items())),
        }
        payload: dict[str, object] = {
            "schema": PLAN_SCHEMA_ID,
            "logical_id": self.logical_id,
            "name": self.name,
            "base_theme": self.base_theme,
            "inputs": dict(inputs),
            "theme": dict(theme),
            "groups": dict(groups),
            "recipes": declared,
            "provenance": [dict(item) for item in provenance],
            "adjustments": [dict(item) for item in adjustments],
            "assets": [],
            "compatibility": dict(compatibility),
            "limitations": list(self.limitations),
        }
        digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
        return DesignSystemPlan(
            schema=PLAN_SCHEMA_ID,
            logical_id=self.logical_id,
            name=self.name,
            base_theme=self.base_theme,
            inputs=inputs,
            theme=theme,
            groups=groups,
            recipes=tuple(declared),
            provenance=provenance,
            adjustments=adjustments,
            assets=(),
            compatibility=compatibility,
            limitations=tuple(self.limitations),
            digest=digest,
        )
