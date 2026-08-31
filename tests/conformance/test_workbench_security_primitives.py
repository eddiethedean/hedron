"""Data-only adversarial corpus for duplicated Workbench security primitives."""

from __future__ import annotations

import pytest

from fastapi_workbench.mount import (
    is_local_path as generic_is_local_path,
)
from fastapi_workbench.mount import (
    normalize_mount_path as generic_normalize_mount,
)
from fastapi_workbench.mount import (
    path_has_mount_prefix as generic_has_prefix,
)
from fastapi_workbench.mount import (
    prefix_local_path as generic_prefix,
)
from fastapi_workbench.urls import normalize_http_origin as generic_normalize_origin
from hedron_core.htmx_contract import is_local_path as core_is_local_path
from hedron_core.mount import (
    normalize_mount_path as core_normalize_mount,
)
from hedron_core.mount import (
    path_has_mount_prefix as core_has_prefix,
)
from hedron_core.mount import (
    prefix_local_path as core_prefix,
)
from hedron_posit.urls import normalize_http_origin as posit_normalize_origin

ORIGIN_CASES = (
    ("HTTPS://Example.COM:443/", "https://example.com"),
    ("http://127.0.0.1:80", "http://127.0.0.1"),
    ("https://[2001:0db8::1]:8443", "https://[2001:db8::1]:8443"),
    ("https://BÜCHER.example", "https://xn--bcher-kva.example"),
)

INVALID_ORIGINS = (
    "//evil.example",
    "https://user:password@example.com",
    "https://example.com/path",
    "https://example.com?token=x",
    "https://example.com\\@evil.example",
    "https://-bad.example",
    "https://example..com",
    "https://[::1",
    "javascript://example.com",
)

MOUNT_CASES = (
    (None, ""),
    ("/", ""),
    ("apps/demo/", "/apps/demo"),
    ("/s/a/p/1", "/s/a/p/1"),
    ("/café", ""),
    ("/caf%C3%A9", "/caf%C3%A9"),
    ("/safe/%252e%252e/admin", ""),
    ("/safe/%2E/admin", ""),
    ("/safe/../admin", ""),
    ("//evil.example", ""),
    ("/cookie;Domain=evil", ""),
    ('/cookie"quoted', ""),
    ("/with?query", ""),
)

LOCAL_PATH_CASES = (
    ("/app", True),
    ("/app/child?tab=1#main", True),
    ("//evil.example", False),
    ("/%252e%252e/admin", False),
    ("/safe\\evil", False),
    ("https://evil.example", False),
)


@pytest.mark.parametrize(("raw", "expected"), ORIGIN_CASES)
def test_origin_canonicalization_conforms(raw: str, expected: str) -> None:
    assert generic_normalize_origin(raw) == expected
    assert posit_normalize_origin(raw) == expected


@pytest.mark.parametrize("raw", INVALID_ORIGINS)
def test_invalid_origins_are_rejected_by_both_implementations(raw: str) -> None:
    with pytest.raises(ValueError):
        generic_normalize_origin(raw)
    with pytest.raises(ValueError):
        posit_normalize_origin(raw)


@pytest.mark.parametrize(("raw", "expected"), MOUNT_CASES)
def test_mount_normalization_and_header_encodability_conform(
    raw: str | None, expected: str
) -> None:
    assert generic_normalize_mount(raw) == expected
    assert core_normalize_mount(raw) == expected
    expected.encode("latin-1")


@pytest.mark.parametrize(("path", "expected"), LOCAL_PATH_CASES)
def test_local_path_policy_conforms(path: str, expected: bool) -> None:
    assert generic_is_local_path(path) is expected
    assert core_is_local_path(path) is expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/app", True),
        ("/app/child?next=/app2#main", True),
        ("/app2", False),
        ("/application", False),
        ("/app-elsewhere", False),
    ],
)
def test_prefix_boundary_policy_conforms(path: str, expected: bool) -> None:
    assert generic_has_prefix(path, "/app") is expected
    assert core_has_prefix(path, "/app") is expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/", "/app/"),
        ("/profile?tab=1#main", "/app/profile?tab=1#main"),
        ("/app/profile", "/app/profile"),
        ("/app2/profile", "/app/app2/profile"),
        ("//evil.example", "//evil.example"),
        ("/%252e%252e/admin", "/%252e%252e/admin"),
    ],
)
def test_prefix_idempotence_and_rejection_conform(path: str, expected: str) -> None:
    assert generic_prefix(path, "/app") == expected
    assert core_prefix(path, "/app") == expected
