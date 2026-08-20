"""PDIAG-052 evidence."""

from __future__ import annotations

from hedron_posit.diagnostics import (
    scan_location_header,
    scan_set_cookie_headers,
    scan_unregistered_cookies,
)


def test_scan_literal_path_auto_never_includes_cookie_value() -> None:
    diags = scan_set_cookie_headers(
        ["session=super-secret; Path=auto; HttpOnly"],
        mount="/s/abc/p/xyz/",
    )
    assert any(item.code == "HED-POSIT-0512" for item in diags)
    blob = " ".join(item.explanation for item in diags)
    assert "super-secret" not in blob


def test_scan_unmounted_location() -> None:
    diags = scan_location_header("/login", mount="/s/abc/p/xyz")
    assert any(item.code == "HED-POSIT-0514" for item in diags)


def test_scan_unregistered_cookie_names() -> None:
    diags = scan_unregistered_cookies(["rogue"], registered=("session",))
    assert any(item.code == "HED-POSIT-0516" for item in diags)
