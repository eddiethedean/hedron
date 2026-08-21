"""SURFACE-057 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core import (
    AccountSummary,
    AppFooter,
    Brand,
    Card,
    EnvironmentBanner,
    NavStatus,
    Surface,
    Text,
)
from hedron_core.rendering import RenderContext, RenderMode, render


def test_surface_057_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.57.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["SURFACE-057"]["state"] == "Verified"


def test_surface_card_and_typed_chrome() -> None:
    ctx = RenderContext.standalone()
    surface = render(
        Surface(Text("panel"), appearance="raised", elevation="md", padding="sm"),
        context=ctx,
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'data-hedron-surface="true"' in surface
    assert 'data-hedron-appearance="raised"' in surface
    card = render(
        Card(Text("body"), title="Title", appearance="plain", density="compact"),
        context=ctx,
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'data-hedron-appearance="plain"' in card
    brand = render(Brand("Hedron", href="/"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert 'data-hedron-brand="true"' in brand
    account = render(
        AccountSummary("Ada", detail="Admin"), context=ctx, mode=RenderMode.FRAGMENT
    ).html
    assert 'data-hedron-account-summary="true"' in account
    banner = render(EnvironmentBanner("Staging"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert 'data-hedron-environment-banner="true"' in banner
    status = render(NavStatus("Connected"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert 'data-hedron-nav-status="true"' in status
    footer = render(AppFooter("© Hedron"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert 'data-hedron-app-footer="true"' in footer
