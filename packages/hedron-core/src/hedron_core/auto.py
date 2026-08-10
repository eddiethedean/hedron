"""Intelligent Auto() renderer registry and bounded Data Intelligence."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, cast

from hedron_core.builtins.content import DescriptionList, Text
from hedron_core.builtins.content import List as HedronList
from hedron_core.builtins.utilities import JSONViewer
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.models import Props

__all__ = [
    "Auto",
    "AutoDecision",
    "DataIntelligenceReport",
    "RendererSpec",
    "clear_renderers_for_tests",
    "inspect_data",
    "register_renderer",
]


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


@dataclass(frozen=True, slots=True)
class AutoDecision:
    selected: str
    candidates: tuple[str, ...]
    rejected: tuple[tuple[str, str], ...]
    inspection: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DataIntelligenceReport:
    row_count: int | None
    columns: tuple[str, ...]
    cardinality: Mapping[str, int]
    datetime_columns: tuple[str, ...]
    geospatial_columns: tuple[str, ...]
    bounded: bool
    notes: tuple[str, ...] = ()


_renderers: list[RendererSpec] = []
_last_decision: AutoDecision | None = None
_MAX_INSPECT_ROWS = 200
_MAX_INSPECT_COLS = 50


def clear_renderers_for_tests() -> None:
    global _last_decision
    _renderers.clear()
    _last_decision = None
    _register_defaults()


def register_renderer(spec: RendererSpec) -> None:
    # Deterministic order: priority desc, then name asc — never import order.
    _renderers[:] = sorted(
        (*[r for r in _renderers if r.name != spec.name], spec),
        key=lambda r: (-r.priority, r.name),
    )


def get_last_auto_decision() -> AutoDecision | None:
    return _last_decision


def inspect_data(value: object) -> DataIntelligenceReport:
    """Bounded schema/size/cardinality inspection; refuses unbounded lazy collect."""
    notes: list[str] = []
    rows: list[Mapping[str, object]] = []
    if isinstance(value, Mapping) and not hasattr(value, "model_dump"):
        # single mapping or column-oriented
        if value and all(
            isinstance(v, Sequence) and not isinstance(v, (str, bytes)) for v in value.values()
        ):
            keys = list(value.keys())[:_MAX_INSPECT_COLS]
            length = len(next(iter(value.values())))
            if length > _MAX_INSPECT_ROWS:
                notes.append(f"truncated rows to {_MAX_INSPECT_ROWS}")
            n = min(length, _MAX_INSPECT_ROWS)
            rows = [{str(k): value[k][i] for k in keys} for i in range(n)]
        else:
            rows = [cast(Mapping[str, object], value)]
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        if hasattr(value, "__len__") and len(value) > _MAX_INSPECT_ROWS:
            notes.append(f"truncated rows to {_MAX_INSPECT_ROWS}")
        sample = list(value[:_MAX_INSPECT_ROWS])
        for item in sample:
            if isinstance(item, Mapping):
                rows.append(cast(Mapping[str, object], item))
            elif hasattr(item, "model_dump"):
                rows.append(item.model_dump())
    elif hasattr(value, "__iter__") and not isinstance(value, (str, bytes, Mapping)):
        type_name = type(value).__name__
        if "lazy" in type_name.lower() or type_name.endswith("QuerySet"):
            raise error(
                "HED-AUTO-0002",
                title="Implicit lazy collection refused",
                explanation=f"Auto inspection will not collect lazy type {type_name}.",
                remediation="Pass a bounded page or materialized rows.",
            )
        # dataframe-like
        module = type(value).__module__.split(".")[0]
        if module in {"pandas", "polars", "pyarrow"}:
            try:
                from hedron_data.normalize import normalize_rows

                rows = cast(
                    list[Mapping[str, object]],
                    normalize_rows(value, max_rows=_MAX_INSPECT_ROWS),
                )
            except Exception as exc:
                notes.append(f"dataframe inspect skipped: {exc}")
        else:
            notes.append(f"unrecognized iterable {type_name}")

    columns: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for k in row:
            if k not in seen and len(columns) < _MAX_INSPECT_COLS:
                seen.add(str(k))
                columns.append(str(k))
    cardinality: dict[str, int] = {}
    datetime_cols: list[str] = []
    geo_cols: list[str] = []
    for col in columns:
        values = [row.get(col) for row in rows]
        cardinality[col] = len({repr(v) for v in values})
        name = col.lower()
        if "date" in name or "time" in name:
            datetime_cols.append(col)
        if name in {"lat", "lon", "lng", "latitude", "longitude", "geo"}:
            geo_cols.append(col)
    return DataIntelligenceReport(
        row_count=len(rows) if rows else None,
        columns=tuple(columns),
        cardinality=cardinality,
        datetime_columns=tuple(datetime_cols),
        geospatial_columns=tuple(geo_cols),
        bounded=True,
        notes=tuple(notes),
    )


def _is_component(value: object) -> bool:
    return isinstance(value, Component) or hasattr(value, "__hedron_node__")


def _is_tabular(value: object) -> bool:
    if isinstance(value, Sequence) and value and not isinstance(value, (str, bytes)):
        first = value[0]
        return isinstance(first, Mapping) or hasattr(first, "model_dump")
    module = type(value).__module__.split(".")[0]
    return type(value).__name__ == "DataFrame" and module in {"pandas", "polars"}


def _is_chart_like(value: object) -> bool:
    module = type(value).__module__
    name = type(value).__name__
    return (
        module.startswith("plotly")
        or module.startswith("altair")
        or (module.startswith("matplotlib") and name.lower().endswith("figure"))
    )


def _factory_component(value: object) -> NodeLike:
    return cast(NodeLike, value)


def _factory_datatable(value: object) -> NodeLike:
    try:
        from hedron_data import DataTable

        return DataTable(value)
    except ImportError as exc:
        raise error(
            "HED-AUTO-0003",
            title="hedron-data required",
            explanation="Tabular Auto() rendering requires hedron-data.",
            remediation="pip install hedron-data",
        ) from exc


def _factory_mapping(value: object) -> NodeLike:
    mapping = cast(Mapping[object, object], value)
    if len(mapping) > 20:
        return JSONViewer(mapping)
    pairs: list[tuple[NodeLike, NodeLike]] = [
        (str(k), cast(NodeLike, "***" if "secret" in str(k).lower() else v))
        for k, v in mapping.items()
    ]
    return DescriptionList(*pairs)


def _factory_sequence(value: object) -> NodeLike:
    seq = cast(Sequence[object], value)
    return HedronList(*[str(v) for v in seq[:100]])


def _factory_text(value: object) -> NodeLike:
    return Text(str(value))


def _factory_chart_reject(value: object) -> NodeLike:
    raise error(
        "HED-AUTO-0004",
        title="Chart adapters require hedron-charts",
        explanation=f"No chart renderer for {type(value).__name__} .",
        remediation="Install hedron-charts or pass an explicit chart component.",
    )


def _register_defaults() -> None:
    if any(r.name == "component" for r in _renderers):
        return
    register_renderer(
        RendererSpec(
            name="component",
            priority=1000,
            predicate=_is_component,
            explanation="Passthrough Hedron components",
            factory=_factory_component,
        )
    )
    register_renderer(
        RendererSpec(
            name="chart-stub",
            priority=900,
            predicate=_is_chart_like,
            optional_package="hedron-charts",
            explanation="Charts via hedron-charts when installed",
            factory=_factory_chart_reject,
        )
    )
    register_renderer(
        RendererSpec(
            name="datatable",
            priority=800,
            predicate=_is_tabular,
            optional_package="hedron-data",
            cost=5,
            explanation="Tabular rows → DataTable",
            factory=_factory_datatable,
        )
    )
    register_renderer(
        RendererSpec(
            name="mapping",
            priority=500,
            types=(dict,),
            predicate=lambda v: isinstance(v, Mapping),
            explanation="Mappings → DescriptionList or JSONViewer",
            factory=_factory_mapping,
        )
    )
    register_renderer(
        RendererSpec(
            name="sequence",
            priority=400,
            predicate=lambda v: (
                isinstance(v, Sequence) and not isinstance(v, (str, bytes)) and not _is_tabular(v)
            ),
            explanation="Sequences → List",
            factory=_factory_sequence,
        )
    )
    register_renderer(
        RendererSpec(
            name="text",
            priority=100,
            predicate=lambda v: v is not None,
            explanation="Fallback text rendering",
            factory=_factory_text,
        )
    )


class AutoProps(Props):
    as_: str | None = None


class Auto(Component[AutoProps]):
    """Select an appropriate component through the inspectable renderer registry."""

    props_type = AutoProps
    logical_name = "Auto"

    def __init__(self, value: object = None, *, as_: str | None = None, **kwargs: Any) -> None:
        super().__init__(AutoProps(as_=as_, **kwargs))
        self._value = value
        self._resolved: NodeLike | None = None
        self._decision: AutoDecision | None = None

    @property
    def decision(self) -> AutoDecision | None:
        return self._decision

    def resolve(self) -> NodeLike:
        global _last_decision
        value = self._value
        inspection: dict[str, object] = {}
        if _is_tabular(value) or isinstance(value, Mapping):
            try:
                report = inspect_data(value)
                inspection = {
                    "row_count": report.row_count,
                    "columns": list(report.columns),
                    "cardinality": dict(report.cardinality),
                    "datetime_columns": list(report.datetime_columns),
                    "geospatial_columns": list(report.geospatial_columns),
                    "notes": list(report.notes),
                }
            except Exception as exc:
                inspection = {"error": str(exc)}

        candidates: list[str] = []
        rejected: list[tuple[str, str]] = []
        selected_spec: RendererSpec | None = None

        if self.props.as_:
            for spec in _renderers:
                if spec.name == self.props.as_:
                    selected_spec = spec
                    candidates.append(spec.name)
                    break
            if selected_spec is None:
                raise error(
                    "HED-AUTO-0001",
                    title="Unknown Auto renderer",
                    explanation=f"No renderer named {self.props.as_!r}.",
                    remediation=f"Known renderers: {[r.name for r in _renderers]}",
                )
        else:
            for spec in _renderers:
                candidates.append(spec.name)
                matched = False
                if spec.predicate is not None:
                    try:
                        matched = bool(spec.predicate(value))
                    except Exception as exc:
                        rejected.append((spec.name, f"predicate error: {exc}"))
                        continue
                elif spec.types:
                    matched = isinstance(value, spec.types)
                if not matched:
                    rejected.append((spec.name, "type/predicate mismatch"))
                    continue
                selected_spec = spec
                break

        if selected_spec is None or selected_spec.factory is None:
            raise error(
                "HED-AUTO-0001",
                title="No Auto renderer matched",
                explanation=f"No renderer for value of type {type(value).__name__}.",
                remediation="Pass as_= explicitly or register a renderer.",
            )

        self._decision = AutoDecision(
            selected=selected_spec.name,
            candidates=tuple(candidates),
            rejected=tuple(rejected),
            inspection=inspection,
        )
        _last_decision = self._decision
        self._resolved = selected_spec.factory(value)
        return self._resolved

    def render(self) -> NodeLike:
        # Return the resolved Component/NodeLike so the renderer owns identity,
        # cycle detection, and diagnostics (do not call child .render() here).
        return self.resolve()


_register_defaults()
