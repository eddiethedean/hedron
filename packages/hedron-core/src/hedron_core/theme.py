"""Theme registration and token emission."""

from __future__ import annotations

import colorsys
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import cast

from hedron_core.codes import (
    HED_THEME_CONTRAST,
    HED_THEME_DUPLICATE,
    HED_THEME_ELEMENT_TOKEN,
    HED_THEME_INVALID,
    HED_THEME_MISSING_TOKEN,
    HED_THEME_STYLE_CONTRACT,
)
from hedron_core.diagnostics import Diagnostic, DiagnosticSeverity, error, make_diagnostic
from hedron_core.registry import ThemeMeta, get_registry, register_theme
from hedron_core.theme_platform import Color
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "FORCED_COLOR_TOKENS",
    "OVERLAY_ELEVATION_TOKENS",
    "PRINT_SAFE_TOKENS",
    "PRIVATE_SELECTORS_SUPPORTED",
    "REQUIRED_A11Y_TOKENS",
    "THEME_DENSITIES",
    "Theme",
    "aurora_theme",
    "builtin_themes",
    "compile_palette",
    "design_system_vars",
    "contrast_diagnostics",
    "contrast_ratio",
    "default_theme",
    "emit_theme_css",
    "ensure_builtin_themes_registered",
    "ensure_default_theme_registered",
    "get_theme",
    "register_theme_instance",
    "run_visual_conformance",
    "theme_element_compatibility",
    "validate_element_style_contract",
    "validate_theme_tokens",
]

# Custom themes and visual conformance never authorize private CSS selectors.
PRIVATE_SELECTORS_SUPPORTED = False

REQUIRED_A11Y_TOKENS: tuple[str, ...] = (
    "color.bg",
    "color.fg",
    "color.accent",
    "color.focus",
    "color.danger",
    "color.muted",
    "font.family",
    "font.size",
    "space.unit",
    "motion.duration",
    "focus.ring",
)

# Element CSS must continue to consume these semantic tokens inside
# ``@media (forced-colors: active)`` rather than relying on literal colors.
FORCED_COLOR_TOKENS: tuple[str, ...] = (
    "color.bg",
    "color.fg",
    "color.accent",
    "color.focus",
    "color.danger",
)

# Element print rules should resolve through this bounded token set and avoid
# motion, translucent surfaces, or color-only state communication.
PRINT_SAFE_TOKENS: tuple[str, ...] = (
    "color.bg",
    "color.fg",
    "font.family",
    "font.size",
)

# Mirrors the shared appearance vocabulary in
# ``hedron_core.builtins.appearance`` without importing the built-ins package.
THEME_DENSITIES: tuple[str, ...] = ("compact", "comfortable", "spacious")

# Overlays, popovers, and toasts resolve stacking through these tokens so no
# application CSS is required to place chrome above content. Themes override an
# entry by using the same key in ``Theme.elevation``.
OVERLAY_ELEVATION_TOKENS: Mapping[str, str] = {
    "overlay-scrim": "rgb(9 12 20 / 55%)",
    "overlay-radius": "0.75rem",
    "overlay-shadow": "0 1.25rem 3rem rgb(9 12 20 / 22%)",
    "layer-sticky": "700",
    "layer-dropdown": "800",
    "layer-overlay": "900",
    "layer-toast": "1000",
}

# Design-system values are emitted verbatim into CSS custom properties, so they
# must not be able to close a declaration or open a rule/at-rule.
_UNSAFE_CSS_VALUE = re.compile(r"[;{}<>@\\]|url\s*\(|/\*", re.IGNORECASE)
_LENGTH_VALUE = re.compile(r"^\d+(\.\d+)?(rem|em|px|%|vw|ch)$")
_HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def _validated_css_value(field_name: str, key: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise error(
            HED_THEME_INVALID,
            title="Invalid design-system value",
            explanation=f"{field_name}[{key!r}] must be a non-empty string.",
            remediation="Pass a CSS value such as '0.5rem' or '#2563eb'.",
        )
    if _UNSAFE_CSS_VALUE.search(value):
        raise error(
            HED_THEME_INVALID,
            title="Unsafe design-system value",
            explanation=(
                f"{field_name}[{key!r}]={value!r} contains characters that could "
                "escape a CSS declaration."
            ),
            remediation="Use plain CSS token values without ';', '{', '@', or url().",
        )
    return value.strip()


def _validated_token_key(field_name: str, key: str) -> str:
    if not key or not re.fullmatch(r"[A-Za-z][A-Za-z0-9._-]*", key):
        raise error(
            HED_THEME_INVALID,
            title="Invalid design-system token name",
            explanation=f"{field_name} key {key!r} is not a safe token name.",
            remediation="Use dotted or hyphenated alphanumeric names such as 'accent.soft'.",
        )
    return key


def _contract_names(value: object) -> set[str]:
    if isinstance(value, str):
        return {item for item in re.split(r"[\s,]+", value) if item}
    if isinstance(value, (tuple, list, set, frozenset)):
        if any(not isinstance(item, str) or not item for item in value):
            raise ValueError("element style contract names must be non-empty strings")
        return set(value)
    raise TypeError("element style contract entries must be strings or string collections")


def validate_element_style_contract(
    style_contract: Mapping[str, object],
    parts: tuple[str, ...] | list[str],
    slots: Mapping[str, str],
    tokens: tuple[str, ...] | list[str],
) -> None:
    """Ensure style-contract references agree with the element ABI metadata."""
    unknown = set(style_contract) - {"parts", "slots", "tokens"}
    if unknown:
        raise ValueError(f"unknown element style contract keys: {', '.join(sorted(unknown))}")
    declared = {
        "parts": set(parts),
        "slots": set(slots),
        "tokens": set(tokens),
    }
    for kind, available in declared.items():
        if kind not in style_contract:
            continue
        referenced = _contract_names(style_contract[kind])
        if any("*" in name for name in referenced):
            continue
        missing = referenced - available
        if missing:
            raise ValueError(
                f"style contract references undeclared {kind}: {', '.join(sorted(missing))}"
            )


def theme_element_compatibility(
    theme_tokens: Mapping[str, str] | tuple[str, ...] | list[str] | set[str],
    element_tokens: tuple[str, ...] | list[str] | set[str],
) -> list[str]:
    """Return element token names not supplied by a theme."""
    available = set(theme_tokens)
    return sorted(set(element_tokens) - available)


def _theme_token_map(theme: object) -> Mapping[str, str] | None:
    tokens = getattr(theme, "tokens", None)
    if isinstance(tokens, Mapping):
        return cast(Mapping[str, str], tokens)
    return None


def run_visual_conformance(
    theme: object | None = None,
    *,
    element_ids: Sequence[str] | None = None,
) -> list[Diagnostic]:
    """Run reusable visual-conformance checks; empty list means ok.

    When ``theme`` is provided, requires ``REQUIRED_A11Y_TOKENS``,
    ``FORCED_COLOR_TOKENS``, and ``PRINT_SAFE_TOKENS``. Registered element
    style contracts are validated when present. Private CSS selectors are
    never claimed as supported (``PRIVATE_SELECTORS_SUPPORTED`` is False).
    """
    diagnostics: list[Diagnostic] = []
    token_map = _theme_token_map(theme) if theme is not None else None
    if token_map is not None:
        for label, required in (
            ("accessibility", REQUIRED_A11Y_TOKENS),
            ("forced-colors", FORCED_COLOR_TOKENS),
            ("print-safe", PRINT_SAFE_TOKENS),
        ):
            missing = [name for name in required if name not in token_map]
            if missing:
                diagnostics.append(
                    make_diagnostic(
                        HED_THEME_MISSING_TOKEN,
                        severity=DiagnosticSeverity.ERROR,
                        title=f"Theme missing {label} tokens",
                        explanation=f"Missing tokens: {', '.join(missing)}.",
                        remediation=(
                            "Provide all required semantic tokens for custom themes "
                            "(default_styles=False)."
                        ),
                        context={"missing": missing, "set": label},
                    )
                )

    registry = get_registry()
    elements = sorted(registry.element_definitions(), key=lambda item: item.logical_id)
    if element_ids is not None:
        wanted = set(element_ids)
        present = {item.logical_id for item in elements}
        for missing_id in sorted(wanted - present):
            diagnostics.append(
                make_diagnostic(
                    HED_THEME_ELEMENT_TOKEN,
                    severity=DiagnosticSeverity.WARNING,
                    title="Element not registered for visual conformance",
                    explanation=f"No element definition for {missing_id!r}.",
                    remediation="Register the element definition before conformance.",
                    component_id=missing_id,
                )
            )
        elements = [item for item in elements if item.logical_id in wanted]

    for element in elements:
        if element.style_contract:
            try:
                validate_element_style_contract(
                    element.style_contract,
                    parts=element.parts,
                    slots=element.slots,
                    tokens=element.tokens,
                )
            except (TypeError, ValueError) as exc:
                diagnostics.append(
                    make_diagnostic(
                        HED_THEME_STYLE_CONTRACT,
                        severity=DiagnosticSeverity.ERROR,
                        title="Element style contract failed",
                        explanation=str(exc),
                        remediation=(
                            "Align style_contract parts/slots/tokens with the "
                            "element ABI metadata. Private selectors are not supported."
                        ),
                        component_id=element.logical_id,
                        context={"private_selectors_supported": False},
                    )
                )
        if token_map is not None and element.tokens:
            missing_tokens = theme_element_compatibility(token_map, element.tokens)
            if missing_tokens:
                diagnostics.append(
                    make_diagnostic(
                        HED_THEME_ELEMENT_TOKEN,
                        severity=DiagnosticSeverity.WARNING,
                        title="Theme missing element tokens",
                        explanation=(
                            f"Element {element.logical_id!r} requires tokens not "
                            f"supplied by the theme: {', '.join(missing_tokens)}."
                        ),
                        remediation="Extend the theme with the missing semantic tokens.",
                        component_id=element.logical_id,
                        context={"missing": missing_tokens},
                    )
                )
    return diagnostics


@dataclass(frozen=True, slots=True)
class Theme:
    """Python-native application design system.

    ``tokens``/``modes``/``variants`` are the phase 0.9 semantic contract.
    ``palette``, ``density``, ``shape``, ``nav_width``, and ``elevation`` are the
    optional 0.54 design-system fields; each is emitted as CSS custom properties
    by :func:`emit_theme_css`. ``parent`` records the theme this one was derived
    from via :meth:`extend`.
    """

    name: str
    tokens: Mapping[str, str]
    modes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    variants: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    palette: Mapping[str, str] = field(default_factory=dict)
    density: str | None = None
    shape: Mapping[str, str] = field(default_factory=dict)
    nav_width: str | None = None
    elevation: Mapping[str, str] = field(default_factory=dict)
    parent: str | None = None
    accessibility_modes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or not self.name.replace("-", "").replace("_", "").isalnum():
            raise error(
                HED_THEME_INVALID,
                title="Invalid theme name",
                explanation=f"Theme name {self.name!r} is not a valid identifier.",
                remediation="Use a simple alphanumeric theme name.",
            )
        validate_theme_tokens(self.tokens)
        for variant, values in self.variants.items():
            _validated_token_key("variant", variant)
            if not re.fullmatch(r"[A-Za-z0-9_-]+", variant):
                raise error(
                    HED_THEME_INVALID,
                    title="Invalid theme variant name",
                    explanation=f"variant={variant!r} is not a safe finite variant name.",
                    remediation="Use letters, numbers, underscores, and hyphens only.",
                )
            for key, value in values.items():
                _validated_token_key(f"variant.{variant}", key)
                _validated_css_value(f"variant.{variant}", key, value)
        for field_name, mapping in (
            ("palette", self.palette),
            ("shape", self.shape),
            ("elevation", self.elevation),
        ):
            for key, value in mapping.items():
                _validated_token_key(field_name, key)
                _validated_css_value(field_name, key, value)
        if self.density is not None and self.density not in THEME_DENSITIES:
            raise error(
                HED_THEME_INVALID,
                title="Invalid theme density",
                explanation=f"density={self.density!r} is not a supported density.",
                remediation=f"Use one of: {', '.join(THEME_DENSITIES)}.",
            )
        if self.nav_width is not None and not _LENGTH_VALUE.match(self.nav_width.strip()):
            raise error(
                HED_THEME_INVALID,
                title="Invalid theme nav_width",
                explanation=f"nav_width={self.nav_width!r} is not a safe CSS length.",
                remediation="Use a length such as '15rem' or '240px'.",
            )
        if self.parent is not None and (
            not self.parent or not self.parent.replace("-", "").replace("_", "").isalnum()
        ):
            raise error(
                HED_THEME_INVALID,
                title="Invalid parent theme name",
                explanation=f"parent={self.parent!r} is not a valid theme identifier.",
                remediation="Use the name of an existing theme, or None.",
            )
        for mode, values in self.accessibility_modes.items():
            if mode not in {"forced-colors", "more-contrast"}:
                raise error(
                    HED_THEME_INVALID,
                    title="Invalid accessibility theme mode",
                    explanation=f"accessibility mode {mode!r} is not supported.",
                    remediation="Use 'forced-colors' or 'more-contrast'.",
                )
            for key, value in values.items():
                _validated_token_key(f"accessibility.{mode}", key)
                _validated_css_value(f"accessibility.{mode}", key, value)

    def extend(
        self,
        name: str,
        *,
        tokens: Mapping[str, str] | None = None,
        modes: Mapping[str, Mapping[str, str]] | None = None,
        variants: Mapping[str, Mapping[str, str]] | None = None,
        palette: Mapping[str, str] | None = None,
        density: str | None = None,
        shape: Mapping[str, str] | None = None,
        nav_width: str | None = None,
        elevation: Mapping[str, str] | None = None,
        accessibility_modes: Mapping[str, Mapping[str, str]] | None = None,
    ) -> Theme:
        """Return a new theme that inherits this theme's values by name.

        Overrides are merged per mapping, so a derived theme only restates what
        it changes. The result records ``parent=self.name`` and is fully
        resolved, which keeps ``emit_theme_css`` and scoped
        ``data-hedron-theme`` subtrees independent of registration order.
        """
        merged_modes: dict[str, Mapping[str, str]] = {
            mode: dict(values) for mode, values in self.modes.items()
        }
        for mode, values in (modes or {}).items():
            merged_modes[mode] = {**dict(merged_modes.get(mode, {})), **dict(values)}
        merged_variants: dict[str, Mapping[str, str]] = {
            variant: dict(values) for variant, values in self.variants.items()
        }
        for variant, values in (variants or {}).items():
            merged_variants[variant] = {**dict(merged_variants.get(variant, {})), **dict(values)}
        merged_accessibility: dict[str, Mapping[str, str]] = {
            mode: dict(values) for mode, values in self.accessibility_modes.items()
        }
        for mode, values in (accessibility_modes or {}).items():
            merged_accessibility[mode] = {
                **dict(merged_accessibility.get(mode, {})),
                **dict(values),
            }
        return replace(
            self,
            name=name,
            tokens={**dict(self.tokens), **dict(tokens or {})},
            modes=merged_modes,
            variants=merged_variants,
            palette={**dict(self.palette), **dict(palette or {})},
            density=self.density if density is None else density,
            shape={**dict(self.shape), **dict(shape or {})},
            nav_width=self.nav_width if nav_width is None else nav_width,
            elevation={**dict(self.elevation), **dict(elevation or {})},
            parent=self.name,
            accessibility_modes=merged_accessibility,
        )


def validate_theme_tokens(tokens: Mapping[str, str]) -> None:
    missing = [t for t in REQUIRED_A11Y_TOKENS if t not in tokens]
    if missing:
        raise error(
            HED_THEME_MISSING_TOKEN,
            title="Theme missing required accessibility tokens",
            explanation=f"Missing tokens: {', '.join(missing)}.",
            remediation="Provide all required a11y tokens listed in Theme docs.",
            context=cast(Mapping[str, JsonValue], {"missing": missing}),
        )


def default_theme() -> Theme:
    return Theme(
        name="default",
        tokens={
            "color.bg": "#f6f8fb",
            "color.surface": "#ffffff",
            "color.surface-muted": "#f0f3f8",
            "color.fg": "#172033",
            "color.accent": "#2563eb",
            "color.on-accent": "#ffffff",
            "color.focus": "#2563eb",
            "color.danger": "#c73939",
            "color.on-danger": "#ffffff",
            "color.muted": "#647084",
            "font.family": "system-ui, sans-serif",
            "font.size": "1rem",
            "space.unit": "0.25rem",
            "motion.duration": "150ms",
            "focus.ring": "3px solid #2563eb",
        },
        modes={
            "dark": {
                "color.bg": "#0d121c",
                "color.surface": "#151c28",
                "color.surface-muted": "#1b2432",
                "color.fg": "#eef3fa",
                "color.accent": "#7ca7ff",
                "color.on-accent": "#071a3c",
                "color.focus": "#7ca7ff",
                "color.danger": "#ff8585",
                "color.on-danger": "#321214",
                "color.muted": "#9ba8ba",
            }
        },
    )


def aurora_theme() -> Theme:
    """Return Hedron's expressive violet first-party theme."""
    return Theme(
        name="aurora",
        tokens={
            "color.bg": "#f7f5ff",
            "color.surface": "#ffffff",
            "color.surface-muted": "#eeeaff",
            "color.fg": "#221a35",
            "color.accent": "#6d3ce7",
            "color.on-accent": "#ffffff",
            "color.focus": "#6d3ce7",
            "color.danger": "#b4234d",
            "color.on-danger": "#ffffff",
            "color.muted": "#675e78",
            "font.family": '"Avenir Next", "Segoe UI", system-ui, sans-serif',
            "font.size": "1rem",
            "space.unit": "0.25rem",
            "motion.duration": "170ms",
            "focus.ring": "3px solid #8b5cf6",
        },
        modes={
            "dark": {
                "color.bg": "#120d1f",
                "color.surface": "#1d162d",
                "color.surface-muted": "#261c3a",
                "color.fg": "#f8f4ff",
                "color.accent": "#c4a7ff",
                "color.on-accent": "#20123a",
                "color.focus": "#c4a7ff",
                "color.danger": "#ff87a9",
                "color.on-danger": "#3d0718",
                "color.muted": "#b9abc9",
                "focus.ring": "3px solid #c4a7ff",
            }
        },
    )


def builtin_themes() -> tuple[Theme, ...]:
    """Return all themes shipped by Hedron in stable display order."""
    return (default_theme(), aurora_theme())


def _token_to_css_var(name: str) -> str:
    return "--hedron-" + name.replace(".", "-")


def design_system_vars(theme: Theme) -> dict[str, str]:
    """Return the CSS custom properties for a theme's design-system fields.

    Always includes the overlay/stacking contract so overlays, popovers, and
    toasts resolve without application CSS.
    """
    variables: dict[str, str] = {"--hedron-theme-name": theme.name}
    if theme.parent:
        variables["--hedron-theme-parent"] = theme.parent
    for key, value in sorted(theme.palette.items()):
        variables[f"--hedron-palette-{key.replace('.', '-')}"] = value
    if theme.density:
        variables["--hedron-density"] = theme.density
    for key, value in sorted(theme.shape.items()):
        variables[f"--hedron-shape-{key.replace('.', '-')}"] = value
    if theme.nav_width:
        variables["--hedron-nav-width"] = theme.nav_width
    overlays = {**OVERLAY_ELEVATION_TOKENS}
    extra: dict[str, str] = {}
    for key, value in theme.elevation.items():
        normalized = key.replace(".", "-")
        if normalized in overlays:
            overlays[normalized] = value
        else:
            extra[normalized] = value
    for key in sorted(overlays):
        variables[f"--hedron-{key}"] = overlays[key]
    for key in sorted(extra):
        variables[f"--hedron-elevation-{key}"] = extra[key]
    return variables


def emit_theme_css(theme: Theme) -> str:
    """Emit cascade-layer tokens CSS for a theme.

    Tokens are emitted on ``:root`` and repeated for the scoped
    ``[data-hedron-theme="<name>"]`` selector so a page or subtree can opt into
    a named theme without application CSS.
    """
    design = design_system_vars(theme)
    lines = ["@layer tokens {", ":root {"]
    for key, value in sorted(theme.tokens.items()):
        lines.append(f"  {_token_to_css_var(key)}: {value};")
    for key in design:
        lines.append(f"  {key}: {design[key]};")
    lines.append("}")
    for variant, values in sorted(theme.variants.items()):
        lines.append(f'[data-hedron-theme="{theme.name}"][data-hedron-variant="{variant}"] {{')
        for key, value in sorted(values.items()):
            lines.append(f"  {_token_to_css_var(key)}: {value};")
        lines.append("}")
    lines.append(f'[data-hedron-theme="{theme.name}"] {{')
    for key, value in sorted(theme.tokens.items()):
        lines.append(f"  {_token_to_css_var(key)}: {value};")
    for key in design:
        lines.append(f"  {key}: {design[key]};")
    lines.append("}")
    dark = theme.modes.get("dark")
    if dark:
        lines.append("@media (prefers-color-scheme: dark) {")
        lines.append('  :root:not([data-theme="light"]) {')
        for key, value in sorted(dark.items()):
            lines.append(f"    {_token_to_css_var(key)}: {value};")
        lines.append("  }")
        lines.append(
            f'  [data-hedron-theme="{theme.name}"]:not([data-theme="light"])'
            f':not([data-hedron-color-mode="light"]) {{'
        )
        for key, value in sorted(dark.items()):
            lines.append(f"    {_token_to_css_var(key)}: {value};")
        lines.append("  }")
        lines.append("}")
        lines.append(':root[data-theme="dark"] {')
        for key, value in sorted(dark.items()):
            lines.append(f"  {_token_to_css_var(key)}: {value};")
        lines.append("}")
        lines.append(
            f'[data-hedron-theme="{theme.name}"][data-theme="dark"], '
            f'[data-hedron-theme="{theme.name}"][data-hedron-color-mode="dark"] {{'
        )
        for key, value in sorted(dark.items()):
            lines.append(f"  {_token_to_css_var(key)}: {value};")
        lines.append("}")
        # Explicit light preference must defeat system dark preference.
        lines.append(':root[data-theme="light"] {')
        for key, value in sorted(theme.tokens.items()):
            lines.append(f"  {_token_to_css_var(key)}: {value};")
        lines.append("}")
        lines.append(
            f'[data-hedron-theme="{theme.name}"][data-theme="light"], '
            f'[data-hedron-theme="{theme.name}"][data-hedron-color-mode="light"] {{'
        )
        for key, value in sorted(theme.tokens.items()):
            lines.append(f"  {_token_to_css_var(key)}: {value};")
        lines.append("}")
    for mode, values in sorted(theme.accessibility_modes.items()):
        if mode == "forced-colors":
            lines.append("@media (forced-colors: active) {")
            lines.append("  :root {")
            lines.append("    forced-color-adjust: auto;")
        else:
            lines.append("@media (prefers-contrast: more) {")
            lines.append("  :root {")
        for key, value in sorted(values.items()):
            lines.append(f"    {_token_to_css_var(key)}: {value};")
        lines.append("  }")
        lines.append("}")
    lines.append("@media (prefers-reduced-motion: reduce) {")
    lines.append("  :root {")
    lines.append(f"    {_token_to_css_var('motion.duration')}: 0ms;")
    lines.append("  }")
    lines.append("}")
    lines.append("}")
    return "\n".join(lines) + "\n"


def register_theme_instance(theme: Theme) -> None:
    try:
        register_theme(
            logical_id=theme.name,
            name=theme.name,
            tokens=theme.tokens,
            modes=theme.modes,
            variants=theme.variants,
            accessibility_modes=theme.accessibility_modes,
        )
    except Exception as exc:
        # Re-raise duplicates with theme code if already mapped.
        if "already registered" in str(exc):
            raise error(
                HED_THEME_DUPLICATE,
                title="Duplicate theme registration",
                explanation=f"Theme {theme.name!r} is already registered.",
                remediation="Use unique theme names.",
            ) from exc
        raise


def _ensure_theme_registered(theme: Theme) -> None:
    registry = get_registry()
    if registry.get_theme(theme.name) is not None:
        return
    try:
        register_theme_instance(theme)
    except Exception as exc:
        # Sealed builder after another app lifespan: if the active snapshot already
        # has the theme, succeed; otherwise re-raise.
        if "sealed" in str(exc).lower() and get_registry().get_theme(theme.name) is not None:
            return
        raise


def ensure_builtin_themes_registered() -> tuple[Theme, ...]:
    """Idempotently register every theme distributed with Hedron."""
    themes = builtin_themes()
    for theme in themes:
        _ensure_theme_registered(theme)
    return themes


def ensure_default_theme_registered() -> Theme:
    """Register built-in themes and return the backwards-compatible default."""
    return ensure_builtin_themes_registered()[0]


def get_theme(name: str | None) -> ThemeMeta | None:
    if not name:
        return None
    return get_registry().get_theme(name)


def _parse_hex(value: str | Color) -> tuple[float, float, float]:
    if isinstance(value, Color):
        return value.to_srgb()
    raw = value.strip()
    if not _HEX_COLOR.match(raw):
        raise error(
            HED_THEME_INVALID,
            title="Invalid seed color",
            explanation=f"Color {value!r} is not a 3- or 6-digit hex value.",
            remediation="Pass a hex color such as '#2563eb'.",
        )
    digits = raw[1:]
    if len(digits) == 3:
        digits = "".join(ch * 2 for ch in digits)
    return tuple(int(digits[index : index + 2], 16) / 255 for index in (0, 2, 4))  # type: ignore[return-value]


def _to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(max(0.0, min(1.0, channel)) * 255):02x}" for channel in rgb)


def _relative_luminance(color: str) -> float:
    channels = _parse_hex(color)
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    """Return the WCAG 2.1 contrast ratio between two hex colors."""
    lighter, darker = sorted(
        (_relative_luminance(first), _relative_luminance(second)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


def _with_lightness(hue: float, saturation: float, lightness: float) -> str:
    return _to_hex(colorsys.hls_to_rgb(hue, lightness, saturation))


def _darken_until(hue: float, saturation: float, against: str, target: float, start: float) -> str:
    """Walk lightness down until the color clears ``target`` against ``against``."""
    lightness = start
    while lightness > 0.0:
        candidate = _with_lightness(hue, saturation, lightness)
        if contrast_ratio(candidate, against) >= target:
            return candidate
        lightness -= 0.01
    return "#000000"


def compile_palette(seed: str | Color) -> dict[str, str]:
    """Compile an accessible semantic palette from a single seed color.

    The result is a ``Theme.tokens``-compatible mapping whose text pairs meet
    WCAG AA (4.5:1) by construction, so applications choose one brand color
    instead of authoring CSS.
    """
    hue, _seed_lightness, saturation = colorsys.rgb_to_hls(*_parse_hex(seed))
    saturation = max(saturation, 0.35)
    surface = "#ffffff"
    background = _with_lightness(hue, min(saturation, 0.45), 0.975)
    surface_muted = _with_lightness(hue, min(saturation, 0.4), 0.945)
    foreground = _darken_until(hue, min(saturation, 0.45), background, 7.0, 0.25)
    muted = _darken_until(hue, min(saturation, 0.3), background, 4.5, 0.6)
    border = _with_lightness(hue, min(saturation, 0.35), 0.86)
    accent = _darken_until(hue, saturation, surface, 4.5, 0.55)
    danger = _darken_until(0.995, 0.6, surface, 4.5, 0.55)
    return {
        "color.bg": background,
        "color.surface": surface,
        "color.surface-muted": surface_muted,
        "color.fg": foreground,
        "color.muted": muted,
        "color.border": border,
        "color.accent": accent,
        "color.accent-soft": _with_lightness(hue, min(saturation, 0.6), 0.93),
        "color.on-accent": "#ffffff",
        "color.focus": accent,
        "color.danger": danger,
        "color.on-danger": "#ffffff",
    }


# (foreground token, background token, minimum ratio, severity)
_CONTRAST_PAIRS: tuple[tuple[str, str, float, DiagnosticSeverity], ...] = (
    ("color.fg", "color.bg", 4.5, DiagnosticSeverity.ERROR),
    ("color.muted", "color.bg", 4.5, DiagnosticSeverity.ERROR),
    ("color.on-accent", "color.accent", 4.5, DiagnosticSeverity.ERROR),
    ("color.on-danger", "color.danger", 4.5, DiagnosticSeverity.ERROR),
    ("color.accent", "color.bg", 3.0, DiagnosticSeverity.WARNING),
)


def _contrast_diagnostics_for(
    tokens: Mapping[str, str], *, mode: str, theme_name: str
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for foreground, background, minimum, severity in _CONTRAST_PAIRS:
        first = tokens.get(foreground)
        second = tokens.get(background)
        if first is None or second is None:
            continue
        if not (_HEX_COLOR.match(first.strip()) and _HEX_COLOR.match(second.strip())):
            # Non-literal values (var(), color-mix(), keywords) are not measurable here.
            continue
        ratio = contrast_ratio(first, second)
        if ratio + 1e-9 >= minimum:
            continue
        diagnostics.append(
            make_diagnostic(
                HED_THEME_CONTRAST,
                severity=severity,
                title="Theme contrast below target",
                explanation=(
                    f"{theme_name} ({mode}): {foreground} on {background} is "
                    f"{ratio:.2f}:1, below the {minimum:.1f}:1 target."
                ),
                remediation=(
                    "Adjust the token pair, or derive tokens with "
                    "compile_palette(seed) which meets AA by construction."
                ),
                context=cast(
                    Mapping[str, JsonValue],
                    {
                        "mode": mode,
                        "foreground": foreground,
                        "background": background,
                        "ratio": round(ratio, 3),
                        "minimum": minimum,
                    },
                ),
            )
        )
    return diagnostics


def contrast_diagnostics(theme: Theme | Mapping[str, str]) -> list[Diagnostic]:
    """Return contrast findings for a theme (all modes) or a token mapping.

    An empty list means every measurable text pair clears WCAG AA and every
    non-text accent pair clears 3:1.
    """
    if isinstance(theme, Theme):
        diagnostics = _contrast_diagnostics_for(theme.tokens, mode="light", theme_name=theme.name)
        for mode, overrides in sorted(theme.modes.items()):
            merged = {**dict(theme.tokens), **dict(overrides)}
            diagnostics.extend(_contrast_diagnostics_for(merged, mode=mode, theme_name=theme.name))
        return diagnostics
    return _contrast_diagnostics_for(theme, mode="light", theme_name="tokens")
