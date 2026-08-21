"""Public HTML normalization rules for conformance comparisons."""

from __future__ import annotations

import re

_WS_BETWEEN_TAGS = re.compile(r">\s+<")
_MULTI_SPACE = re.compile(r"[ \t\r\n]+")


def normalize_html(html: str) -> str:
    """Normalize incidental formatting without hiding semantic differences.

    Rules (html-v1):
    - Strip leading/trailing whitespace.
    - Collapse whitespace between tags to nothing.
    - Collapse runs of whitespace inside text to a single space (text nodes only
      when already escaped — callers compare escaped goldens).
    - Lowercase tag names are assumed already produced by the reference serializer.
    - Attribute order is fixed by the reference ATTR_ORDER contract; do not reorder here.
    """
    text = html.strip()
    # Do not collapse spaces inside attribute values or text content aggressively
    # beyond tag boundaries — goldens are already deterministic.
    return _WS_BETWEEN_TAGS.sub("><", text)


def normalize_identity(value: str) -> str:
    return value.strip()


def normalize_diagnostic_code(code: str) -> str:
    return code.strip().upper()
