"""Redirect containment used by the licensed Connect smoke harness."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "check_same_origin_redirect", ROOT / "scripts" / "check_same_origin_redirect.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
safe_redirect_target = MODULE.safe_redirect_target


@pytest.mark.parametrize(
    ("location", "expected"),
    [
        (
            "/content/abc/login",
            "http://127.0.0.1:3939/content/abc/login",
        ),
        (
            "http://127.0.0.1:3939/content/abc/https:/evil.example",
            "http://127.0.0.1:3939/content/abc/https:/evil.example",
        ),
    ],
)
def test_safe_redirect_target_accepts_same_origin_mounted_paths(
    location: str, expected: str
) -> None:
    assert (
        safe_redirect_target(
            origin="http://127.0.0.1:3939",
            mount="/content/abc",
            location=location,
        )
        == expected
    )


@pytest.mark.parametrize(
    "location",
    [
        "https://evil.example/content/abc/login",
        "//evil.example/content/abc/login",
        "/admin",
        "/content/other/login",
        "/content/abc/%2e%2e/admin",
        "/content/abc/%252e%252e/admin",
        "/content/abc/https%3A%2F%2Fevil.example",
        "http://user:pass@127.0.0.1:3939/content/abc/login",
    ],
)
def test_safe_redirect_target_rejects_origin_and_mount_escapes(location: str) -> None:
    with pytest.raises(ValueError):
        safe_redirect_target(
            origin="http://127.0.0.1:3939",
            mount="/content/abc",
            location=location,
        )
