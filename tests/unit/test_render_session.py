"""Shared core render-session invariants."""

from __future__ import annotations

import pytest

from hedron_core import Badge, HedronError, RenderContext, RenderSession


def test_render_session_assigns_unique_auto_identity_across_calls() -> None:
    session = RenderSession()

    first = session.render(Badge(text="one"))
    second = session.render(Badge(text="two"))

    assert len(first.identity_map) == 1
    assert len(second.identity_map) == 1
    assert len(session.identity_map) == 2
    assert len(set(session.identity_map.values())) == 2


def test_render_session_shares_node_budget_across_calls() -> None:
    session = RenderSession(RenderContext(max_nodes=3))
    session.render(Badge(text="one"))

    with pytest.raises(HedronError) as exc:
        session.render(Badge(text="two"))

    assert exc.value.diagnostic.code == "HED-RENDER-0010"
