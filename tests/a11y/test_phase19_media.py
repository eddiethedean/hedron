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


def test_audio_tracks_require_language_via_media_contract() -> None:
    from hedron_core import Audio, render
    from hedron_core.security import SafeUrl, UrlPurpose

    src = SafeUrl.parse("/media/a.mp3", purpose=UrlPurpose.ASSET)
    html = render(
        Audio(src, tracks=[{"src": "/media/captions.vtt", "kind": "captions", "srclang": "en"}])
    ).html
    assert "<track" in html
    with pytest.raises(ValueError, match="language|src"):
        render(Audio(src, tracks=[{"src": "/media/captions.vtt", "kind": "captions"}]))


def test_chart_accessibility_still_requires_alt_or_waiver() -> None:
    ChartAccessibility(title="Sales", alt="Bar chart of sales").validated()
    with pytest.raises(ValueError):
        ChartAccessibility(title="Sales").validated()
