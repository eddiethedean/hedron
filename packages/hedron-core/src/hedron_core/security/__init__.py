"""Security boundary types: Secret, TrustedHtml, SafeUrl."""

from __future__ import annotations

from hedron_core.security.secrets import Secret, is_secret, redact_value
from hedron_core.security.trusted import TrustedHtml
from hedron_core.security.urls import (
    SafeUrl,
    UrlPurpose,
    check_url_purpose_for_attribute,
    contains_dangerous_scheme,
    reject_asset_path_traversal,
)

__all__ = [
    "SafeUrl",
    "Secret",
    "TrustedHtml",
    "UrlPurpose",
    "check_url_purpose_for_attribute",
    "contains_dangerous_scheme",
    "is_secret",
    "redact_value",
    "reject_asset_path_traversal",
]
