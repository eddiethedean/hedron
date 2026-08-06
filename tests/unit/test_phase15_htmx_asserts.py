"""Phase 0.15 HTMX InteractionResult / region / shell asserts."""

from __future__ import annotations

import pytest

from hedron_core.interaction import FragmentRegion
from hedron_core.testing.adapters import (
    AdapterResponse,
    assert_hx_push_url,
    assert_hx_redirect,
    assert_hx_reswap,
    assert_hx_retarget,
    assert_oob_present,
    assert_toast_markup,
)
from hedron_core.testing.htmx_asserts import (
    assert_shell_dual_path,
    assert_ui_targets_subset_of_regions,
    assert_undeclared_target_rejected,
)


def _resp(
    status: int = 200,
    body: str = "",
    headers: dict[str, str] | None = None,
) -> AdapterResponse:
    return AdapterResponse(status, body, headers or {})


def test_assert_hx_headers() -> None:
    response = _resp(
        headers={
            "HX-Redirect": "/done",
            "HX-Push-Url": "/pushed",
            "HX-Retarget": "#panel",
            "HX-Reswap": "outerHTML",
        }
    )
    assert_hx_redirect(response, "/done")
    assert_hx_push_url(response, "/pushed")
    assert_hx_retarget(response, "#panel")
    assert_hx_reswap(response, "outerHTML")
    with pytest.raises(AssertionError):
        assert_hx_redirect(response, "/other")


def test_assert_oob_and_toast() -> None:
    oob = _resp(body='<div id="toast" hx-swap-oob="true">Saved</div>')
    assert_oob_present(oob, contains="Saved")
    toast = _resp(body='<div class="hedron-toast hedron-toast-info" role="status">Hi</div>')
    assert_toast_markup(toast, contains="Hi")
    toast_data = _resp(body='<div data-hedron-toast="true">Ping</div>')
    assert_toast_markup(toast_data, contains="Ping")
    with pytest.raises(AssertionError):
        assert_oob_present(_resp(body="<div>no oob</div>"))
    with pytest.raises(AssertionError):
        assert_toast_markup(_resp(body="<div>plain</div>"))


def test_assert_undeclared_target_rejected() -> None:
    assert_undeclared_target_rejected(
        _resp(403, "FragmentRegionError: HX-Target is not an authorized declared fragment region")
    )
    assert_undeclared_target_rejected(
        _resp(403, '{"code":"HED-HTMX-0001","title":"Unauthorized fragment target"}')
    )
    with pytest.raises(AssertionError):
        # Generic CSRF-style 403 without region detail must not pass.
        assert_undeclared_target_rejected(_resp(403, "Forbidden"))
    with pytest.raises(AssertionError):
        assert_undeclared_target_rejected(_resp(200, "ok"))
    with pytest.raises(AssertionError):
        # 200 bodies that merely mention HX-Target must not pass.
        assert_undeclared_target_rejected(_resp(200, "missing HX-Target header"))


def test_assert_ui_targets_subset_of_regions() -> None:
    regions = (
        FragmentRegion(id="main", selector="#main"),
        FragmentRegion(id="side", selector="#side"),
    )
    html = '<button hx-target="#main"></button><a data-hx-target="#side"></a>'
    assert_ui_targets_subset_of_regions(html, regions)
    with pytest.raises(AssertionError):
        assert_ui_targets_subset_of_regions(
            '<button hx-target="#evil"></button>',
            regions,
        )


def test_assert_shell_dual_path() -> None:
    fragment = _resp(200, "<div>panel body</div>")
    page = _resp(200, "<html><body><div>panel body</div></body></html>")
    assert_shell_dual_path(fragment, page, fragment_contains="panel body")

    redirect = _resp(303, "")
    assert_shell_dual_path(fragment, redirect)

    with pytest.raises(AssertionError):
        assert_shell_dual_path(
            _resp(200, "<html><body>chrome</body></html>"),
            page,
            fragment_contains="chrome",
        )
