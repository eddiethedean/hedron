"""Non-executing React migration dispositions for phase 0.63.

This scanner deliberately reports source facts and bounded recommendations. It
does not import JavaScript, run a bundler, infer runtime behavior, or rewrite
the source tree.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

SCHEMA = "hedron.react-migration/1"
MAX_FILES = 500
MAX_BYTES = 512 * 1024

_RULES: tuple[dict[str, Any], ...] = (
    {
        "pattern": r"\b(useActionState|useFormState|<form\b|<Form\b)",
        "kind": "form-lifecycle",
        "disposition": "native",
        "confidence": "bounded",
        "target": "form command + lifecycle boundary",
    },
    {
        "pattern": r"\b(useQuery|useSWR|isLoading|isPending|loading|<Suspense\b)",
        "kind": "async-region",
        "disposition": "native",
        "confidence": "bounded",
        "target": "refreshable view/job/async region",
    },
    {
        "pattern": r"\b(useOptimistic|optimistic|startTransition)\b",
        "kind": "optimistic-update",
        "disposition": "adapter",
        "confidence": "ambiguous",
        "target": "approved optimistic risk class or explicit adapter",
    },
    {
        "pattern": r"\b(ErrorBoundary|componentDidCatch|getDerivedStateFromError)\b",
        "kind": "error-boundary",
        "disposition": "redesign",
        "confidence": "bounded",
        "target": "declared server/element boundary",
    },
    {
        "pattern": r"\b(createPortal|useNavigate|BrowserRouter|MemoryRouter|react-router)\b",
        "kind": "client-routing-or-portal",
        "disposition": "redesign",
        "confidence": "bounded",
        "target": "server routes + navigation/overlay ownership",
    },
    {
        "pattern": r"\b(WebSocket|SharedWorker|ServiceWorker|offline|IndexedDB|canvas\b|<canvas\b)",
        "kind": "client-runtime",
        "disposition": "unsupported",
        "confidence": "exact",
        "target": "retain isolated custom frontend or redesign",
    },
    {
        "pattern": r"\b(ThirdParty|ReactWidget|ReactSelect|ReactTable)\b",
        "kind": "react-only-widget",
        "disposition": "adapter",
        "confidence": "ambiguous",
        "target": "bounded adapter or Experimental island review",
    },
)


def migration_disposition_manifest() -> dict[str, Any]:
    """Return the frozen disposition catalog used by the source scanner."""

    rows = [
        {
            "kind": str(rule["kind"]),
            "disposition": str(rule["disposition"]),
            "confidence": str(rule["confidence"]),
            "target": str(rule["target"]),
        }
        for rule in _RULES
    ]
    payload: dict[str, Any] = {
        "schema": "hedron.react-migration-disposition/1",
        "rules": rows,
        "non_executing": True,
        "unsupported_is_explicit": True,
    }
    payload["digest"] = hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()
    return payload


def _files(source: Path) -> tuple[Path, ...]:
    if source.is_file():
        return (source,)
    if not source.is_dir():
        raise ValueError(f"React source does not exist: {source}")
    allowed = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
    found = [
        path
        for path in sorted(source.rglob("*"))
        if path.is_file() and not path.is_symlink() and path.suffix.lower() in allowed
    ]
    if len(found) > MAX_FILES:
        raise ValueError(f"React source exceeds the {MAX_FILES}-file analysis limit")
    return tuple(found)


def _span(text: str, offset: int) -> dict[str, int]:
    line = text.count("\n", 0, offset) + 1
    previous = text.rfind("\n", 0, offset)
    return {"start_line": line, "start_column": offset - previous}


def analyze_react_source(source: Path) -> dict[str, Any]:
    """Analyze React/TypeScript source using bounded lexical facts only."""

    root = source if source.is_dir() else source.parent
    findings: list[dict[str, Any]] = []
    files_seen = 0
    bytes_seen = 0
    for path in _files(source):
        if path.stat().st_size > MAX_BYTES:
            findings.append(
                {
                    "code": "HED-MIGRATE-0001",
                    "kind": "analysis-limit",
                    "disposition": "unsupported",
                    "confidence": "exact",
                    "message": f"Skipped oversized source file {path.name}.",
                    "span": {
                        "path": str(path.relative_to(root)),
                        "start_line": 1,
                        "start_column": 1,
                    },
                }
            )
            continue
        text = path.read_text(encoding="utf-8")
        files_seen += 1
        bytes_seen += len(text.encode("utf-8"))
        relative = str(path.relative_to(root))
        for rule in _RULES:
            for match in re.finditer(str(rule["pattern"]), text, re.IGNORECASE):
                span = _span(text, match.start())
                findings.append(
                    {
                        "code": f"HED-MIGRATE-{str(rule['kind']).upper().replace('-', '_')}",
                        "kind": rule["kind"],
                        "disposition": rule["disposition"],
                        "confidence": rule["confidence"],
                        "target": rule["target"],
                        "evidence": match.group(0),
                        "span": {"path": relative, **span},
                    }
                )
    findings.sort(
        key=lambda item: (
            str(item.get("span", {}).get("path", "")),
            int(item.get("span", {}).get("start_line", 0)),
            str(item.get("kind", "")),
        )
    )
    disposition_counts: dict[str, int] = {}
    for finding in findings:
        disposition = str(finding["disposition"])
        disposition_counts[disposition] = disposition_counts.get(disposition, 0) + 1
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "source": str(source),
        "non_executing": True,
        "limits": {"max_files": MAX_FILES, "max_bytes_per_file": MAX_BYTES},
        "files_seen": files_seen,
        "bytes_seen": bytes_seen,
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "findings": findings,
        "catalog": migration_disposition_manifest()["digest"],
    }
    payload["digest"] = hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()
    return payload


__all__ = ["SCHEMA", "analyze_react_source", "migration_disposition_manifest"]
