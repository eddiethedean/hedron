"""VALIDITY-037: directory upload NUL rejection and SelectSlider value."""

from __future__ import annotations

import re

import pytest

from hedron_core.builtins.forms_extra import SelectSlider, validate_directory_upload
from hedron_core.rendering import render


def test_select_slider_hidden_input_uses_value_not_index() -> None:
    html = render(SelectSlider("level", [("low", "Low"), ("high", "High")], value="high")).html
    match = re.search(r'type="hidden"[^>]*value="([^"]*)"', html)
    assert match is not None
    assert match.group(1) == "high"


def test_validate_directory_upload_rejects_nul_in_path() -> None:
    with pytest.raises(ValueError, match="Unsafe directory upload path"):
        validate_directory_upload([("safe\x00evil.txt", 1)], max_files=10, max_total_size=100)
