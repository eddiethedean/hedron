"""Phase 0.16 image tools and editor extras."""

from __future__ import annotations

import pytest

from hedron.testing import assert_renders
from hedron_extras.editors import Calendar, SignaturePad, Typeahead
from hedron_extras.image_tools import ImageAnnotations, ImageCompare, ImageCrop, ImageRegionSelect


def test_image_compare_crop_region_annotations() -> None:
    assert_renders(
        ImageCompare("/a.png", "/b.png", orientation="vertical"),
        contains="hedron-image-compare",
    )
    assert_renders(
        ImageCrop("/a.png", shape="circle", width=0.5, height=0.5),
        contains="hedron-image-crop",
    )
    assert_renders(
        ImageRegionSelect("/a.png", regions=[{"kind": "box", "points": [[0.1, 0.1], [0.2, 0.2]]}]),
        contains="hedron-image-region",
    )
    assert_renders(
        ImageAnnotations("/a.png", [{"label": "spot", "x": 0.2, "y": 0.3}]),
        contains="hedron-image-annotations",
    )
    with pytest.raises(ValueError):
        ImageCompare("javascript:alert(1)", "/b.png")


def test_calendar_signature_typeahead() -> None:
    assert_renders(Calendar(value="2026-08-06"), contains="hedron-calendar")
    assert_renders(SignaturePad(max_bytes=10_000), contains="hedron-signature-pad")
    html = assert_renders(
        Typeahead("city", ["Austin", "Boston"], value="Austin"),
        contains="hedron-typeahead",
    )
    assert 'role="combobox"' in html
