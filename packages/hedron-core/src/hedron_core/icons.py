"""Trusted icon and SVG registry with explicit active-content policy."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

from hedron_core.active_markup import active_markup_reason
from hedron_core.diagnostics import error
from hedron_core.security import TrustedHtml

__all__ = [
    "IconEntry",
    "clear_icons_for_tests",
    "get_icon",
    "list_icons",
    "register_icon",
    "trusted_svg",
]


@dataclass(frozen=True, slots=True)
class IconEntry:
    name: str
    svg: TrustedHtml
    title: str
    source: str


_LOCK = RLock()
_ICONS: dict[str, IconEntry] = {}


def register_icon(
    name: str,
    svg: str | TrustedHtml,
    *,
    title: str,
    source: str = "application",
) -> IconEntry:
    if not name or not name.replace("-", "").replace("_", "").isalnum():
        raise error(
            "HED-ICON-0001",
            title="Invalid icon name",
            explanation=f"Icon name {name!r} must be alphanumeric with hyphens/underscores.",
            remediation="Use a stable logical icon name such as 'check' or 'chevron-right'.",
        )
    if not title.strip():
        raise error(
            "HED-ICON-0002",
            title="Icon title required",
            explanation="Trusted icons require an accessible title.",
            remediation="Pass title= with a human-readable label.",
        )
    trusted = svg if isinstance(svg, TrustedHtml) else TrustedHtml.reviewed(svg, source=source)
    reason = active_markup_reason(trusted.value)
    if reason is not None:
        raise error(
            "HED-ICON-0003",
            title="Active script content rejected",
            explanation=f"Icon SVG rejected ({reason}).",
            remediation="Sanitize SVG before registration or use TrustedHtml.nh3(...).",
        )
    entry = IconEntry(name=name, svg=trusted, title=title, source=source)
    with _LOCK:
        _ICONS[name] = entry
    return entry


def get_icon(name: str) -> IconEntry:
    with _LOCK:
        try:
            return _ICONS[name]
        except KeyError as exc:
            raise error(
                "HED-ICON-0004",
                title="Unknown icon",
                explanation=f"Icon {name!r} is not registered.",
                remediation="Call register_icon(...) before rendering, or list_icons().",
            ) from exc


def list_icons() -> tuple[IconEntry, ...]:
    with _LOCK:
        return tuple(_ICONS[name] for name in sorted(_ICONS))


def trusted_svg(svg: str, *, source: str) -> TrustedHtml:
    """Register-ready SVG trust boundary (does not auto-sanitize)."""
    return TrustedHtml.reviewed(svg, source=source)


def clear_icons_for_tests() -> None:
    with _LOCK:
        _ICONS.clear()
