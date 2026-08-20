"""Shared size, density, appearance, and emphasis vocabulary (phase 0.54 / RFC-0081).

Presentation props are a closed vocabulary so themes can style every built-in
through ``data-hedron-*`` hooks without application CSS.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Literal

from hedron_core.codes import HED_HTML_0006
from hedron_core.diagnostics import error

__all__ = [
    "APPEARANCES",
    "BREAKPOINTS",
    "CONTENT_WIDTHS",
    "DENSITIES",
    "EMPHASES",
    "SIZES",
    "STATE_KINDS",
    "TYPOGRAPHY_ROLES",
    "Appearance",
    "ContentWidth",
    "Density",
    "Emphasis",
    "Size",
    "StateKind",
    "TypographyRole",
    "appearance_data",
    "normalize_responsive_int",
    "require_choice",
    "responsive_data",
]

SIZES: tuple[str, ...] = ("sm", "md", "lg")
DENSITIES: tuple[str, ...] = ("compact", "comfortable", "spacious")
APPEARANCES: tuple[str, ...] = ("solid", "outline", "soft", "ghost")
EMPHASES: tuple[str, ...] = ("primary", "secondary", "danger", "neutral")
TYPOGRAPHY_ROLES: tuple[str, ...] = (
    "display",
    "eyebrow",
    "title",
    "body",
    "label",
    "caption",
    "mono",
)
STATE_KINDS: tuple[str, ...] = (
    "loading",
    "empty",
    "error",
    "permission",
    "offline",
    "success",
)
CONTENT_WIDTHS: tuple[str, ...] = ("narrow", "default", "wide", "full")

# Responsive prop maps use this closed breakpoint ladder; ``base`` is the
# mobile-first default and the remaining names are min-width steps.
BREAKPOINTS: tuple[str, ...] = ("base", "sm", "md", "lg", "xl")

Size = Literal["sm", "md", "lg"]
Density = Literal["compact", "comfortable", "spacious"]
Appearance = Literal["solid", "outline", "soft", "ghost"]
Emphasis = Literal["primary", "secondary", "danger", "neutral"]
TypographyRole = Literal["display", "eyebrow", "title", "body", "label", "caption", "mono"]
StateKind = Literal["loading", "empty", "error", "permission", "offline", "success"]
ContentWidth = Literal["narrow", "default", "wide", "full"]


def require_choice(value: str | None, allowed: Iterable[str], *, label: str) -> str | None:
    """Return ``value`` when it belongs to a closed presentation vocabulary."""
    if value is None:
        return None
    options = tuple(allowed)
    if value not in options:
        raise error(
            HED_HTML_0006,
            title=f"Invalid {label} value",
            explanation=f"{label}={value!r} is not part of the shared appearance vocabulary.",
            remediation=f"Use one of: {', '.join(options)}.",
        )
    return value


def appearance_data(
    *,
    size: str | None = None,
    density: str | None = None,
    appearance: str | None = None,
    emphasis: str | None = None,
) -> dict[str, str | bool | int | float | None]:
    """Return ``data-hedron-*`` markers for the shared presentation vocabulary."""
    data: dict[str, str | bool | int | float | None] = {}
    for key, value, allowed in (
        ("hedron-size", size, SIZES),
        ("hedron-density", density, DENSITIES),
        ("hedron-appearance", appearance, APPEARANCES),
        ("hedron-emphasis", emphasis, EMPHASES),
    ):
        checked = require_choice(value, allowed, label=key.removeprefix("hedron-"))
        if checked is not None:
            data[key] = checked
    return data


def normalize_responsive_int(
    value: int | Mapping[str, int],
    *,
    label: str,
    minimum: int = 1,
    maximum: int = 6,
) -> dict[str, int]:
    """Normalize an int or breakpoint map into a ``{breakpoint: int}`` dict.

    A bare int becomes ``{"base": value}``. Mapping keys must come from
    :data:`BREAKPOINTS` so themes can compile a bounded set of media queries.
    """
    raw: Mapping[str, int] = {"base": value} if isinstance(value, int) else value
    if not raw:
        raise error(
            HED_HTML_0006,
            title=f"Empty responsive {label} map",
            explanation=f"{label} must declare at least one breakpoint.",
            remediation="Pass an int or a map such as {'base': 1, 'md': 2}.",
        )
    normalized: dict[str, int] = {}
    for breakpoint_name, count in raw.items():
        if breakpoint_name not in BREAKPOINTS:
            raise error(
                HED_HTML_0006,
                title=f"Unknown {label} breakpoint",
                explanation=f"Breakpoint {breakpoint_name!r} is not supported.",
                remediation=f"Use one of: {', '.join(BREAKPOINTS)}.",
            )
        if not isinstance(count, int) or isinstance(count, bool):
            raise error(
                HED_HTML_0006,
                title=f"Invalid {label} value",
                explanation=f"{label}[{breakpoint_name!r}] must be an integer.",
                remediation="Pass integer column counts.",
            )
        if count < minimum or count > maximum:
            raise error(
                HED_HTML_0006,
                title=f"Invalid {label} value",
                explanation=(
                    f"{label}[{breakpoint_name!r}]={count} is outside "
                    f"the supported range {minimum}-{maximum}."
                ),
                remediation=f"Use a value between {minimum} and {maximum}.",
            )
        normalized[breakpoint_name] = count
    if "base" not in normalized:
        normalized["base"] = normalized[min(normalized, key=BREAKPOINTS.index)]
    return {name: normalized[name] for name in BREAKPOINTS if name in normalized}


def responsive_data(
    columns: Mapping[str, int], *, prefix: str
) -> dict[str, str | bool | int | float | None]:
    """Return ``data-<prefix>`` / ``data-<prefix>-<breakpoint>`` markers."""
    data: dict[str, str | bool | int | float | None] = {}
    for breakpoint_name, count in columns.items():
        key = prefix if breakpoint_name == "base" else f"{prefix}-{breakpoint_name}"
        data[key] = str(count)
    return data
