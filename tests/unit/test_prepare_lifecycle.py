"""Component prepare() lifecycle (PREP-013)."""

from __future__ import annotations

import asyncio

import pytest
from starlette.requests import Request

from hedron import Hedron
from hedron_core.builtins.content import Text
from hedron_core.builtins.document import Page
from hedron_core.component import Component
from hedron_core.diagnostics import HedronError
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.prepare import (
    PartialFailurePolicy,
    PrepareContext,
    collect_prepare_targets,
    prepare_tree,
)
from hedron_core.rendering import RenderMode, render


class _FetchProps(Props):
    label: str = "ready"


class FetchCard(Component[_FetchProps]):
    props_type = _FetchProps

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self.prepared: str | None = None

    async def prepare(self, ctx: PrepareContext) -> None:
        ctx.check()
        self.prepared = await ctx.cached("label", lambda: self.props.label)

    def render(self) -> object:
        return Text(self.prepared or "missing")


class FailingPrep(Component[_FetchProps]):
    props_type = _FetchProps

    async def prepare(self, ctx: PrepareContext) -> None:
        del ctx
        raise RuntimeError("boom")

    def render(self) -> object:
        return Text("x")


@pytest.mark.anyio
async def test_prepare_runs_before_render() -> None:
    card = FetchCard(label="hello")
    ctx = await prepare_tree(Page(card))
    assert card.prepared == "hello"
    assert ctx.timings
    html = render(Page(card), mode=RenderMode.FRAGMENT).html
    assert "hello" in html


@pytest.mark.anyio
async def test_prepare_reaches_components_inside_native_html_elements() -> None:
    card = FetchCard(label="wrapped")
    await prepare_tree(html.div(card))
    assert card.prepared == "wrapped"


@pytest.mark.anyio
async def test_prepare_cancel_via_deadline() -> None:
    card = FetchCard(label="x")

    async def _hang(ctx: PrepareContext) -> None:
        ctx.cancel()
        ctx.check()

    card.prepare = _hang  # type: ignore[method-assign]
    with pytest.raises(HedronError):
        await prepare_tree(card, context=PrepareContext())


@pytest.mark.anyio
async def test_partial_failure_continue() -> None:
    ok = FetchCard(label="ok")
    bad = FailingPrep(label="bad")
    ctx = PrepareContext(partial_failure=PartialFailurePolicy.CONTINUE)
    await prepare_tree([ok, bad], context=ctx)
    assert ok.prepared == "ok"
    assert any(t.error for t in ctx.timings)


@pytest.mark.anyio
async def test_fail_fast_cancels_sibling_prepare_tasks() -> None:
    started = asyncio.Event()
    side_effects: list[str] = []

    class Slow(Component[_FetchProps]):
        props_type = _FetchProps

        async def prepare(self, ctx: PrepareContext) -> None:
            del ctx
            started.set()
            await asyncio.sleep(0.05)
            side_effects.append("late")

        def render(self) -> object:
            return Text("slow")

    class Fail(Component[_FetchProps]):
        props_type = _FetchProps

        async def prepare(self, ctx: PrepareContext) -> None:
            del ctx
            await started.wait()
            raise RuntimeError("boom")

        def render(self) -> object:
            return Text("fail")

    with pytest.raises(RuntimeError, match="boom"):
        await prepare_tree([Slow(), Fail()])
    await asyncio.sleep(0.1)
    assert side_effects == []


@pytest.mark.anyio
async def test_collect_prepare_targets_handles_deep_trees_iteratively() -> None:
    card = FetchCard(label="leaf")
    node: object = card
    for _ in range(1500):
        node = Page(node)  # type: ignore[arg-type]
    assert collect_prepare_targets(node) == [card]


def test_collect_skips_default_prepare() -> None:
    targets = collect_prepare_targets(Text("a"))
    assert targets == []


@pytest.mark.anyio
async def test_cache_handoff() -> None:
    card = FetchCard(label="cached")
    ctx = PrepareContext()
    await prepare_tree(card, context=ctx)
    assert "label" in ctx.cache


@pytest.mark.anyio
async def test_cached_is_single_flight_under_concurrent_await() -> None:
    """#577: concurrent ctx.cached misses must share one factory invocation."""
    import asyncio

    ctx = PrepareContext()
    calls = {"n": 0}

    async def factory() -> int:
        calls["n"] += 1
        await asyncio.sleep(0.05)
        return calls["n"]

    async def one() -> int:
        return await ctx.cached("k", factory)

    values = await asyncio.gather(one(), one(), one())
    assert values == [1, 1, 1]
    assert calls["n"] == 1
    assert ctx.cache["k"] == 1


@pytest.mark.anyio
async def test_prepare_deadline_header_rejects_non_finite_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Trusted proxy headers must not turn a finite prepare budget into infinity."""
    from hedron.routing.route import prepare_endpoint_value

    app = Hedron(title="prepare-deadline", explorer="off", session_secret="prepare-secret")
    app.state.hedron_trusted_peers = ["127.0.0.1"]
    captured: dict[str, object] = {}

    async def fake_prepare_tree(
        value: object, *, context: PrepareContext, **kwargs: object
    ) -> None:
        del value, kwargs
        captured["deadline"] = context.deadline

    monkeypatch.setattr("hedron_core.prepare.prepare_tree", fake_prepare_tree)
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [(b"x-hedron-prepare-deadline", b"inf")],
            "client": ("127.0.0.1", 1234),
            "app": app,
        }
    )
    await prepare_endpoint_value(Text("x"), request=request)
    assert captured["deadline"] is None
