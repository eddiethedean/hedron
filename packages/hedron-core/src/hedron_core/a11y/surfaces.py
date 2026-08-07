"""Surface helpers for INTERACT / MEDIA / COG / I18N packets."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

__all__ = [
    "CognitivePreferences",
    "MediaTrackContract",
    "StructureReport",
    "TargetSpacingPolicy",
    "validate_page_structure",
]


@dataclass(frozen=True, slots=True)
class TargetSpacingPolicy:
    """WCAG 2.2 target size / spacing guidance (CSS pixels)."""

    min_target_css_px: int = 24
    allow_spacing_exception: bool = True
    notes: str = "24x24 CSS px or equivalent spacing; document exceptions"


@dataclass(frozen=True, slots=True)
class MediaTrackContract:
    """Caption / transcript / audio-description obligations for media."""

    kind: Literal[
        "captions", "subtitles", "transcript", "audio_description", "descriptive_transcript"
    ]
    language: str
    src: str | None = None
    reviewed: bool = False

    def validated(self) -> MediaTrackContract:
        if not self.language.strip():
            raise ValueError("Media track requires language")
        if self.kind in {"captions", "subtitles", "audio_description"} and not self.src:
            raise ValueError(f"{self.kind} requires src")
        return self


@dataclass(frozen=True, slots=True)
class CognitivePreferences:
    """Authoring helpers for cognitive / personalization controls."""

    reduced_motion: bool = False
    density: Literal["comfortable", "compact"] = "comfortable"
    text_spacing: bool = False
    notification_intensity: Literal["low", "medium", "high"] = "medium"
    auto_update: bool = False
    help_slot: str | None = None
    glossary_slot: str | None = None
    simplified_presentation: bool = False

    def judges_prose_clarity(self) -> bool:
        return False


@dataclass
class StructureReport:
    title: str | None = None
    lang: str | None = None
    dir: str | None = None
    landmarks: list[str] = field(default_factory=list)
    headings: list[str] = field(default_factory=list)
    has_skip_link: bool = False
    issues: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.issues


_TITLE = re.compile(r"<title>([^<]*)</title>", re.I)
_LANG = re.compile(r"<html[^>]*\blang=(['\"])(.*?)\1", re.I)
_DIR = re.compile(r"<html[^>]*\bdir=(['\"])(.*?)\1", re.I)
_LANDMARK = re.compile(
    r"<(header|main|nav|aside|footer)(\s|>)|"
    r"<section\b([^>]*)>",
    re.I,
)
_SECTION_NAMED = re.compile(
    r"\b(aria-label|aria-labelledby|title)\s*=",
    re.I,
)
_HEADING = re.compile(r"<h([1-6])\b", re.I)
_SKIP = re.compile(r'href=["\']#[^"\']*["\'][^>]*>\s*skip', re.I)


def validate_page_structure(html: str) -> StructureReport:
    report = StructureReport()
    title_m = _TITLE.search(html)
    report.title = title_m.group(1).strip() if title_m else None
    lang_m = _LANG.search(html)
    report.lang = lang_m.group(2) if lang_m else None
    dir_m = _DIR.search(html)
    report.dir = dir_m.group(2) if dir_m else None
    landmarks: list[str] = []
    for m in _LANDMARK.finditer(html):
        if m.group(1):
            landmarks.append(m.group(1).lower())
            continue
        section_attrs = m.group(3) or ""
        if _SECTION_NAMED.search(section_attrs):
            landmarks.append("section")
    report.landmarks = landmarks
    report.headings = [f"h{m.group(1)}" for m in _HEADING.finditer(html)]
    report.has_skip_link = bool(_SKIP.search(html))
    if not report.title:
        report.issues.append("missing document title")
    if not report.lang:
        report.issues.append("missing html lang")
    if "main" not in report.landmarks:
        report.issues.append("missing main landmark")
    if not report.has_skip_link:
        report.issues.append("missing skip link")
    return report
