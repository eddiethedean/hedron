"""Explicit theme / color-mode / density scope boundary (phase 0.58)."""

from __future__ import annotations

import re
from typing import Any, Literal

from hedron_core.builtins._base import ElementProps, class_names, collect_children, mark_data
from hedron_core.builtins.appearance import DENSITIES, Density, require_choice
from hedron_core.codes import HED_STYLE_SCOPE_0001, HED_STYLE_SCOPE_0002
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html

_ColorMode = Literal["light", "dark"]
_THEME_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_RECIPE_DEFAULT_KEYS = frozenset(
    {
        "recipe",
        "recipes",
        "recipe_defaults",
        "defaults",
        "style_recipe",
        "style_recipes",
    }
)


class StyleScopeProps(ElementProps):
    theme: str | None = None
    color_mode: _ColorMode | None = None
    density: Density | None = None
    variant: str | None = None


class StyleScope(Component[StyleScopeProps]):
    """Visible subtree boundary for theme, color mode, and density only.

    V1 intentionally rejects scope-wide recipe defaults to avoid hidden
    descendant mutation and specificity authority.
    """

    props_type = StyleScopeProps
    logical_name = "StyleScope"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        theme: str | None = None,
        color_mode: _ColorMode | None = None,
        density: Density | None = None,
        variant: str | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        rejected = sorted(key for key in kwargs if key in _RECIPE_DEFAULT_KEYS)
        if rejected:
            raise error(
                HED_STYLE_SCOPE_0002,
                title="StyleScope recipe defaults unsupported",
                explanation=(
                    "StyleScope rejects recipe defaults "
                    f"({', '.join(rejected)}). Only theme, color_mode, and density "
                    "are supported in 0.58."
                ),
                remediation="Apply recipes with DesignSystem.apply on components instead.",
            )
        if kwargs:
            # Surface other unknown kwargs with the scope diagnostic rather than
            # a generic props validation message.
            unknown = ", ".join(sorted(kwargs))
            raise error(
                HED_STYLE_SCOPE_0001,
                title="Invalid StyleScope value",
                explanation=f"Unsupported StyleScope keyword(s): {unknown}.",
                remediation="Pass only theme, color_mode, density, variant, id, class_, and mark.",
            )
        if theme is not None:
            if not isinstance(theme, str) or not theme.strip():
                raise error(
                    HED_STYLE_SCOPE_0001,
                    title="Invalid StyleScope theme",
                    explanation=f"theme={theme!r} must be a non-empty theme name.",
                    remediation="Pass a registered theme name such as 'default' or 'aurora'.",
                )
            theme = theme.strip()
            if _THEME_NAME_RE.fullmatch(theme) is None:
                raise error(
                    HED_STYLE_SCOPE_0001,
                    title="Invalid StyleScope theme",
                    explanation=f"theme={theme!r} must match [A-Za-z0-9_-]+.",
                    remediation="Pass a registered theme name such as 'default' or 'aurora'.",
                )
        if color_mode is not None and color_mode not in ("light", "dark"):
            raise error(
                HED_STYLE_SCOPE_0001,
                title="Invalid StyleScope color_mode",
                explanation=f"color_mode={color_mode!r} must be 'light' or 'dark'.",
                remediation="Pass color_mode='light' or color_mode='dark'.",
            )
        if density is not None:
            require_choice(density, DENSITIES, label="density")
        if variant is not None:
            if not isinstance(variant, str) or not variant.strip():
                raise error(
                    HED_STYLE_SCOPE_0001,
                    title="Invalid StyleScope variant",
                    explanation=f"variant={variant!r} must be a non-empty variant name.",
                    remediation="Pass a registered finite theme variant name.",
                )
            variant = variant.strip()
            if _THEME_NAME_RE.fullmatch(variant) is None:
                raise error(
                    HED_STYLE_SCOPE_0001,
                    title="Invalid StyleScope variant",
                    explanation=f"variant={variant!r} must match [A-Za-z0-9_-]+.",
                    remediation="Pass a registered finite theme variant name.",
                )
        super().__init__(
            StyleScopeProps(
                theme=theme,
                color_mode=color_mode,
                density=density,
                variant=variant,
                id=id,
                class_=class_,
                mark=mark,
            )
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        data: dict[str, str | bool | int | float | None] = {
            "hedron-style-scope": "true",
        }
        if self.props.theme is not None:
            data["hedron-theme"] = self.props.theme
        if self.props.color_mode is not None:
            data["hedron-color-mode"] = self.props.color_mode
            # Align with page-level data-theme contract used by emit_theme_css.
            data["theme"] = self.props.color_mode
        if self.props.density is not None:
            data["hedron-density"] = self.props.density
        if self.props.variant is not None:
            data["hedron-variant"] = self.props.variant
        data.update(mark_data(self.props.mark))
        return html.div(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-style-scope", self.props.class_),
            data=data,
        )
