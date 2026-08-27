"""The Edron 0.9 deprecated-feature exclusion policy."""

from __future__ import annotations

from collections.abc import Iterable

DEPRECATED_HEDRON_067_PATHS = frozenset(
    {
        "hedron-disclose",
        "hedron-elements duplicate common-widget wrappers",
        "hedron-dialog",
        "hedron-field-text",
        "hedron-field-choice",
        "hedron-field-file",
        "hedron-action-async",
        "delegated common-widget controllers",
    }
)


def deprecated_hedron_paths(text: str, *, paths: Iterable[str] = ()) -> tuple[str, ...]:
    """Return deprecated Hedron compatibility markers present in *text*."""
    markers = tuple(paths) or tuple(DEPRECATED_HEDRON_067_PATHS)
    return tuple(sorted(marker for marker in markers if marker and marker in text))


__all__ = ["DEPRECATED_HEDRON_067_PATHS", "deprecated_hedron_paths"]
