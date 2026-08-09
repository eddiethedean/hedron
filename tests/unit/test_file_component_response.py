"""FileComponentResponse Content-Disposition filename sanitization."""

from __future__ import annotations

from hedron.responses import FileComponentResponse, _safe_content_disposition_filename


def test_safe_filename_strips_crlf_quotes_and_backslashes() -> None:
    cleaned = _safe_content_disposition_filename('evil\r\nSet-Cookie: a=b";x\\y.txt')
    assert "\r" not in cleaned
    assert "\n" not in cleaned
    assert '"' not in cleaned
    assert "\\" not in cleaned
    # CRLF removal prevents header injection; remaining text is a single filename token.
    assert cleaned == "evilSet-Cookie: a=b;xy.txt"


def test_safe_filename_empty_becomes_download() -> None:
    assert _safe_content_disposition_filename("") == "download"
    assert _safe_content_disposition_filename("   ") == "download"
    assert _safe_content_disposition_filename('\r\n"') == "download"


def test_safe_filename_truncates_at_200() -> None:
    long_name = "a" * 250 + ".bin"
    cleaned = _safe_content_disposition_filename(long_name)
    assert len(cleaned) == 200


def test_file_component_response_sets_sanitized_disposition() -> None:
    resp = FileComponentResponse(b"payload", filename='report\r\nX: 1".csv')
    cd = resp.headers.get("content-disposition") or resp.headers.get("Content-Disposition")
    assert cd is not None
    assert "\r" not in cd
    assert "\n" not in cd
    assert "attachment;" in cd
    # Exactly one quoted filename= value — no quote breakout.
    assert cd.count('"') == 2
    assert 'filename="reportX: 1.csv"' in cd
