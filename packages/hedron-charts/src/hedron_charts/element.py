"""First-party Chart / hedron-chart components (phase 0.38)."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, cast

from hedron_charts.compile import beginner_to_spec, compile_chart
from hedron_charts.export import export_csv, export_svg
from hedron_charts.limits import redact_rows, reject_active_svg
from hedron_charts.spec import ChartPlan, ChartSpec
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import TrustedHtml
from hedron_core.typing_aliases import JsonValue

ABI_VERSION = 1
TAG_NAME = "hedron-chart"
ELEMENT_ID = "hedron-chart"

__all__ = [
    "ABI_VERSION",
    "Chart",
    "ELEMENT_ID",
    "TAG_NAME",
    "chart_from_beginner",
    "fallback_nodes",
    "plan_payload_json",
]


def plan_payload_json(plan: ChartPlan) -> str:
    payload = plan.to_json_dict()
    if not plan.accessibility.include_table:
        payload = dict(payload)
        raw_acc = payload.get("accessibility")
        acc = dict(raw_acc) if isinstance(raw_acc, dict) else {}
        acc["table_rows"] = []
        payload["accessibility"] = acc
    return json.dumps(payload, separators=(",", ":"), default=str)


def fallback_nodes(plan: ChartPlan) -> list[NodeLike]:
    nodes: list[NodeLike] = [
        html.figcaption(
            html.strong(plan.accessibility.title),
            html.span(f" — {plan.accessibility.description}"),
        ),
    ]
    static_svg = export_svg(plan, authorized=True)
    reject_active_svg(static_svg)
    nodes.append(html.raw(TrustedHtml.reviewed(static_svg, source="hedron-charts:first-party-svg")))
    nodes.append(html.p(plan.accessibility.summary, class_="hedron-chart-summary"))
    if plan.accessibility.include_table and plan.transformed_rows:
        cleaned = redact_rows(list(plan.transformed_rows))
        headers = list(cleaned[0].keys())
        head = html.tr(*[html.th(h) for h in headers])
        body = [html.tr(*[html.td(str(row.get(h, ""))) for h in headers]) for row in cleaned]
        nodes.append(
            html.table(html.thead(head), html.tbody(*body), class_="hedron-chart-fallback")
        )
    else:
        nodes.append(
            html.pre(export_csv(plan, authorized=True)[:2000], class_="hedron-chart-static-csv")
        )
    return nodes


class ChartProps(Props):
    title: str = "Chart"
    class_: str | None = None


class Chart(Component[ChartProps]):
    """Advanced Chart(spec=...) entry that compiles to ChartPlan + hedron-chart."""

    props_type = ChartProps
    logical_name = "Chart"
    distribution = "hedron-charts"

    def __init__(
        self,
        spec: ChartSpec | Mapping[str, Any] | None = None,
        *,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        title = "Chart"
        if isinstance(spec, ChartSpec):
            title = spec.accessibility.title
            payload = spec.to_json_dict()
        elif spec is None:
            payload = None
        else:
            payload = dict(spec)
            raw_acc = payload.get("accessibility")
            acc: Mapping[str, Any] = (
                cast(Mapping[str, Any], raw_acc) if isinstance(raw_acc, dict) else {}
            )
            title = str(acc.get("title") or "Chart")
        super().__init__(ChartProps(title=title, class_=class_, **kwargs))
        self._spec = payload

    def compile_plan(self) -> ChartPlan:
        if not self._spec:
            raise ValueError("Chart requires a spec")
        return compile_chart(self._spec)

    def render(self) -> NodeLike:
        plan = self.compile_plan()
        payload = plan_payload_json(plan)
        children = fallback_nodes(plan)
        return html.tag(TAG_NAME)(
            html.figure(
                *children,
                class_="hedron-chart-fallback-figure",
            ),
            **{
                "data-hedron-abi": str(ABI_VERSION),
                "data-hedron-element": ELEMENT_ID,
                "data-hedron-chart": "first-party",
                "data-hedron-payload": payload,
                "role": "group",
                "aria-label": plan.accessibility.title,
                "class_": self.props.class_,
            },
        )


def chart_from_beginner(
    *,
    kind: str,
    data: Sequence[Mapping[str, JsonValue]],
    x: str,
    y: str,
    title: str,
    description: str,
    color: str | None = None,
    class_: str | None = None,
) -> Chart:
    spec = beginner_to_spec(
        kind=kind,
        data=data,
        x=x,
        y=y,
        title=title,
        description=description,
        color=color,
    )
    return Chart(spec=spec, class_=class_)
