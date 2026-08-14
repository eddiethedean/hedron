"""REGRESS-039 media download / range streaming (#104, #221)."""

from __future__ import annotations

import asyncio
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
from starlette.responses import StreamingResponse

from hedron.builtins import media as media_mod
from hedron.builtins.media import download_all_zip, media_file_response


def test_039_download_all_zip_unique_arcnames(tmp_path: Path) -> None:
    root = tmp_path / "media"
    a = root / "a"
    b = root / "b"
    a.mkdir(parents=True)
    b.mkdir(parents=True)
    (a / "same.txt").write_bytes(b"first")
    (b / "same.txt").write_bytes(b"second")

    resp = download_all_zip(
        [a / "same.txt", b / "same.txt"],
        root=root,
        authorized=True,
        max_total_bytes=1000,
    )
    with zipfile.ZipFile(BytesIO(resp.body)) as zf:
        names = zf.namelist()
    assert names == ["a/same.txt", "b/same.txt"]
    assert len(set(names)) == 2


def test_039_media_range_streams_without_full_buffer(tmp_path: Path) -> None:
    root = tmp_path / "media"
    root.mkdir()
    target = root / "clip.bin"
    target.write_bytes(b"0123456789" * 100)

    with patch.object(media_mod, "_iter_file_range", wraps=media_mod._iter_file_range) as mocked:
        resp = media_file_response(
            target,
            root=root,
            filename="clip.bin",
            authorized=True,
            range_header="bytes=0-99",
            max_range_bytes=10_000,
        )
        assert isinstance(resp, StreamingResponse)
        assert resp.status_code == 206

        async def _read() -> bytes:
            chunks: list[bytes] = []
            async for chunk in resp.body_iterator:
                chunks.append(chunk)
            return b"".join(chunks)

        body = asyncio.run(_read())
        assert body == (b"0123456789" * 100)[:100]
        assert mocked.called


def test_039_media_range_rejects_oversized_span(tmp_path: Path) -> None:
    root = tmp_path / "media"
    root.mkdir()
    target = root / "clip.bin"
    target.write_bytes(b"x" * 1000)
    with pytest.raises(ValueError, match="max_range_bytes"):
        media_file_response(
            target,
            root=root,
            filename="clip.bin",
            authorized=True,
            range_header="bytes=0-",
            max_range_bytes=100,
        )
