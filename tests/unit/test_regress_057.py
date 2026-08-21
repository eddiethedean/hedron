"""REGRESS-057 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core import AppShell, Button, Card, NavLink, Stack, Status, Text
from hedron_core.rendering import RenderContext, RenderMode, render


def test_regress_057_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.57.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["REGRESS-057"]["state"] == "Verified"


def test_existing_calls_remain_compatible() -> None:
    ctx = RenderContext.standalone()
    button = render(Button("Primary"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert "hedron-button-primary" in button
    stack = render(Stack(Text("ok"), gap="1rem"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert 'data-hedron-gap="md"' in stack
    status = render(Status("Ready"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert "hedron-status-info" in status
    card = render(Card(Text("body"), title="T"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert "hedron-card" in card
    shell = render(
        AppShell(nav=NavLink("Home", "/"), body=Text("main"), brand=Text("Brand")),
        context=ctx,
        mode=RenderMode.FRAGMENT,
    ).html
    assert "hedron-app-shell" in shell
