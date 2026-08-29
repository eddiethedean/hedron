"""Bounded, non-executing phase 0.63 static checks."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import TypedDict

from hedron_core.codes import (
    HED_CHECK_0001,
    HED_CHECK_0002,
    HED_CHECK_0003,
    HED_CHECK_0004,
    HED_CHECK_0005,
    HED_CHECK_0006,
)
from hedron_core.compat import tomllib
from hedron_core.typing_aliases import is_object_list, is_string_mapping

SCHEMA = "hedron.interaction-checks/1"
MAX_FILES = 1_000
MAX_BYTES = 512 * 1024
_SKIP = frozenset({".git", ".venv", "node_modules", "dist", "build", "site", "__pycache__"})
_RULES: tuple[tuple[str, str, str, str], ...] = (
    (HED_CHECK_0001, "error", "application-css", r"\.(css|scss|sass|less)$"),
    (HED_CHECK_0002, "error", "unsafe-css-url", r"url\(\s*['\"]?(https?:|//|\.\.)"),
    (HED_CHECK_0003, "error", "callback-execution", r"\b(eval|exec|Function)\s*\("),
    (
        HED_CHECK_0004,
        "warning",
        "unbounded-client-runtime",
        r"\b(WebSocket|setInterval|localStorage)\b",
    ),
    (HED_CHECK_0005, "warning", "raw-html-sink", r"\b(dangerouslySetInnerHTML|innerHTML)\b"),
    (HED_CHECK_0006, "warning", "inline-style", r"\bstyle\s*=\s*['\"]"),
)


class _SpanCoordinates(TypedDict):
    start_line: int
    start_column: int


class FindingSpan(_SpanCoordinates):
    path: str


class Phase063Finding(TypedDict):
    code: str
    severity: str
    kind: str
    message: str
    span: FindingSpan
    evidence: str
    suppressed: bool


class _AnalysisBase(TypedDict):
    schema: str
    non_executing: bool
    limits: dict[str, int]
    files_scanned: int
    bytes_scanned: int
    suppressions: list[str]
    findings: list[Phase063Finding]


class Phase063Analysis(_AnalysisBase):
    digest: str


def _span(text: str, offset: int) -> _SpanCoordinates:
    line = text.count("\n", 0, offset) + 1
    previous = text.rfind("\n", 0, offset)
    return {"start_line": line, "start_column": offset - previous}


def _suppressed(root: Path) -> set[str]:
    path = root / ".hedron" / "phase063-suppressions.toml"
    if not path.is_file():
        return set()
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return set()
    rows: object = data.get("suppressions", [])
    if not is_object_list(rows):
        return set()
    result: set[str] = set()
    for row in rows:
        if (
            is_string_mapping(row)
            and str(row.get("code", "")).startswith("HED-CHECK-")
            and str(row.get("justification", "")).strip()
        ):
            result.add(str(row["code"]))
    return result


def analyze_project(root: Path) -> Phase063Analysis:
    """Scan source text only; never import or execute the project."""

    root = root.resolve()
    files = [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and not path.is_symlink()
        and not any(part in _SKIP for part in path.parts)
    ]
    if len(files) > MAX_FILES:
        files = files[:MAX_FILES]
    suppressions = _suppressed(root)
    findings: list[Phase063Finding] = []
    bytes_seen = 0
    for path in files:
        if path.stat().st_size > MAX_BYTES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        bytes_seen += len(text.encode("utf-8"))
        relative = str(path.relative_to(root))
        for code, severity, kind, pattern in _RULES:
            matches = list(
                re.finditer(pattern, relative if kind == "application-css" else text, re.I)
            )
            for match in matches[:20]:
                if code in suppressions and not code.startswith("HED-SEC-"):
                    continue
                source_text = relative if kind == "application-css" else text
                location: FindingSpan = {
                    "path": relative,
                    **_span(source_text, match.start()),
                }
                findings.append(
                    {
                        "code": code,
                        "severity": severity,
                        "kind": kind,
                        "message": f"{kind} pattern detected",
                        "span": location,
                        "evidence": match.group(0)[:80],
                        "suppressed": False,
                    }
                )
    findings.sort(key=lambda item: (item["span"]["path"], item["span"]["start_line"], item["code"]))
    payload: _AnalysisBase = {
        "schema": SCHEMA,
        "non_executing": True,
        "limits": {"max_files": MAX_FILES, "max_bytes_per_file": MAX_BYTES},
        "files_scanned": len(files),
        "bytes_scanned": bytes_seen,
        "suppressions": sorted(suppressions),
        "findings": findings,
    }
    digest = hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()
    return {**payload, "digest": digest}


__all__ = ["SCHEMA", "analyze_project"]
