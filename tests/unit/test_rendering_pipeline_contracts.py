"""Substitution contracts for the SOLID rendering pipeline."""

from __future__ import annotations

from collections.abc import Iterable

import pytest

from hedron_core import HedronError, html
from hedron_core._nodes import Node
from hedron_core.alpine import AlpineFeatureDemand, BrowserFeaturePlan
from hedron_core.component import Component, NodeLike
from hedron_core.html import _NativeElement
from hedron_core.models import Props
from hedron_core.rendering import RenderContext, RenderMode, RenderSession
from hedron_core.rendering.session import serialize_result
from hedron_core.rendering.state import RenderState


class _ProbeProps(Props):
    value: str = "default"


class _Probe(Component[_ProbeProps]):
    props_type = _ProbeProps

    def render(self) -> NodeLike:
        return self.props.value


class _FalsyPolicy:
    def __bool__(self) -> bool:
        return False


class _ProbeComponentRenderer(_FalsyPolicy):
    def __init__(self) -> None:
        self.calls = 0

    def render(self, component: Component[Props]) -> NodeLike:
        del component
        self.calls += 1
        return html.div("substituted")


class _ProbeBrowserCollector(_FalsyPolicy):
    def __init__(self) -> None:
        self.calls = 0

    def collect(self, element: _NativeElement, state: RenderState) -> None:
        del element, state
        self.calls += 1


class _ProbePlanBuilder(_FalsyPolicy):
    def __init__(self) -> None:
        self.calls = 0

    def build(self, demands: Iterable[AlpineFeatureDemand]) -> BrowserFeaturePlan:
        self.calls += 1
        assert tuple(demands) == ()
        return BrowserFeaturePlan()


class _ProbeSerializer(_FalsyPolicy):
    def __init__(self) -> None:
        self.calls = 0

    def __call__(
        self,
        value: NodeLike,
        nodes: tuple[Node, ...],
        context: RenderContext,
        mode: RenderMode,
    ) -> str:
        self.calls += 1
        return serialize_result(value, nodes, context, mode)


def test_session_accepts_falsy_substitutable_pipeline_policies() -> None:
    component_renderer = _ProbeComponentRenderer()
    browser_collector = _ProbeBrowserCollector()
    plan_builder = _ProbePlanBuilder()
    serializer = _ProbeSerializer()
    session = RenderSession(
        RenderContext.standalone(),
        component_renderer=component_renderer,
        browser_collector=browser_collector,
        browser_plan_builder=plan_builder,
        serializer=serializer,
    )

    result = session.render(_Probe(value="original"), mode=RenderMode.FRAGMENT)

    assert result.html == "<div>substituted</div>"
    assert len(result.identity_map) == 1
    assert component_renderer.calls == 1
    assert browser_collector.calls == 1
    assert plan_builder.calls == 1
    assert serializer.calls == 1


def test_component_renderer_cannot_bypass_node_accounting() -> None:
    session = RenderSession(
        RenderContext(max_nodes=1), component_renderer=_ProbeComponentRenderer()
    )

    with pytest.raises(HedronError) as exc:
        session.render(_Probe(value="original"))

    assert exc.value.diagnostic.code == "HED-RENDER-0010"
