"""Phase 0.19 MEDIA-019."""

from __future__ import annotations

import pytest

from hedron_core.a11y import MediaTrackContract
from hedron_core.visualization import ChartAccessibility


def test_media_track_contract_validation() -> None:
    ok = MediaTrackContract(
        kind="captions", language="en", src="/media/captions.vtt", reviewed=True
    ).validated()
    assert ok.language == "en"
    with pytest.raises(ValueError):
        MediaTrackContract(kind="captions", language="en").validated()
    transcript = MediaTrackContract(kind="transcript", language="en").validated()
    assert transcript.src is None


def test_chart_accessibility_still_requires_alt_or_waiver() -> None:
    ChartAccessibility(title="Sales", alt="Bar chart of sales").validated()
    with pytest.raises(ValueError):
        ChartAccessibility(title="Sales").validated()
