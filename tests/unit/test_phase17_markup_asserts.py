"""Phase 0.17 Dialog/Tabs/Pagination/Lazy markup asserts (ASSERT-017)."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from hedron.builtins import Lazy, Pagination
from hedron.routing import ComponentRef
from hedron_core import Dialog, Tabs, render
from hedron_core.testing.adapters import (
    assert_dialog_markup,
    assert_lazy_markup,
    assert_pagination_markup,
    assert_tabs_markup,
)


@dataclass
class _Resp:
    body: str
    status_code: int = 200
    headers: dict[str, str] | None = None


def test_assert_dialog_markup() -> None:
    html = render(Dialog("Title", "Body", open=True, id="dlg")).html
    assert_dialog_markup(_Resp(html), contains="Title")
    with pytest.raises(AssertionError):
        assert_dialog_markup(_Resp("<div>plain</div>"))


def test_assert_tabs_markup() -> None:
    html = render(Tabs(("One", "A"), ("Two", "B"))).html
    assert_tabs_markup(_Resp(html), contains="One")


def test_assert_pagination_and_lazy_markup() -> None:
    page = render(
        Pagination(page=1, page_size=10, total=30, base_path="/items", target="#list")
    ).html
    assert_pagination_markup(_Resp(page))
    lazy = render(Lazy(ref=ComponentRef(logical_id="x", path="/frag", method="GET"))).html
    assert_lazy_markup(_Resp(lazy))
