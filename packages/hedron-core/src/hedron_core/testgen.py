"""Deterministic reviewable interaction-test generation from sealed catalogs.

TESTGEN-053 / RFC-0080: emit pytest source from a sealed ``InteractionCatalog``
(or duck-typed object with ``entries`` / ``fingerprint``). Catalog fields are
never ``eval``/``exec``'d — only redacted string literals are embedded.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, Protocol

__all__ = [
    "GENERATOR_VERSION",
    "PATHS",
    "generate_interaction_tests",
]

GENERATOR_VERSION = "1.0.0"

PATHS: tuple[str, ...] = ("page", "htmx", "mounted", "error")

_PATH_PREFERRED_KINDS: Mapping[str, tuple[str, ...]] = {
    "page": ("view",),
    "htmx": ("view", "command"),
    "mounted": ("view",),
    "error": ("command", "view"),
}

_IDENT_RE = re.compile(r"[^0-9a-zA-Z_]+")


class _CatalogLike(Protocol):
    @property
    def entries(self) -> Mapping[str, Any]: ...

    @property
    def fingerprint(self) -> str: ...


def _redact_literal(value: object) -> str:
    """Embed ``value`` as a Python string literal; never treat it as code."""
    text = "" if value is None else str(value)
    cleaned = "".join(ch for ch in text if ch >= " " and ch != "\x7f")
    return repr(cleaned)


def _docstring(text: str) -> str:
    """Return a single-line docstring using a redacted literal body."""
    body = _redact_literal(text)[1:-1]
    return f'"""{body}"""'


def _safe_ident(*parts: str) -> str:
    joined = "_".join(parts)
    ident = _IDENT_RE.sub("_", joined).strip("_").lower()
    if not ident:
        ident = "entry"
    if ident[0].isdigit():
        ident = f"id_{ident}"
    return ident[:80]


def _entry_kind(entry: object) -> str:
    kind = getattr(entry, "kind", None)
    if isinstance(kind, str) and kind:
        return kind
    if isinstance(entry, Mapping):
        raw = entry.get("kind")
        if isinstance(raw, str) and raw:
            return raw
    return ""


def _entry_logical_id(entry: object, fallback: str) -> str:
    logical_id = getattr(entry, "logical_id", None)
    if isinstance(logical_id, str) and logical_id:
        return logical_id
    if isinstance(entry, Mapping):
        raw = entry.get("logical_id")
        if isinstance(raw, str) and raw:
            return raw
    return fallback


def _entry_descriptor_fp(entry: object) -> str:
    fp = getattr(entry, "descriptor_fingerprint", None)
    if isinstance(fp, str) and fp:
        return fp
    if isinstance(entry, Mapping):
        raw = entry.get("descriptor_fingerprint")
        if isinstance(raw, str) and raw:
            return raw
    return ""


def _sorted_entries(catalog: _CatalogLike) -> list[tuple[str, object]]:
    entries = getattr(catalog, "entries", None) or {}
    if not isinstance(entries, Mapping):
        return []
    return sorted(entries.items(), key=lambda item: item[0])


def _select_entries_for_path(
    path: str,
    entries: Sequence[tuple[str, object]],
) -> list[tuple[str, object]]:
    preferred = _PATH_PREFERRED_KINDS.get(path, ())
    matched = [(key, entry) for key, entry in entries if _entry_kind(entry) in preferred]
    if matched:
        return matched
    return list(entries)


def generate_interaction_tests(
    catalog: _CatalogLike,
    *,
    profile: str = "default",
    generator_version: str = GENERATOR_VERSION,
) -> str:
    """Return deterministic pytest source for page/HTMX/mount/error stubs.

    Determinism inputs: catalog fingerprint, ``profile``, and
    ``generator_version``. Output is reviewable source only — never executes
    catalog fields.
    """
    fingerprint = str(getattr(catalog, "fingerprint", "") or "")
    fp_lit = _redact_literal(fingerprint)
    profile_lit = _redact_literal(profile)
    version_lit = _redact_literal(generator_version)
    entries = _sorted_entries(catalog)

    lines: list[str] = [
        f'"""Generated interaction tests (hedron testgen {generator_version}).',
        "",
        f"Catalog fingerprint: {fp_lit}",
        f"Profile: {profile_lit}",
        f"Generator version: {version_lit}",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        f"CATALOG_FINGERPRINT = {fp_lit}",
        f"GENERATOR_VERSION = {version_lit}",
        f"PROFILE = {profile_lit}",
        "",
    ]

    if not entries:
        for path in PATHS:
            name = _safe_ident("placeholder", path)
            lines.append(f"def test_{name}() -> None:")
            lines.append(f"    {_docstring(f'Placeholder {path} path; catalog has no entries.')}")
            lines.append(f"    assert CATALOG_FINGERPRINT == {fp_lit}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    emitted: set[str] = set()
    for path in PATHS:
        for key, entry in _select_entries_for_path(path, entries):
            logical_id = _entry_logical_id(entry, key)
            kind = _entry_kind(entry) or "unknown"
            desc_fp = _entry_descriptor_fp(entry)
            fn = _safe_ident(path, kind, logical_id)
            if fn in emitted:
                fn = _safe_ident(path, kind, logical_id, "dup", key)
            emitted.add(fn)
            lines.append(f"def test_{fn}() -> None:")
            lines.append(f"    {_docstring(f'Stub {path} path for {kind} {logical_id}.')}")
            lines.append(f"    assert CATALOG_FINGERPRINT == {fp_lit}")
            lines.append(f"    logical_id = {_redact_literal(logical_id)}")
            lines.append(f"    kind = {_redact_literal(kind)}")
            if desc_fp:
                lines.append(f"    descriptor_fingerprint = {_redact_literal(desc_fp)}")
            lines.append(f"    path = {_redact_literal(path)}")
            lines.append(f"    assert logical_id == {_redact_literal(logical_id)}")
            lines.append(f"    assert path == {_redact_literal(path)}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
