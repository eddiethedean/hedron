"""#273: is_local_path must reject raw absolute URLs in the query."""

from __future__ import annotations

from hedron_core.htmx_contract import is_local_path


def test_raw_query_absolute_url_is_rejected() -> None:
    assert is_local_path("/r?next=https://evil.com") is False
    assert is_local_path("/r?next=https%3A%2F%2Fevil.com") is False
    assert is_local_path("/ok/path") is True
