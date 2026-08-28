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
    "register_first_party_icons",
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

_FIRST_PARTY_PATHS: dict[str, str] = {
    "home": "M3 10.5 12 3l9 7.5V21H3zM9 21v-6h6v6",
    "menu": "M3 6h18M3 12h18M3 18h18",
    "chevron-right": "m9 18 6-6-6-6",
    "chevron-left": "m15 18-6-6 6-6",
    "close": "m6 6 12 12M18 6 6 18",
    "user": "M20 21a8 8 0 0 0-16 0M12 13a4 4 0 1 0 0-8 4 4 0 0 0 0 8",
    "team": "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8m7-7a4 4 0 0 1 0 7",
    "database": "M4 5c0 2 16 2 16 0M4 5v14c0 2 16 2 16 0V5M4 12c0 2 16 2 16 0",
    "link": "M10 13a5 5 0 0 0 7.5.5l2-2a5 5 0 0 0-7-7l-1 1M14 11a5 5 0 0 0-7.5-.5l-2 2a5 5 0 0 0 7 7l1-1",
    "key": "m15 7 6 6m-3-3-3 3m-6-6a4 4 0 1 0-5.7-5.7A4 4 0 0 0 9 7z",
    "pulse": "M3 12h4l2-7 4 14 2-7h6",
    "audit": "M5 4h14v16H5zM8 8h8M8 12h8M8 16h5",
    "search": "m21 21-4.3-4.3M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15",
    "settings": "M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.8 1.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5v.1h-2.6v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1-1.8-1.8.1-.1A1.7 1.7 0 0 0 8 15a1.7 1.7 0 0 0-1.5-1H6v-2.6h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1L9 6.6l.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.5v-.1h2.6v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.8 1.8-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.5 1h.1V14h-.1a1.7 1.7 0 0 0-1.1 1z",
    "signout": "M10 17l5-5-5-5M15 12H3m9-7h8v14h-8",
    "check": "m5 12 4 4L19 6",
    "warning": "m12 3 9 18H3zM12 9v4m0 4h.01",
    "error": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18m0 5v5m0 4h.01",
    "eye": "M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6m10 3a3 3 0 1 0 0-6 3 3 0 0 0 0 6",
    "eye-off": "m3 3 18 18M10.6 6.2A10.7 10.7 0 0 1 12 6c6.5 0 10 6 10 6a18 18 0 0 1-4 4.7M6.2 6.2C3.5 8.2 2 12 2 12s3.5 6 10 6a10.7 10.7 0 0 0 1.4-.1",
}


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


def register_first_party_icons(*, source: str = "hedron-core-icons") -> tuple[IconEntry, ...]:
    """Install Hedron's small optional semantic icon pack into the trusted registry."""
    entries: list[IconEntry] = []
    for name, path in _FIRST_PARTY_PATHS.items():
        entries.append(
            register_icon(
                name,
                f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{path}"/></svg>',
                title=name.replace("-", " ").title(),
                source=source,
            )
        )
    return tuple(entries)


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
