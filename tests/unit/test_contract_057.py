"""CONTRACT-057 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from hedron_core import Alert, Badge, Button, NavLink, Status
from hedron_core.builtins.appearance import (
    APPEARANCES,
    GAP_TOKENS,
    OVERFLOW_MODES,
    TRACKS,
    WIDTHS,
    appearance_data,
    normalize_gap,
)
from hedron_core.diagnostics import HedronError
from hedron_core.rendering import RenderContext, RenderMode, render


def test_contract_057_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.57.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["CONTRACT-057"]["state"] == "Verified"
    contract = tomllib.loads(
        Path("docs/acceptance/presentation-contract-057.toml").read_text(encoding="utf-8")
    )
    assert contract["authority"] == "hedron_core.builtins.appearance"
    assert "plain" in contract["appearance"]
    assert "raised" in contract["appearance"]


def test_shared_vocabulary_matches_locked_contract() -> None:
    assert APPEARANCES == ("solid", "outline", "soft", "ghost", "plain", "raised")
    assert WIDTHS == ("content", "field", "full")
    assert OVERFLOW_MODES == ("wrap", "break", "truncate", "clip")
    assert TRACKS == ("narrow", "default", "wide", "fluid")
    assert GAP_TOKENS == ("none", "xs", "sm", "md", "lg", "xl")
    assert appearance_data(appearance="plain", width="field", overflow="truncate") == {
        "hedron-appearance": "plain",
        "hedron-width": "field",
        "hedron-overflow": "truncate",
    }
    with pytest.raises(HedronError):
        appearance_data(appearance="loud")


def test_controls_adopt_appearance_markers() -> None:
    ctx = RenderContext.standalone()
    button = render(
        Button("Save", appearance="soft", emphasis="primary", size="sm"),
        context=ctx,
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'data-hedron-appearance="soft"' in button
    assert 'data-hedron-emphasis="primary"' in button
    badge = render(
        Badge("New", appearance="outline", size="sm"), context=ctx, mode=RenderMode.FRAGMENT
    ).html
    assert 'data-hedron-tone="neutral"' in badge
    alert = render(Alert("Heads up", appearance="soft"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert 'data-hedron-tone="info"' in alert
    status = render(Status("Ready", size="sm"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert 'data-hedron-tone="info"' in status
    nav = render(NavLink("Home", "/"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert "hedron-nav-link" in nav


def test_normalize_gap_tokens_and_compat_lengths() -> None:
    assert normalize_gap("md") == ("md", None)
    assert normalize_gap("1rem") == ("md", "1rem")
    assert normalize_gap("0.5rem") == ("sm", "0.5rem")
    with pytest.raises(HedronError):
        normalize_gap("12vw")
    with pytest.raises(HedronError):
        normalize_gap("0.75rem")
