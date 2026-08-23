"""SURFACE-057 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

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
from hedron_core.diagnostics import HedronError
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
    brand = render(
        Brand("Hedron", href="/", mark_text="H", subtitle="Typed UI"),
        context=ctx,
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'data-hedron-brand="true"' in brand
    assert 'class="hedron-brand-copy"' in brand
    assert 'class="hedron-brand-subtitle"' in brand
    account = render(
        AccountSummary("Ada", detail="Admin", href="/account", mark_text="A", action=Text("Sign out")),
        context=ctx,
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'data-hedron-account-summary="true"' in account
    assert 'href="/account"' in account
    assert 'class="hedron-account-copy"' in account
    assert "Sign out" in account
    banner = render(EnvironmentBanner("Staging"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert 'data-hedron-environment-banner="true"' in banner
    status = render(NavStatus("Connected"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert 'data-hedron-nav-status="true"' in status
    footer = render(AppFooter("© Hedron"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert 'data-hedron-app-footer="true"' in footer
    with pytest.raises(HedronError):
        Brand("   ")
    with pytest.raises(HedronError):
        AccountSummary("")
    with pytest.raises(HedronError):
        Surface(Text("x"), appearance="soft")
    css = Path("packages/hedron-core/src/hedron_core/static/hedron-default.css").read_text(
        encoding="utf-8"
    )
    assert '[data-hedron-content-width="full"]' in css
    assert '[data-hedron-mobile-collapse="off"]' in css
    assert '[data-hedron-padding="md"]' in css
    assert '[data-hedron-elevation="none"]' in css
