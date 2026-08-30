"""Auto renderer and inspection report types."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Literal

from hedron_core.component import NodeLike

RendererMaturity = Literal["supported", "experimental"]


@dataclass(frozen=True, slots=True)
class RendererSpec:
    name: str
    priority: int
    types: tuple[type, ...] = ()
    predicate: Callable[[object], bool] | None = None
    cost: int = 1
    optional_package: str | None = None
    security_notes: str = ""
    explanation: str = ""
    factory: Callable[[object], NodeLike] | None = None
    maturity: RendererMaturity = "supported"


@dataclass(frozen=True, slots=True)
class AutoDecision:
    selected: str
    candidates: tuple[str, ...]
    rejected: tuple[tuple[str, str], ...]
    inspection: Mapping[str, object] = field(default_factory=dict[str, object])


@dataclass(frozen=True, slots=True)
class DataIntelligenceReport:
    row_count: int | None
    columns: tuple[str, ...]
    cardinality: Mapping[str, int]
    datetime_columns: tuple[str, ...]
    geospatial_columns: tuple[str, ...]
    bounded: bool
    notes: tuple[str, ...] = ()
