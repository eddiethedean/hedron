"""Compatibility re-export from hedron_posit.urls."""

from __future__ import annotations

from hedron_posit.urls import (
    ExternalBase,
    browser_mount_from_request,
    compose_external_url,
    connect_external_base_from_request,
    is_ephemeral_workbench_mount,
    local_href,
    mounted_redirect,
    normalize_http_origin,
    validate_external_base_url,
)

__all__ = [
    "ExternalBase",
    "browser_mount_from_request",
    "compose_external_url",
    "connect_external_base_from_request",
    "is_ephemeral_workbench_mount",
    "local_href",
    "mounted_redirect",
    "normalize_http_origin",
    "validate_external_base_url",
]
