"""Explicit theme / color-mode / density scope boundary (phase 0.58)."""

from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import Field

from hedron_core.builtins._base import ElementProps, class_names, collect_children, mark_data
from hedron_core.builtins.appearance import DENSITIES, Density, require_choice
from hedron_core.codes import HED_STYLE_SCOPE_0001, HED_STYLE_SCOPE_0002
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.theme_platform import StyleContext

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
PRESENTATION_SLOTS: tuple[str, ...] = (
    "PageHeader.title",
    "PageHeader.description",
    "Heading",
    "Text",
    "Card.heading",
    "Card.supporting-copy",
    "Card.metadata",
    "FormField.control",
    "ProcessFlow.step",
)
_PRESENTATION_SLOT_SET = frozenset(PRESENTATION_SLOTS)


class StyleScopeProps(ElementProps):
    scope: str | None = None
    theme: str | None = None
    color_mode: _ColorMode | None = None
    density: Density | None = None
    variant: str | None = None
    design: str | None = None
    recipe_defaults: dict[str, str] = Field(default_factory=dict)
    presentation: dict[str, str] = Field(default_factory=dict)


class StyleScope(Component[StyleScopeProps]):
    """Visible theme boundary with explicit, presentation-only recipe defaults."""

    props_type = StyleScopeProps
    logical_name = "StyleScope"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        scope: str | None = None,
        theme: str | None = None,
        color_mode: _ColorMode | None = None,
        density: Density | None = None,
        variant: str | None = None,
        design: str | None = None,
        recipe_defaults: dict[str, str] | None = None,
        presentation: dict[str, str] | None = None,
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
                    f"({', '.join(rejected)}). Pass recipe_defaults explicitly in 0.60."
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
        if scope is not None:
            if not isinstance(scope, str) or _THEME_NAME_RE.fullmatch(scope.strip()) is None:
                raise error(
                    HED_STYLE_SCOPE_0001,
                    title="Invalid application style scope",
                    explanation=f"scope={scope!r} must match [A-Za-z0-9_-]+.",
                    remediation="Use the same scope name passed to app.styles(scope=...).",
                )
            scope = scope.strip()
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
        if design is not None and _THEME_NAME_RE.fullmatch(design.strip()) is None:
            raise error(
                HED_STYLE_SCOPE_0001,
                title="Invalid StyleScope design",
                explanation=f"design={design!r} must be a safe registered design name.",
                remediation="Use a registered DesignSystem name.",
            )
        defaults = dict(recipe_defaults or {})
        if any(
            _THEME_NAME_RE.fullmatch(str(key)) is None
            or _THEME_NAME_RE.fullmatch(str(value)) is None
            for key, value in defaults.items()
        ):
            raise error(
                HED_STYLE_SCOPE_0001,
                title="Invalid StyleScope recipe defaults",
                explanation="Recipe family and recipe names must be safe registered identifiers.",
                remediation="Use recipe_defaults={'surface': 'panel'} with registered recipes.",
            )
        presentation_values = dict(presentation or {})
        if any(key not in _PRESENTATION_SLOT_SET for key in presentation_values):
            invalid = sorted(set(presentation_values) - _PRESENTATION_SLOT_SET)
            raise error(
                HED_STYLE_SCOPE_0001,
                title="Invalid StyleScope presentation slot",
                explanation=f"Unsupported presentation slot(s): {', '.join(invalid)}.",
                remediation=f"Use one of: {', '.join(PRESENTATION_SLOTS)}.",
            )
        if any(
            _THEME_NAME_RE.fullmatch(str(value)) is None
            for value in presentation_values.values()
        ):
            raise error(
                HED_STYLE_SCOPE_0001,
                title="Invalid StyleScope presentation mapping",
                explanation="Presentation recipe names must be safe registered identifiers.",
                remediation="Use presentation={'PageHeader.title': 'auth-display'}.",
            )
        super().__init__(
            StyleScopeProps(
                scope=scope,
                theme=theme,
                color_mode=color_mode,
                density=density,
                variant=variant,
                design=design,
                recipe_defaults=defaults,
                presentation=presentation_values,
                id=id,
                class_=class_,
                mark=mark,
            )
        )
        self._children = collect_children(*nodes, children=children)
        self._style_context = StyleContext(recipes=defaults, presentation=presentation_values)

    @property
    def style_context(self) -> StyleContext:
        return self._style_context

    def render(self) -> NodeLike:
        data: dict[str, str | bool | int | float | None] = {
            "hedron-style-scope": "true",
        }
        if self.props.scope is not None:
            data["hedron-style-scope"] = self.props.scope
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
        if self.props.design is not None:
            data["hedron-design"] = self.props.design
        if self.props.recipe_defaults:
            data["hedron-recipe-context"] = ";".join(
                f"{key}={value}" for key, value in sorted(self.props.recipe_defaults.items())
            )
        if self.props.presentation:
            data["hedron-presentation"] = ";".join(
                f"{key}={value}" for key, value in sorted(self.props.presentation.items())
            )
        data.update(mark_data(self.props.mark))
        return html.div(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-style-scope", self.props.class_),
            data=data,
        )
