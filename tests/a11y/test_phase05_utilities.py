"""Accessibility smoke checks for phase 0.5 utilities and tables."""

from __future__ import annotations

import pytest

from hedron_core import Expander, Metric, Progress, Status, Tabs, Toast, render
from hedron_core.color_mode import ColorModeToggle
from hedron_data import Column, DataTable


@pytest.mark.a11y
def test_datatable_headers_and_caption() -> None:
    html = render(
        DataTable(
            [{"id": "1", "name": "Ada"}],
            columns=[Column(name="id"), Column(name="name")],
            caption="People",
        )
    ).html
    assert 'scope="col"' in html
    assert "<caption>People</caption>" in html


@pytest.mark.a11y
def test_utility_live_regions_and_semantics() -> None:
    assert 'role="group"' in render(Metric("Users", 3)).html
    assert "<progress" in render(Progress(1, maximum=5, label="Load")).html
    assert 'aria-live="polite"' in render(Status("Saved")).html
    assert 'aria-live="polite"' in render(Toast("Hi")).html
    assert "<summary" in render(Expander("More", "x")).html
    assert 'role="tablist"' in render(Tabs(("A", "1"), ("B", "2"))).html
    assert 'aria-label="Color mode"' in render(ColorModeToggle()).html


@pytest.mark.a11y
def test_sidebar_accessible_label() -> None:
    from hedron_core import Sidebar, Text

    html = render(Sidebar(Text("item"), label="Navigation")).html
    assert 'aria-label="Navigation"' in html
