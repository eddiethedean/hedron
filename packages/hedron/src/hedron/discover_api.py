"""Versioned public-API stability discovery (DISCOVER-053).

Curated inventory over ``hedron.__all__`` with optional stability tags.
Existing import names are never renamed.
"""

from __future__ import annotations

from typing import Literal

STABILITY_INVENTORY_VERSION = "1.0.0"

Stability = Literal["supported", "stable", "experimental"]

# Small explicit overrides for known facade / experimental names.
# Names present in ``hedron.__all__`` but absent here default to ``supported``.
_STABILITY_OVERRIDES: dict[str, Stability] = {
    "Hedron": "stable",
    "HedronRouter": "stable",
    "HedronRoute": "stable",
    "Page": "stable",
    "Text": "stable",
    "html": "stable",
    "FragmentRegion": "stable",
    "Component": "stable",
    "Form": "stable",
    "FormField": "stable",
    "FormErrors": "stable",
    "CsrfField": "stable",
    "Hx": "stable",
    "Label": "stable",
    "Stack": "stable",
    "TextInput": "stable",
    "TextArea": "stable",
    "SubmitButton": "stable",
    "RefreshButton": "stable",
    "Poll": "stable",
    "swap": "stable",
    "swap_oob": "stable",
    "retarget": "stable",
    "redirect_htmx": "stable",
    "SecurityPolicy": "stable",
    "SecurityHeadersPolicy": "stable",
    "DoubleSubmitCookieCsrf": "stable",
    "SessionTokenCsrf": "stable",
    "CsrfStrategy": "stable",
}


def _public_names() -> list[str]:
    import hedron

    return sorted(str(name) for name in hedron.__all__)


def _stability_for(name: str) -> Stability:
    return _STABILITY_OVERRIDES.get(name, "supported")


def discover_public_api(*, format: str = "json") -> dict[str, object] | str:
    """Return the versioned stability inventory for the curated public API.

    Args:
        format: ``\"json\"`` returns a dict with ``version`` and ``items``;
            ``\"human\"`` returns multiline text. Existing names are preserved.
    """
    items = [{"name": name, "stability": _stability_for(name)} for name in _public_names()]
    if format == "human":
        lines = [f"stability inventory {STABILITY_INVENTORY_VERSION}"]
        lines.extend(f"{row['name']}\t{row['stability']}" for row in items)
        return "\n".join(lines) + "\n"
    if format != "json":
        raise ValueError(f"unsupported format {format!r}; expected 'json' or 'human'")
    return {
        "version": STABILITY_INVENTORY_VERSION,
        "items": items,
    }


__all__ = [
    "STABILITY_INVENTORY_VERSION",
    "discover_public_api",
]
