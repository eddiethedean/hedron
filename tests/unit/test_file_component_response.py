"""FileComponentResponse Content-Disposition filename sanitization."""

from __future__ import annotations

from hedron.responses import FileComponentResponse, _safe_content_disposition_filename


def test_safe_filename_rejects_path_and_header_injection() -> None:
    # Backslashes / path segments fail closed to a generic download name.
    assert _safe_content_disposition_filename('evil\r\nSet-Cookie: a=b";x\\y.txt') == "download"
    assert _safe_content_disposition_filename("../secret.txt") == "download"
    assert _safe_content_disposition_filename("/etc/passwd") == "download"


def test_safe_filename_empty_becomes_download() -> None:
    assert _safe_content_disposition_filename("") == "download"
    # Whitespace / punctuation-only names collapse via upload sanitizer.
    assert _safe_content_disposition_filename("   ") == "_"
    assert _safe_content_disposition_filename('\r\n"') == "_"


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
    assert 'filename="report_X_1_.csv"' in cd
