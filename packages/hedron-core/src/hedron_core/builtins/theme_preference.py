"""Server-first theme selection primitives (phase 0.60)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Literal

from hedron_core.builtins._base import class_names, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.registry import get_registry
from hedron_core.security import SafeUrl, UrlPurpose

__all__ = [
    "ThemePicker",
    "ThemePickerProps",
    "ThemePreference",
    "resolve_theme_preference",
    "theme_markers",
    "theme_boot_asset",
]

ColorMode = Literal["system", "light", "dark"]
_THEME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


@dataclass(frozen=True, slots=True)
class ThemePreference:
    """Allowlisted page preference; persistence remains application-owned."""

    theme: str = "default"
    color_mode: ColorMode = "system"

    def __post_init__(self) -> None:
        if not _THEME.fullmatch(self.theme):
            raise ValueError("theme preference must use a safe registered name")
        if self.color_mode not in ("system", "light", "dark"):
            raise ValueError("color_mode must be system, light, or dark")


def resolve_theme_preference(
    theme: str | None,
    color_mode: str | None,
    *,
    allowed_themes: tuple[str, ...] = ("default", "aurora"),
) -> ThemePreference:
    allowed = tuple(dict.fromkeys(allowed_themes))
    if any(not _THEME.fullmatch(name) for name in allowed):
        raise ValueError("allowed theme names must be safe identifiers")
    selected = theme or "default"
    if selected not in allowed:
        selected = "default" if "default" in allowed else allowed[0]
    mode = color_mode or "system"
    if mode not in ("system", "light", "dark"):
        mode = "system"
    return ThemePreference(theme=selected, color_mode=mode)  # type: ignore[arg-type]


def theme_markers(preference: ThemePreference) -> dict[str, str]:
    """Return safe document markers that can be emitted before page content."""
    return {
        "data-hedron-theme": preference.theme,
        "data-hedron-color-mode": preference.color_mode,
        "data-theme": preference.color_mode,
        "style": (
            "color-scheme: light dark;"
            if preference.color_mode == "system"
            else f"color-scheme: {preference.color_mode};"
        ),
    }


def theme_boot_asset(
    allowed_themes: tuple[str, ...],
    *,
    allowed_color_modes: tuple[ColorMode, ...] = ("system", "light", "dark"),
) -> str:
    """Return a bounded CSP-compatible helper for local preference storage.

    The helper only reads an allowlisted local value and updates framework-owned
    attributes. It never accepts CSS, selectors, or remote inputs.
    """
    allowed = tuple(dict.fromkeys(allowed_themes))
    if any(not _THEME.fullmatch(name) for name in allowed):
        raise ValueError("allowed theme names must be safe identifiers")
    if not allowed_color_modes or any(
        mode not in ("system", "light", "dark") for mode in allowed_color_modes
    ):
        raise ValueError("allowed color modes must use system, light, and/or dark")
    encoded = json.dumps(allowed, separators=(",", ":"))
    encoded_modes = json.dumps(tuple(dict.fromkeys(allowed_color_modes)), separators=(",", ":"))
    return (
        "(() => {"
        f"const allowed={encoded};"
        f"const modes={encoded_modes};"
        "const value=localStorage.getItem('hedron-theme');"
        "const mode=localStorage.getItem('hedron-color-mode');"
        "if(value && allowed.includes(value)){document.documentElement.dataset.hedronTheme=value;}"
        "if(mode && modes.includes(mode)){document.documentElement.dataset.hedronColorMode=mode;"
        "document.documentElement.dataset.theme=mode;"
        "document.documentElement.style.colorScheme=mode==='system'?'light dark':mode;}"
        "})();"
    )


class ThemePickerProps(Props):
    id: str | None = None
    class_: str | None = None
    mark: str | None = None


class ThemePicker(Component[Any]):
    """Accessible no-JavaScript theme form with optional HTMX enhancement."""

    logical_name = "ThemePicker"
    props_type = ThemePickerProps

    def __init__(
        self,
        *,
        themes: tuple[str, ...] = ("default", "aurora"),
        color_modes: tuple[ColorMode, ...] = ("system", "light", "dark"),
        selected: ThemePreference | None = None,
        action: SafeUrl | str = "/preferences/theme",
        csrf_token: str | None = None,
        compact: bool = False,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        if not themes or any(not _THEME.fullmatch(name) for name in themes):
            raise ValueError("ThemePicker themes must be non-empty safe names")
        registry = get_registry()
        registered = {item.name for item in registry.themes()}
        unknown = sorted(set(themes) - registered)
        if unknown and registered:
            raise ValueError(f"ThemePicker themes are not registered: {', '.join(unknown)}")
        if not color_modes or any(mode not in ("system", "light", "dark") for mode in color_modes):
            raise ValueError("ThemePicker color_modes must use system, light, and/or dark")
        if isinstance(action, SafeUrl):
            action_url = action
        else:
            action_url = SafeUrl.parse(action, purpose=UrlPurpose.FORM_ACTION)
        preference = selected or resolve_theme_preference(None, None, allowed_themes=themes)
        if preference.theme not in themes:
            preference = resolve_theme_preference(
                None, preference.color_mode, allowed_themes=themes
            )
        super().__init__(
            ThemePickerProps(id=id, class_=class_, mark=mark, **kwargs),
        )
        self._themes = tuple(themes)
        self._color_modes = tuple(color_modes)
        self._selected = preference
        self._action = action_url
        self._csrf_token = csrf_token
        self._compact = compact
        self._id = id
        self._class = class_
        self._mark = mark

    def render(self) -> NodeLike:
        theme_options = [
            html.option(name.title(), value=name, selected=name == self._selected.theme)
            for name in self._themes
        ]
        mode_options = [
            html.option(mode.title(), value=mode, selected=mode == self._selected.color_mode)
            for mode in self._color_modes
        ]
        children: list[NodeLike] = [
            html.label("Theme", html.select(*theme_options, name="theme")),
            html.label("Color mode", html.select(*mode_options, name="color_mode")),
        ]
        if self._csrf_token is not None:
            children.append(html.input(type="hidden", name="csrf_token", value=self._csrf_token))
        children.append(html.button("Apply", type="submit"))
        return html.form(
            *children,
            action=self._action,
            method="post",
            id=self.props.id,
            class_=class_names("hedron-theme-picker", self.props.class_),
            data={
                "hedron-theme-picker": "true",
                "hedron-theme-picker-compact": self._compact,
                **mark_data(self.props.mark),
            },
        )
