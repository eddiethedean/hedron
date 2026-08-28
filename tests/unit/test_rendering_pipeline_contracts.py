"""Substitution contracts for the SOLID rendering pipeline."""

from __future__ import annotations

from collections.abc import Iterable

from hedron_core import Text
from hedron_core._nodes import Node, TextNode
from hedron_core.alpine import AlpineFeatureDemand, BrowserFeaturePlan
from hedron_core.component import Component, NodeLike
from hedron_core.models import Props
from hedron_core.rendering import RenderContext, RenderMode, RenderSession
from hedron_core.rendering.browser_plan import BrowserPlanBuilder
from hedron_core.rendering.normalize import Normalizer
from hedron_core.rendering.state import RenderState


class _ProbeProps(Props):
    value: str = "default"


class _Probe(Component[_ProbeProps]):
    props_type = _ProbeProps

    def render(self) -> NodeLike:
        return Text(self.props.value)


class _ProbeComponentRenderer:
    def render(
        self,
        component: Component[Props],
        state: RenderState,
        *,
        depth: int,
        normalize: Normalizer,
    ) -> tuple[Node, ...]:
        del component, state, depth
        return (TextNode("substituted"),)


class _ProbePlanBuilder(BrowserPlanBuilder):
    def __init__(self) -> None:
        self.calls = 0

    def build(self, demands: Iterable[AlpineFeatureDemand]) -> BrowserFeaturePlan:
        self.calls += 1
        assert tuple(demands) == ()
        return BrowserFeaturePlan()


def test_session_accepts_substitutable_pipeline_policies() -> None:
    plan_builder = _ProbePlanBuilder()
    session = RenderSession(
        RenderContext.standalone(),
        component_renderer=_ProbeComponentRenderer(),
        browser_plan_builder=plan_builder,
        serializer=lambda value, nodes, context, mode: (
            f"{mode.value}:{context.locale}:" + str(len(nodes)) + ":" + "|".join(
                node.text for node in nodes if isinstance(node, TextNode)
            )
        ),
    )

    result = session.render(_Probe(value="original"), mode=RenderMode.FRAGMENT)

    assert result.html == "fragment:en:1:substituted"
    assert plan_builder.calls == 1
