"""ColorMode preference API and accessible toggle component."""

from __future__ import annotations

from typing import Any, Literal

from hedron_core.compat import StrEnum
from hedron_core.component import Component
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.typing_aliases import HtmlAttrMap

__all__ = [
    "ColorMode",
    "ColorModePreference",
    "ColorModeToggle",
    "color_mode_script",
    "resolve_color_mode",
]


class ColorMode(StrEnum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


ColorModePreference = Literal["light", "dark", "system"]


def resolve_color_mode(
    preference: ColorMode | str | None,
    *,
    system_dark: bool = False,
) -> Literal["light", "dark"]:
    """Resolve stored preference against system preference."""
    pref = ColorMode(preference) if preference else ColorMode.SYSTEM
    if pref is ColorMode.SYSTEM:
        return "dark" if system_dark else "light"
    return "dark" if pref is ColorMode.DARK else "light"


class ColorModeToggleProps(Props):
    preference: str = "system"
    label: str = "Color mode"
    id: str | None = None


class ColorModeToggle(Component[ColorModeToggleProps]):
    """Accessible light/dark/system preference control."""

    props_type = ColorModeToggleProps
    logical_name = "ColorModeToggle"

    def __init__(
        self,
        *,
        preference: ColorMode | str = ColorMode.SYSTEM,
        label: str = "Color mode",
        id: str | None = None,
        action: str | None = None,
        csrf_token: str | None = None,
        **kwargs: object,
    ) -> None:
        pref = preference.value if isinstance(preference, ColorMode) else str(preference)
        super().__init__(ColorModeToggleProps(preference=pref, label=label, id=id, **kwargs))
        self._action = action
        self._csrf_token = csrf_token

    def render(self) -> Any:
        control_id = self.props.id or f"hedron-color-mode-{self.render_instance_id()[2:10]}"
        options = []
        for mode in (ColorMode.LIGHT, ColorMode.DARK, ColorMode.SYSTEM):
            opts: HtmlAttrMap = {"value": mode.value}
            if self.props.preference == mode.value:
                opts["selected"] = True
            options.append(html.option(mode.value.title(), **opts))
        select_attrs: HtmlAttrMap = {
            "name": "color_mode",
            "aria": {"label": self.props.label},
            "data": {"hedron-color-mode": "true"},
        }
        form_attrs: HtmlAttrMap = {"method": "post", "class_": "hedron-color-mode"}
        if self._action:
            from hedron_core.security import SafeUrl, UrlPurpose

            form_attrs["action"] = (
                self._action
                if isinstance(self._action, SafeUrl)
                else SafeUrl.parse(str(self._action), purpose=UrlPurpose.FORM_ACTION)
            )
        fields: list[Any] = [
            html.label(self.props.label, for_=control_id),
            html.select(*options, id=control_id, **select_attrs),
        ]
        if self._csrf_token:
            fields.append(html.input(type="hidden", name="csrf_token", value=self._csrf_token))
        fields.append(html.button("Apply", type="submit"))
        return html.form(*fields, **form_attrs)


def color_mode_script() -> str:
    """Small CSP-externalizable helper to apply data-theme from preference cookie."""
    return (
        "(function(){try{var m=document.cookie.match(/(?:^|; )hedron_color_mode=([^;]+)/);"
        "var p=m?decodeURIComponent(m[1]):'system';"
        "var dark=window.matchMedia('(prefers-color-scheme: dark)').matches;"
        "var resolved=p==='system'?(dark?'dark':'light'):p;"
        "document.documentElement.setAttribute('data-theme', resolved);"
        "}catch(e){}})();"
    )
