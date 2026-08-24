"""Bounded, non-executing phase 0.63 static checks."""

from __future__ import annotations

import hashlib
import re
import tomllib
from pathlib import Path
from typing import Any

SCHEMA = "hedron.interaction-checks/1"
MAX_FILES = 1_000
MAX_BYTES = 512 * 1024
_SKIP = frozenset({".git", ".venv", "node_modules", "dist", "build", "site", "__pycache__"})
_RULES: tuple[tuple[str, str, str, str], ...] = (
    ("HED-CHECK-0001", "error", "application-css", r"\.(css|scss|sass|less)$"),
    ("HED-CHECK-0002", "error", "unsafe-css-url", r"url\(\s*['\"]?(https?:|//|\.\.)"),
    ("HED-CHECK-0003", "error", "callback-execution", r"\b(eval|exec|Function)\s*\("),
    (
        "HED-CHECK-0004",
        "warning",
        "unbounded-client-runtime",
        r"\b(WebSocket|setInterval|localStorage)\b",
    ),
    ("HED-CHECK-0005", "warning", "raw-html-sink", r"\b(dangerouslySetInnerHTML|innerHTML)\b"),
    ("HED-CHECK-0006", "warning", "inline-style", r"\bstyle\s*=\s*['\"]"),
)


def _span(text: str, offset: int) -> dict[str, int]:
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
    rows = data.get("suppressions", [])
    if not isinstance(rows, list):
        return set()
    result: set[str] = set()
    for row in rows:
        if (
            isinstance(row, dict)
            and str(row.get("code", "")).startswith("HED-CHECK-")
            and str(row.get("justification", "")).strip()
        ):
            result.add(str(row["code"]))
    return result


def analyze_project(root: Path) -> dict[str, Any]:
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
    findings: list[dict[str, Any]] = []
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
                location = {"path": relative, **_span(source_text, match.start())}
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
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "non_executing": True,
        "limits": {"max_files": MAX_FILES, "max_bytes_per_file": MAX_BYTES},
        "files_scanned": len(files),
        "bytes_scanned": bytes_seen,
        "suppressions": sorted(suppressions),
        "findings": findings,
    }
    payload["digest"] = hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()
    return payload


__all__ = ["SCHEMA", "analyze_project"]
