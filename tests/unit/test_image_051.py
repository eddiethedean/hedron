"""IMAGE-051 normalized crop/region/annotation intents."""

from __future__ import annotations

import pytest

from hedron.testing import assert_renders
from hedron_extras.image_tools import ImageAnnotations, ImageCrop, ImageRegionSelect


def test_image_crop_normalized_and_server_confirmed() -> None:
    html = assert_renders(
        ImageCrop("/static/a.png", source_width=800, source_height=600, revision="r1"),
        contains='data-server-confirmed="true"',
    )
    assert "hedron-extras-image-tools" in html
    assert 'data-source-width="800"' in html
    assert 'name="crop__revision"' in html
    with pytest.raises(ValueError, match="normalized"):
        ImageCrop("/static/a.png", x=2.0)


def test_region_and_annotations_bounds() -> None:
    html = assert_renders(
        ImageRegionSelect("/static/a.png", regions=[{"kind": "box", "points": [[0.1, 0.2]]}]),
        contains="server-confirmed",
    )
    assert "hedron-extras-image-tools" in html
    with pytest.raises(ValueError, match="normalized"):
        ImageRegionSelect("/static/a.png", regions=[{"kind": "box", "points": [[2.0, 0.0]]}])
    anns = assert_renders(
        ImageAnnotations("/static/a.png", [{"label": "x", "x": 0.1, "y": 0.2}]),
        contains="server-confirmed",
    )
    assert "x @ (0.10,0.20)" in anns
    with pytest.raises(ValueError, match="budget"):
        ImageAnnotations(
            "/static/a.png",
            [{"label": str(i), "x": 0.0, "y": 0.0} for i in range(501)],
        )
