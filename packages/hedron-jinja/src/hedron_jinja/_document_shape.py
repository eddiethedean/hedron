"""Document-shape checks and policy fingerprinting for HDJ page renders."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from html.parser import HTMLParser
from typing import Any, cast

_PAGE_DOCTYPE_RE = re.compile(r"^\s*<!doctype\s+html\b", re.IGNORECASE)


def valid_page_shape(rendered: str) -> bool:
    """Return True when rendered HTML has doctype plus html/head/body skeleton tokens."""
    return _PAGE_DOCTYPE_RE.search(rendered) is not None and document_tokens(rendered) == (
        "html",
        "head",
        "/head",
        "body",
        "/body",
        "/html",
    )


class _DocumentShapeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.tokens: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        lowered = tag.lower()
        if lowered in {"html", "head", "body"}:
            self.tokens.append(lowered)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered in {"html", "head", "body"}:
            self.tokens.append(f"/{lowered}")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)


def document_tokens(rendered: str) -> tuple[str, ...]:
    """Extract ordered html/head/body open and close tokens from rendered markup."""
    parser = _DocumentShapeParser()
    parser.feed(rendered)
    parser.close()
    return tuple(parser.tokens)


def fingerprint_policy(value: object) -> object:
    """Build a hashable fingerprint of a policy/config value for cache keys."""
    if isinstance(value, Mapping):
        mapping = cast(Mapping[Any, Any], value)
        return tuple(sorted((str(key), fingerprint_policy(item)) for key, item in mapping.items()))
    if isinstance(value, (list, tuple)):
        sequence = cast(Sequence[Any], value)
        return tuple(fingerprint_policy(item) for item in sequence)
    if isinstance(value, (set, frozenset)):
        items = cast(Sequence[Any], list(cast(set[Any] | frozenset[Any], value)))
        return tuple(sorted(repr(fingerprint_policy(item)) for item in items))
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    return (type(value).__qualname__, id(value))
