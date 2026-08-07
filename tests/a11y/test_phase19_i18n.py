"""Phase 0.19 I18N-019."""

from __future__ import annotations

from hedron_core import Main, Page, Text, render
from hedron_core.a11y import validate_page_structure


def test_page_structure_lang_dir_and_main() -> None:
    html = render(Page(Main(Text("مرحبا")), title="Hello", lang="ar", dir="rtl")).html
    report = validate_page_structure(html)
    assert report.lang == "ar"
    assert report.dir == "rtl"
    assert report.title == "Hello"
    assert "main" in report.landmarks
    assert report.ok or "missing main landmark" not in report.issues


def test_structure_flags_missing_title() -> None:
    report = validate_page_structure("<html lang='en'><body><main>x</main></body></html>")
    assert "missing document title" in report.issues
