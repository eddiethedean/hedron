"""ReactMigrationMatrix and disposition catalog (MIGRATE-040)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Disposition = Literal["native", "hedron", "element", "react-island", "not-a-fit"]

DISPOSITIONS: tuple[Disposition, ...] = (
    "native",
    "hedron",
    "element",
    "react-island",
    "not-a-fit",
)

NON_FITS: tuple[str, ...] = (
    "Offline-first / client-authoritative auth flows",
    "Games / continuous canvas / WebGL loops",
    "Arbitrary npm dependency graphs without a pinned supply inventory",
    "High-frequency multiplayer collaboration UIs",
)

__all__ = [
    "DISPOSITIONS",
    "NON_FITS",
    "Disposition",
    "ReactMigrationMatrix",
    "matrix_rows",
]


@dataclass(frozen=True, slots=True)
class ReactMigrationMatrix:
    """Coverage ledger for React → Hedron migration dispositions."""

    surface: str
    disposition: Disposition
    notes: str = ""


def matrix_rows() -> tuple[ReactMigrationMatrix, ...]:
    return (
        ReactMigrationMatrix("forms", "hedron", "Map to Form / field components"),
        ReactMigrationMatrix("lists", "hedron", "Map to Table / DataTable"),
        ReactMigrationMatrix("custom-widget", "element", "Author via public element kit"),
        ReactMigrationMatrix(
            "legacy-chart-island", "react-island", "Experimental docs/reference only"
        ),
        ReactMigrationMatrix("webgl-game", "not-a-fit", NON_FITS[1]),
        ReactMigrationMatrix("buttons", "native", "Use platform HTML / HTMX primitives"),
    )
