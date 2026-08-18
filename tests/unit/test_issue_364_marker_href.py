"""#364: compile_map validates marker href instead of crashing at render."""

from __future__ import annotations

import pytest

from hedron_core import HedronError
from hedron_maps import Map


def test_unsafe_marker_href_fails_at_compile() -> None:
    with pytest.raises(HedronError):
        Map(
            title="T",
            description="D",
            markers=[
                {
                    "id": "a",
                    "lat": 1,
                    "lon": 2,
                    "label": "A",
                    "href": "javascript:alert(1)",
                }
            ],
        ).compile_plan()
