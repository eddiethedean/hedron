"""Component prepare() lifecycle (PREP-013)."""

from __future__ import annotations

import pytest

from hedron_core.builtins.content import Text
from hedron_core.builtins.document import Page
from hedron_core.component import Component
from hedron_core.diagnostics import HedronError
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