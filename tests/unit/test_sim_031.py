"""SIM-031 unit coverage: declared HTMX subset and loud failures."""

from __future__ import annotations

import pytest

from hedron_sim import (
    DECLARED_HX_METHODS,
    UnsupportedSimFeatureError,
    require_supported_method,
    require_supported_swap,
    subset_policy_markdown,
)


def test_subset_policy_lists_methods() -> None:
    text = subset_policy_markdown()
    assert "GET" in text
    assert "UnsupportedSimFeatureError" in text
    assert "GET" in DECLARED_HX_METHODS


def test_require_supported_method_and_swap() -> None:
    assert require_supported_method("post") == "POST"
    assert require_supported_swap("beforeend") == "beforeend"
    with pytest.raises(UnsupportedSimFeatureError):
        require_supported_method("TRACE")
    with pytest.raises(UnsupportedSimFeatureError):
        require_supported_swap("morphdom")
