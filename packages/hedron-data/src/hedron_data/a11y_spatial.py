"""Keyboard and single-pointer alternatives for spatial grid/chart operations."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["SpatialAlternative", "spatial_alternatives_for"]


@dataclass(frozen=True, slots=True)
class SpatialAlternative:
    operation: str
    keyboard: str
    single_pointer: str
    traps_browse_mode: bool = False


_DEFAULTS: dict[str, SpatialAlternative] = {
    "drag": SpatialAlternative(
        operation="drag",
        keyboard="Arrow keys move the focused item; Enter confirms drop",
        single_pointer="Long-press then tap destination",
    ),
    "fill": SpatialAlternative(
        operation="fill",
        keyboard="Ctrl+D fills selection from active cell",
        single_pointer="Fill handle menu → Fill Down",
    ),
    "resize": SpatialAlternative(
        operation="resize",
        keyboard="Alt+Arrow adjusts column/row size",
        single_pointer="Resize dialog with numeric input",
    ),
    "reorder": SpatialAlternative(
        operation="reorder",
        keyboard="Ctrl+Arrow reorders focused column/row",
        single_pointer="Move Up/Down commands in column menu",
    ),
    "chart-select": SpatialAlternative(
        operation="chart-select",
        keyboard="Tab through points; Space toggles selection",
        single_pointer="Tap point; synchronized table row selects equivalent",
    ),
}


def spatial_alternatives_for(*operations: str) -> tuple[SpatialAlternative, ...]:
    out: list[SpatialAlternative] = []
    for op in operations:
        alt = _DEFAULTS.get(op)
        if alt is None:
            raise KeyError(f"Unknown spatial operation {op!r}")
        if alt.traps_browse_mode:
            raise ValueError(f"{op} must not trap browse/focus modes")
        out.append(alt)
    return tuple(out)
