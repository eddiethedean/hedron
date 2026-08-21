"""DATA-057 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from hedron_core import (
    Avatar,
    Button,
    Identity,
    ResourceList,
    ResourceRow,
    Table,
    TableColumn,
    Text,
)
from hedron_core.diagnostics import HedronError
from hedron_core.rendering import RenderContext, RenderMode, render


def test_data_057_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.57.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["DATA-057"]["state"] == "Verified"


def test_table_resource_and_identity() -> None:
    ctx = RenderContext.standalone()
    text = render(
        Text("long", overflow="truncate", lines=2), context=ctx, mode=RenderMode.FRAGMENT
    ).html
    assert 'data-hedron-overflow="truncate"' in text
    assert 'data-hedron-lines="2"' in text
    assert "title=" not in text
    table = render(
        Table(
            ["Name", "State"],
            [["alpha", "ready"]],
            columns=[
                TableColumn(header="Name", overflow="truncate", priority=1),
                TableColumn(header="State", kind="status"),
            ],
            responsive="scroll",
            row_states=["selected"],
        ),
        context=ctx,
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'data-hedron-responsive="scroll"' in table
    assert 'data-hedron-row-state="selected"' in table
    resources = render(
        ResourceList(
            ResourceRow("Transfer", href="/t/1", description="nightly"), label="Transfers"
        ),
        context=ctx,
        mode=RenderMode.FRAGMENT,
    ).html
    assert "hedron-resource-list" in resources
    assert 'href="/t/1"' in resources
    with pytest.raises(HedronError):
        ResourceRow("Bad", href="/x", actions=Button("Edit"))
    avatar = render(Avatar("Ada Lovelace"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert "AL" in avatar
    identity = render(Identity("Ada", detail="owner"), context=ctx, mode=RenderMode.FRAGMENT).html
    assert "hedron-identity" in identity
