"""Default Auto renderer predicates and factories."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import cast

from hedron_core.auto.registry import register_renderer, registered_renderers
from hedron_core.auto.spec import RendererSpec
from hedron_core.builtins.content import DescriptionList, Text
from hedron_core.builtins.content import List as HedronList
from hedron_core.builtins.utilities import JSONViewer
from hedron_core.component import Component, NodeLike
from hedron_core.data import DataSource
from hedron_core.diagnostics import error


def is_component(value: object) -> bool:
    return isinstance(value, Component) or hasattr(value, "__hedron_node__")


def is_tabular(value: object) -> bool:
    if isinstance(value, DataSource):
        return True
    if isinstance(value, Sequence) and value and not isinstance(value, (str, bytes)):
        first = value[0]
        return isinstance(first, Mapping) or hasattr(first, "model_dump")
    return hasattr(value, "columns") and callable(getattr(value, "head", None))


def is_chart_like(value: object) -> bool:
    module = type(value).__module__
    name = type(value).__name__
    return (
        module.startswith("plotly")
        or module.startswith("altair")
        or (module.startswith("matplotlib") and name.lower().endswith("figure"))
    )


def factory_component(value: object) -> NodeLike:
    return cast(NodeLike, value)


def factory_datatable(value: object) -> NodeLike:
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


def factory_mapping(value: object) -> NodeLike:
    mapping = cast(Mapping[object, object], value)
    if len(mapping) > 20:
        return JSONViewer(mapping)
    pairs: list[tuple[NodeLike, NodeLike]] = [
        (str(k), cast(NodeLike, "***" if "secret" in str(k).lower() else v))
        for k, v in mapping.items()
    ]
    return DescriptionList(*pairs)


def factory_sequence(value: object) -> NodeLike:
    seq = cast(Sequence[object], value)
    return HedronList(*[str(v) for v in seq[:100]])


def factory_text(value: object) -> NodeLike:
    return Text(str(value))


def factory_chart_reject(value: object) -> NodeLike:
    raise error(
        "HED-AUTO-0004",
        title="Chart adapters require hedron-charts",
        explanation=f"No chart renderer for {type(value).__name__} .",
        remediation="Install hedron-charts or pass an explicit chart component.",
    )


def register_defaults() -> None:
    if any(r.name == "component" for r in registered_renderers()):
        return
    register_renderer(
        RendererSpec(
            name="component",
            priority=1000,
            predicate=is_component,
            explanation="Passthrough Hedron components",
            factory=factory_component,
        )
    )
    register_renderer(
        RendererSpec(
            name="chart-stub",
            priority=900,
            predicate=is_chart_like,
            optional_package="hedron-charts",
            explanation="Charts via hedron-charts when installed",
            factory=factory_chart_reject,
        )
    )
    register_renderer(
        RendererSpec(
            name="datatable",
            priority=800,
            predicate=is_tabular,
            optional_package="hedron-data",
            cost=5,
            explanation="Tabular rows → DataTable",
            factory=factory_datatable,
        )
    )
    register_renderer(
        RendererSpec(
            name="mapping",
            priority=500,
            types=(dict,),
            predicate=lambda v: isinstance(v, Mapping),
            explanation="Mappings → DescriptionList or JSONViewer",
            factory=factory_mapping,
        )
    )
    register_renderer(
        RendererSpec(
            name="sequence",
            priority=400,
            predicate=lambda v: (
                isinstance(v, Sequence) and not isinstance(v, (str, bytes)) and not is_tabular(v)
            ),
            explanation="Sequences → List",
            factory=factory_sequence,
        )
    )
    register_renderer(
        RendererSpec(
            name="text",
            priority=100,
            predicate=lambda v: v is not None,
            explanation="Fallback text rendering",
            factory=factory_text,
        )
    )
