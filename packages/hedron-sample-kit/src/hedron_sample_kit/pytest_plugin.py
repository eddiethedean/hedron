"""Explicit pytest fixture contribution for the sample-kit browser example."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_kit_app_factory() -> str:
    """Return the example app factory path declared by the sample-kit contribution."""
    return "hedron_sample_kit.ui_testing:create_app"


__all__ = ["sample_kit_app_factory"]
