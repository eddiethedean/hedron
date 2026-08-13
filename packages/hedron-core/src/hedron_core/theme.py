"""Theme registration and token emission."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import cast

from hedron_core.codes import HED_THEME_DUPLICATE, HED_THEME_INVALID, HED_THEME_MISSING_TOKEN
from hedron_core.diagnostics import error
from hedron_core.registry import ThemeMeta, get_registry, register_theme
from hedron_core.typing_aliases import JsonValue

__all__ = [
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
    "validate_theme_tokens",
]

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
