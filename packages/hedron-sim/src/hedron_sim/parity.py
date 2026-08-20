"""Differential parity between simulated HTML and real Hedron HTTP responses.

Parity is intentionally shallow: only trivial whitespace and the simulator's own
placeholder tokens are normalized. Anything else that differs is reported so a
divergence is a visible failure rather than a silent approximation.
"""

from __future__ import annotations

import difflib
import re
from typing import Any

from hedron_sim.tokens import SIM_LOCAL_TIME, SIM_UTC

__all__ = [
    "PARITY_FIXTURES",
    "PARITY_SCHEMA",
    "compare_parity",
    "normalize_parity_html",
]

PARITY_SCHEMA = "hedron-sim-parity-1"

# Fixture families required by PARITY-054 (authoring-sim-notebook-054.toml).
PARITY_FIXTURES: tuple[str, ...] = (
    "package_workflows",
    "validation_failures",
    "navigation",
    "asset_lifecycle",
)

_MAX_DIFFERENCES = 20

_BETWEEN_TAGS = re.compile(r">\s+<")
_WHITESPACE = re.compile(r"\s+")
_TOKEN = re.compile(r"__HEDRON_SIM_FORM:[A-Za-z0-9_-]+__")
_PLACEHOLDER = "{sim-placeholder}"
_CHUNK = re.compile(r"<[^>]+>|[^<]+")


def normalize_parity_html(html: str, *, placeholders: bool = True) -> str:
    """Collapse trivial whitespace so equivalent markup compares equal."""
    text = _WHITESPACE.sub(" ", html.strip())
    text = _BETWEEN_TAGS.sub("><", text)
    if placeholders:
        text = _TOKEN.sub(_PLACEHOLDER, text)
        text = text.replace(SIM_UTC, _PLACEHOLDER).replace(SIM_LOCAL_TIME, _PLACEHOLDER)
    return text


def _chunks(html: str) -> list[str]:
    return [chunk for chunk in (part.strip() for part in _CHUNK.findall(html)) if chunk]


def compare_parity(
    sim_html: str,
    server_html: str,
    *,
    fixture: str | None = None,
    placeholders: bool = True,
) -> dict[str, Any]:
    """Compare simulated and real-server HTML.

    Both documents are split into tag and text chunks with each chunk's own
    whitespace trimmed, so indentation and line breaks never register as a
    difference. Returns ``{"ok": bool, "differences": [...]}`` plus the fixture
    label and schema version. Each difference names the operation (``replace``,
    ``insert``, ``delete``) with the simulated and server chunks at that position.
    """
    sim_chunks = _chunks(normalize_parity_html(sim_html, placeholders=placeholders))
    server_chunks = _chunks(normalize_parity_html(server_html, placeholders=placeholders))
    differences: list[dict[str, Any]] = []
    if sim_chunks != server_chunks:
        matcher = difflib.SequenceMatcher(a=sim_chunks, b=server_chunks, autojunk=False)
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == "equal":
                continue
            differences.append(
                {
                    "op": op,
                    "index": i1,
                    "sim": " ".join(sim_chunks[i1:i2]),
                    "server": " ".join(server_chunks[j1:j2]),
                }
            )
            if len(differences) >= _MAX_DIFFERENCES:
                break
    return {
        "schema_version": PARITY_SCHEMA,
        "fixture": fixture,
        "ok": not differences,
        "differences": differences,
    }
