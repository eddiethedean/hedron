"""Theme registration and token emission."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import cast

from hedron_core.codes import (
    HED_THEME_DUPLICATE,
    HED_THEME_ELEMENT_TOKEN,
    HED_THEME_INVALID,
    HED_THEME_MISSING_TOKEN,
    HED_THEME_STYLE_CONTRACT,
)
from hedron_core.diagnostics import Diagnostic, DiagnosticSeverity, error, make_diagnostic
from hedron_core.registry import ThemeMeta, get_registry, register_theme
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "FORCED_COLOR_TOKENS",
    "PRINT_SAFE_TOKENS",
    "PRIVATE_SELECTORS_SUPPORTED",
    "REQUIRED_A11Y_TOKENS",
    "Theme",
    "aurora_theme",
    "builtin_themes",
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
    name: str
    tokens: Mapping[str, str]
    modes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    variants: Mapping[str, Mapping[str, str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or not self.name.replace("-", "").replace("_", "").isalnum():
            raise error(
                HED_THEME_INVALID,
                title="Invalid theme name",
                explanation=f"Theme name {self.name!r} is not a valid identifier.",
                remediation="Use a simple alphanumeric theme name.",
            )
        validate_theme_tokens(self.tokens)


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


def emit_theme_css(theme: Theme) -> str:
    """Emit cascade-layer tokens CSS for a theme."""
    lines = ["@layer tokens {", ":root {"]
    for key, value in sorted(theme.tokens.items()):
        lines.append(f"  {_token_to_css_var(key)}: {value};")
    lines.append("}")
    dark = theme.modes.get("dark")
    if dark:
        lines.append("@media (prefers-color-scheme: dark) {")
        lines.append('  :root:not([data-theme="light"]) {')
        for key, value in sorted(dark.items()):
            lines.append(f"    {_token_to_css_var(key)}: {value};")
        lines.append("  }")
        lines.append("}")
        lines.append(':root[data-theme="dark"] {')
        for key, value in sorted(dark.items()):
            lines.append(f"  {_token_to_css_var(key)}: {value};")
        lines.append("}")
        # Explicit light preference must defeat system dark preference.
        lines.append(':root[data-theme="light"] {')
        for key, value in sorted(theme.tokens.items()):
            lines.append(f"  {_token_to_css_var(key)}: {value};")
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
    themes = ensure_builtin_themes_registered()
    theme = themes[0]
    return theme


def get_theme(name: str | None) -> ThemeMeta | None:
    if not name:
        return None
    return get_registry().get_theme(name)
