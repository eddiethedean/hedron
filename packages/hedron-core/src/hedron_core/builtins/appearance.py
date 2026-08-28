"""Shared size, density, appearance, and emphasis vocabulary (phases 0.54 / 0.57).

Presentation props are a closed vocabulary so themes can style every built-in
through ``data-hedron-*`` hooks without application CSS. Phase 0.57 extends the
authority with ``plain``/``raised``, width, overflow, track, and responsive
table policies (RFC-0084 / D-099 / D-100).
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
    "ELEVATIONS",
    "EMPHASES",
    "GAP_TOKENS",
    "OVERFLOW_MODES",
    "PADDINGS",
    "RESPONSIVE_POLICIES",
    "SHAPES",
    "SIZES",
    "STATE_KINDS",
    "TRACKS",
    "TRACKING",
    "TYPOGRAPHY_ROLES",
    "TYPE_EFFECTS",
    "TYPE_MEASURES",
    "WIDTHS",
    "Appearance",
    "ContentWidth",
    "Density",
    "Elevation",
    "Emphasis",
    "GapToken",
    "OverflowMode",
    "Padding",
    "ResponsivePolicy",
    "Shape",
    "Size",
    "StateKind",
    "Track",
    "TypographyRole",
    "TypographyEffect",
    "TypographyMeasure",
    "Width",
    "appearance_data",
    "gap_data",
    "normalize_gap",
    "normalize_responsive_int",
    "normalize_responsive_track",
    "require_choice",
    "responsive_data",
]

SIZES: tuple[str, ...] = ("sm", "md", "lg")
DENSITIES: tuple[str, ...] = ("compact", "comfortable", "spacious")
APPEARANCES: tuple[str, ...] = ("solid", "outline", "soft", "ghost", "plain", "raised")
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
TYPE_MEASURES: tuple[str, ...] = ("narrow", "default", "wide")
TYPE_EFFECTS: tuple[str, ...] = ("none", "subtle", "display")
STATE_KINDS: tuple[str, ...] = (
    "loading",
    "empty",
    "error",
    "permission",
    "offline",
    "success",
)
CONTENT_WIDTHS: tuple[str, ...] = ("narrow", "default", "wide", "full")
WIDTHS: tuple[str, ...] = ("content", "field", "full")
OVERFLOW_MODES: tuple[str, ...] = ("wrap", "break", "truncate", "clip")
TRACKS: tuple[str, ...] = ("narrow", "default", "wide", "fluid")
TRACKING: tuple[str, ...] = ("tight", "normal", "loose")
RESPONSIVE_POLICIES: tuple[str, ...] = ("scroll", "stack", "priority")
PADDINGS: tuple[str, ...] = ("none", "sm", "md", "lg")
ELEVATIONS: tuple[str, ...] = ("none", "sm", "md", "lg")
SHAPES: tuple[str, ...] = ("square", "rounded", "pill")

# Named gap tokens preferred under strict CSP. Length literals remain accepted
# only when they equal the token CSS size exactly (no silent remapping).
GAP_TOKENS: tuple[str, ...] = ("none", "xs", "sm", "md", "lg", "xl")
_GAP_TOKEN_LENGTHS: dict[str, str] = {
    "0": "none",
    "0rem": "none",
    "0px": "none",
    "0.25rem": "xs",
    "4px": "xs",
    "0.5rem": "sm",
    "8px": "sm",
    "1rem": "md",
    "16px": "md",
    "1.5rem": "lg",
    "24px": "lg",
    "2rem": "xl",
    "32px": "xl",
}

# Responsive prop maps use this closed breakpoint ladder; ``base`` is the
# mobile-first default and the remaining names are min-width steps.
BREAKPOINTS: tuple[str, ...] = ("base", "sm", "md", "lg", "xl")

Size = Literal["sm", "md", "lg"]
Density = Literal["compact", "comfortable", "spacious"]
Appearance = Literal["solid", "outline", "soft", "ghost", "plain", "raised"]
Emphasis = Literal["primary", "secondary", "danger", "neutral"]
TypographyRole = Literal["display", "eyebrow", "title", "body", "label", "caption", "mono"]
TypographyMeasure = Literal["narrow", "default", "wide"]
TypographyEffect = Literal["none", "subtle", "display"]
StateKind = Literal["loading", "empty", "error", "permission", "offline", "success"]
ContentWidth = Literal["narrow", "default", "wide", "full"]
Width = Literal["content", "field", "full"]
OverflowMode = Literal["wrap", "break", "truncate", "clip"]
Track = Literal["narrow", "default", "wide", "fluid"]
ResponsivePolicy = Literal["scroll", "stack", "priority"]
Padding = Literal["none", "sm", "md", "lg"]
Elevation = Literal["none", "sm", "md", "lg"]
Shape = Literal["square", "rounded", "pill"]
GapToken = Literal["none", "xs", "sm", "md", "lg", "xl"]


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
    width: str | None = None,
    overflow: str | None = None,
    track: str | None = None,
    padding: str | None = None,
    elevation: str | None = None,
    shape: str | None = None,
    tone: str | None = None,
) -> dict[str, str | bool | int | float | None]:
    """Return ``data-hedron-*`` markers for the shared presentation vocabulary."""
    data: dict[str, str | bool | int | float | None] = {}
    for key, value, allowed in (
        ("hedron-size", size, SIZES),
        ("hedron-density", density, DENSITIES),
        ("hedron-appearance", appearance, APPEARANCES),
        ("hedron-emphasis", emphasis, EMPHASES),
        ("hedron-width", width, WIDTHS),
        ("hedron-overflow", overflow, OVERFLOW_MODES),
        ("hedron-track", track, TRACKS),
        ("hedron-padding", padding, PADDINGS),
        ("hedron-elevation", elevation, ELEVATIONS),
        ("hedron-shape", shape, SHAPES),
    ):
        checked = require_choice(value, allowed, label=key.removeprefix("hedron-"))
        if checked is not None:
            data[key] = checked
    if tone is not None:
        data["hedron-tone"] = tone
    return data


def normalize_gap(gap: str) -> tuple[str, str | None]:
    """Return ``(token_or_compat, length_or_none)`` for a layout gap value.

    Named tokens (``sm``, ``md``, …) are preferred and never require inline
    styles. Known length literals map to the nearest token for CSP-safe CSS.
    Unknown lengths raise a shared diagnostic rather than silently falling back.
    """
    if gap in GAP_TOKENS:
        return gap, None
    mapped = _GAP_TOKEN_LENGTHS.get(gap)
    if mapped is not None:
        return mapped, gap
    raise error(
        HED_HTML_0006,
        title="Unsupported layout gap",
        explanation=(
            f"Gap {gap!r} is not a supported presentation token. "
            "Strict CSP layouts require named gap tokens that match first-party CSS sizes."
        ),
        remediation=(
            f"Use one of: {', '.join(GAP_TOKENS)}. "
            "Exact length aliases: 0.25rem/4px→xs, 0.5rem/8px→sm, 1rem/16px→md, "
            "1.5rem/24px→lg, 2rem/32px→xl."
        ),
    )


def gap_data(gap: str) -> dict[str, str | bool | int | float | None]:
    """Return ``data-hedron-gap`` markers for a normalized gap value."""
    token, _compat = normalize_gap(gap)
    return {"hedron-gap": token}


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


def normalize_responsive_track(
    value: str | Mapping[str, str],
    *,
    label: str = "track",
) -> dict[str, str]:
    """Normalize a track token or breakpoint map of track tokens."""
    raw: Mapping[str, str] = {"base": value} if isinstance(value, str) else value
    if not raw:
        raise error(
            HED_HTML_0006,
            title=f"Empty responsive {label} map",
            explanation=f"{label} must declare at least one breakpoint.",
            remediation="Pass a track token or a map such as {'base': 'default', 'md': 'wide'}.",
        )
    normalized: dict[str, str] = {}
    for breakpoint_name, track in raw.items():
        if breakpoint_name not in BREAKPOINTS:
            raise error(
                HED_HTML_0006,
                title=f"Unknown {label} breakpoint",
                explanation=f"Breakpoint {breakpoint_name!r} is not supported.",
                remediation=f"Use one of: {', '.join(BREAKPOINTS)}.",
            )
        checked = require_choice(track, TRACKS, label=label)
        assert checked is not None
        normalized[breakpoint_name] = checked
    if "base" not in normalized:
        normalized["base"] = normalized[min(normalized, key=BREAKPOINTS.index)]
    return {name: normalized[name] for name in BREAKPOINTS if name in normalized}


def responsive_data(
    columns: Mapping[str, int | str], *, prefix: str
) -> dict[str, str | bool | int | float | None]:
    """Return ``data-<prefix>`` / ``data-<prefix>-<breakpoint>`` markers."""
    data: dict[str, str | bool | int | float | None] = {}
    for breakpoint_name, count in columns.items():
        key = prefix if breakpoint_name == "base" else f"{prefix}-{breakpoint_name}"
        data[key] = str(count)
    return data
