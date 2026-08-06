"""Portable adapter test harness — re-exported from hedron-core for compatibility."""

from hedron_core.testing.adapters import (
    AdapterAppFixture,
    AdapterResponse,
    assert_fragment_body,
    assert_html_contains,
    assert_htmx_trigger,
    assert_hx_push_url,
    assert_hx_redirect,
    assert_hx_reswap,
    assert_hx_retarget,
    assert_oob_present,
    assert_page_document,
    assert_toast_markup,
    django_fixture,
    fastapi_fixture,
    flask_fixture,
)

__all__ = [
    "AdapterAppFixture",
    "AdapterResponse",
    "assert_fragment_body",
    "assert_html_contains",
    "assert_htmx_trigger",
    "assert_hx_push_url",
    "assert_hx_redirect",
    "assert_hx_reswap",
    "assert_hx_retarget",
    "assert_oob_present",
    "assert_page_document",
    "assert_toast_markup",
    "django_fixture",
    "fastapi_fixture",
    "flask_fixture",
]
