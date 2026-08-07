"""Phase 0.19 I18N-019."""

from __future__ import annotations

from hedron_core import Main, Page, Text, render
from hedron_core.a11y import validate_page_structure
from hedron_core.html import html
from hedron_core.security import SafeUrl, UrlPurpose


def test_page_structure_lang_dir_and_main() -> None:
    page = Page(
        html.a("Skip to content", href=SafeUrl.parse("#main", purpose=UrlPurpose.NAVIGATION)),
        Main(Text("مرحبا"), id="main"),
        title="Hello",
        lang="ar",
        dir="rtl",
    )
    report = validate_page_structure(render(page).html)
    assert report.lang == "ar"
    assert report.dir == "rtl"
    assert report.title == "Hello"
    assert "main" in report.landmarks
    assert report.has_skip_link
    assert report.ok


def test_structure_flags_missing_title() -> None:
    report = validate_page_structure(
        "<html lang='en'><body><a href='#main'>Skip</a><main>x</main></body></html>"
    )
    assert "missing document title" in report.issues
    assert report.lang == "en"


def test_structure_accepts_single_quoted_lang_dir() -> None:
    report = validate_page_structure(
        "<html lang='fr' dir='ltr'><head><title>T</title></head>"
        "<body><a href='#main'>Skip</a><main>x</main></body></html>"
    )
    assert report.lang == "fr"
    assert report.dir == "ltr"
    assert report.ok


def test_structure_flags_missing_skip_link() -> None:
    report = validate_page_structure(
        "<html lang='en'><head><title>T</title></head><body><main>x</main></body></html>"
    )
    assert "missing skip link" in report.issues
    assert not report.ok


def test_section_landmark_requires_name() -> None:
    bare = validate_page_structure(
        "<html lang='en'><head><title>T</title></head>"
        "<body><a href='#main'>Skip</a><main><section>x</section></main></body></html>"
    )
    assert "section" not in bare.landmarks
    named = validate_page_structure(
        "<html lang='en'><head><title>T</title></head>"
        "<body><a href='#main'>Skip</a><main>"
        "<section aria-label='Intro'>x</section></main></body></html>"
    )
    assert "section" in named.landmarks
