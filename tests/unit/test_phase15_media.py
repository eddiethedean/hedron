"""Phase 0.15 M4 media delivery and players (RFC-0034)."""

from __future__ import annotations

from pathlib import Path

import pytest

from hedron.builtins.media import (
    ByteRangeNotSatisfiable,
    download_all_zip,
    media_file_response,
    parse_byte_range,
)
from hedron_core import (
    Audio,
    Gallery,
    PdfViewer,
    Video,
    render,
)
from hedron_core.security import SafeUrl, UrlPurpose


def test_parse_byte_range_absent_and_suffix() -> None:
    assert parse_byte_range(None, size=100) is None
    assert parse_byte_range("", size=100) is None
    assert parse_byte_range("bytes=0-9", size=100) == (0, 9)
    assert parse_byte_range("bytes=50-", size=100) == (50, 99)
    assert parse_byte_range("bytes=-20", size=100) == (80, 99)
    # Multi-range ignored → full entity
    assert parse_byte_range("bytes=0-1,2-3", size=100) is None


def test_parse_byte_range_unsatisfiable() -> None:
    with pytest.raises(ByteRangeNotSatisfiable):
        parse_byte_range("bytes=200-300", size=100)
    with pytest.raises(ByteRangeNotSatisfiable):
        parse_byte_range("bytes=5-3", size=100)


def test_media_file_response_authz_and_traversal(tmp_path: Path) -> None:
    root = tmp_path / "media"
    root.mkdir()
    target = root / "clip.bin"
    target.write_bytes(b"0123456789")
    outside = tmp_path / "secret.bin"
    outside.write_bytes(b"secret")

    with pytest.raises(PermissionError):
        media_file_response(
            target,
            root=root,
            filename="clip.bin",
            content_type="application/octet-stream",
            authorized=False,
        )
    with pytest.raises(PermissionError):
        media_file_response(
            outside,
            root=root,
            filename="secret.bin",
            content_type="application/octet-stream",
            authorized=True,
        )


def test_media_file_response_206_and_416(tmp_path: Path) -> None:
    root = tmp_path / "media"
    root.mkdir()
    target = root / "clip.bin"
    target.write_bytes(b"0123456789")

    partial = media_file_response(
        target,
        root=root,
        filename="clip.bin",
        content_type="application/octet-stream",
        authorized=True,
        range_header="bytes=2-5",
        disposition="inline",
    )
    assert partial.status_code == 206
    assert partial.headers["content-range"] == "bytes 2-5/10"
    assert partial.headers["cache-control"] == "private, no-store"
    assert partial.body == b"2345"
    assert "inline" in partial.headers["content-disposition"]

    unsat = media_file_response(
        target,
        root=root,
        filename="clip.bin",
        content_type="application/octet-stream",
        authorized=True,
        range_header="bytes=50-60",
    )
    assert unsat.status_code == 416
    assert unsat.headers["content-range"] == "bytes */10"

    full = media_file_response(
        target,
        root=root,
        filename="clip.bin",
        content_type="application/octet-stream",
        authorized=True,
        disposition="attachment",
    )
    assert full.status_code == 200
    assert full.headers["cache-control"] == "private, no-store"
    assert "attachment" in full.headers["content-disposition"]


def test_download_all_budget_reject(tmp_path: Path) -> None:
    root = tmp_path / "media"
    root.mkdir()
    a = root / "a.txt"
    b = root / "b.txt"
    a.write_bytes(b"aaaa")
    b.write_bytes(b"bbbb")

    ok = download_all_zip([a, b], root=root, authorized=True, max_total_bytes=100)
    assert ok.status_code == 200
    assert ok.media_type == "application/zip"
    assert ok.headers["cache-control"] == "private, no-store"

    with pytest.raises(ValueError, match="max_total_bytes"):
        download_all_zip([a, b], root=root, authorized=True, max_total_bytes=4)

    with pytest.raises(PermissionError):
        download_all_zip([a], root=root, authorized=False, max_total_bytes=100)


def test_audio_video_pdf_gallery_render() -> None:
    src = SafeUrl.parse("/media/clip.mp3", purpose=UrlPurpose.ASSET)
    poster = SafeUrl.parse("/media/poster.jpg", purpose=UrlPurpose.ASSET)
    pdf = SafeUrl.parse("/media/doc.pdf", purpose=UrlPurpose.ASSET)
    img = SafeUrl.parse("/media/a.png", purpose=UrlPurpose.ASSET)

    audio_html = render(
        Audio(src, tracks=[{"src": "/media/captions.vtt", "kind": "captions", "srclang": "en"}])
    ).html
    assert "<audio" in audio_html
    assert 'src="/media/clip.mp3"' in audio_html
    assert 'kind="captions"' in audio_html
    assert "controls" in audio_html

    video_html = render(Video(src, poster=poster, controls=True)).html
    assert "<video" in video_html
    assert 'poster="/media/poster.jpg"' in video_html

    pdf_html = render(PdfViewer(pdf, title="Spec")).html
    assert "<object" in pdf_html
    assert 'type="application/pdf"' in pdf_html
    assert "/media/doc.pdf" in pdf_html

    gallery_html = render(
        Gallery(
            [{"src": img, "alt": "A", "caption": "Alpha", "href": "/select/a"}],
            lightbox=True,
            mark="photos",
        )
    ).html
    assert "hedron-gallery" in gallery_html
    assert 'data-hedron-mark="photos"' in gallery_html
    assert "hedron-gallery-lightbox" in gallery_html
    assert 'alt="A"' in gallery_html
