"""Source-aware diagnostics and bounded report projections for Edron.

The report objects in this module deliberately contain facts about definitions and
source, never callable results.  They are small enough to use from editor tooling
and are intentionally independent of the native renderer.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

Severity = Literal["error", "warning", "information"]
MAX_DIAGNOSTICS = 512


@dataclass(frozen=True, slots=True)
class SourceLocation:
    """A one-based source span attached to an Edron definition or finding."""

    path: str
    start_line: int
    start_column: int = 1
    end_line: int | None = None
    end_column: int | None = None
    qualname: str | None = None

    def __post_init__(self) -> None:
        if self.start_line < 1 or self.start_column < 1:
            raise ValueError("source positions are one-based")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "start_line": self.start_line,
            "start_column": self.start_column,
            "end_line": self.end_line or self.start_line,
            "end_column": self.end_column or self.start_column,
            **({"qualname": self.qualname} if self.qualname else {}),
        }


def _redact(value: Any, *, depth: int = 0) -> Any:
    """Return a bounded JSON-compatible diagnostic value."""
    if depth > 3:
        return "<redacted>"
    if isinstance(value, str):
        lowered = value.lower()
        if any(word in lowered for word in ("password", "secret", "token", "cookie", "csrf")):
            return "<redacted>"
        return value[:240]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        mapping = cast(Mapping[Any, Any], value)
        mapping_items: list[tuple[Any, Any]] = list(mapping.items())[:32]
        for key, item in mapping_items:
            key_text = str(key)[:80]
            result[key_text] = (
                "<redacted>"
                if any(
                    word in key_text.lower()
                    for word in ("password", "secret", "token", "cookie", "csrf")
                )
                else _redact(item, depth=depth + 1)
            )
        return result
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        sequence_items: list[Any] = list(cast(Sequence[Any], value))[:32]
        return [_redact(item, depth=depth + 1) for item in sequence_items]
    return f"<{type(value).__name__}>"


@dataclass(frozen=True, slots=True)
class EdronDiagnostic:
    """An immutable Edron diagnostic suitable for text, JSON, or SARIF output."""

    code: str
    severity: Severity
    title: str
    explanation: str
    remediation: str = ""
    source: SourceLocation | None = None
    native_diagnostic: Any = None
    context: Mapping[str, Any] = field(default_factory=lambda: dict[str, Any]())
    docs_url: str | None = None

    def __post_init__(self) -> None:
        if not self.code.startswith("EDR-"):
            raise ValueError("Edron diagnostic codes must start with EDR-")
        if self.severity not in {"error", "warning", "information"}:
            raise ValueError(f"unknown diagnostic severity: {self.severity!r}")
        object.__setattr__(self, "context", _redact(self.context))

    def to_mapping(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity,
            "title": self.title,
            "explanation": self.explanation,
            "remediation": self.remediation,
            "context": dict(self.context),
        }
        if self.source is not None:
            result["source"] = self.source.to_mapping()
        if self.docs_url is not None:
            result["docs_url"] = self.docs_url
        if self.native_diagnostic is not None:
            native = getattr(self.native_diagnostic, "as_json", None)
            result["native_diagnostic"] = (
                native() if callable(native) else _redact(self.native_diagnostic)
            )
        return result

    def as_text(self) -> str:
        location = ""
        if self.source is not None:
            location = f" [{self.source.path}:{self.source.start_line}:{self.source.start_column}]"
        parts = [f"{self.code} {self.severity}: {self.title}{location}", self.explanation]
        if self.remediation:
            parts.append(f"Remediation: {self.remediation}")
        return "\n".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Compatibility spelling for JSON-compatible consumers."""
        return self.to_mapping()

    as_json = to_mapping


@dataclass(frozen=True, slots=True)
class DiagnosticReport:
    """A bounded collection of diagnostics with stable output projections."""

    diagnostics: tuple[EdronDiagnostic, ...] = ()
    schema: str = "edron.diagnostics/1"
    truncated: bool = False

    def __post_init__(self) -> None:
        if len(self.diagnostics) > MAX_DIAGNOSTICS:
            object.__setattr__(self, "diagnostics", self.diagnostics[:MAX_DIAGNOSTICS])
            object.__setattr__(self, "truncated", True)

    @property
    def ok(self) -> bool:
        return not any(item.severity == "error" for item in self.diagnostics)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "ok": self.ok,
            "truncated": self.truncated,
            "diagnostics": [item.to_mapping() for item in self.diagnostics],
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.to_mapping(), indent=indent, sort_keys=True) + "\n"

    def to_dict(self) -> dict[str, Any]:
        return self.to_mapping()

    def to_text(self) -> str:
        return "\n\n".join(item.as_text() for item in self.diagnostics) or "No findings."

    def to_sarif(self) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        rules: dict[str, dict[str, Any]] = {}
        for item in self.diagnostics:
            rules.setdefault(
                item.code,
                {
                    "id": item.code,
                    "shortDescription": {"text": item.title},
                    "fullDescription": {"text": item.explanation},
                },
            )
            result: dict[str, Any] = {
                "ruleId": item.code,
                "level": {"error": "error", "warning": "warning", "information": "note"}[
                    item.severity
                ],
                "message": {"text": f"{item.title}: {item.explanation}"},
            }
            if item.source is not None:
                result["locations"] = [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": item.source.path},
                            "region": {
                                "startLine": item.source.start_line,
                                "startColumn": item.source.start_column,
                                "endLine": item.source.end_line or item.source.start_line,
                                "endColumn": item.source.end_column or item.source.start_column,
                            },
                        }
                    }
                ]
            results.append(result)
        return {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [
                {
                    "tool": {"driver": {"name": "edron", "rules": list(rules.values())}},
                    "results": results,
                }
            ],
        }


def source_location(value: Any, *, qualname: str | None = None) -> SourceLocation | None:
    """Best-effort source location lookup that never calls ``value``."""
    import inspect

    try:
        path = inspect.getsourcefile(value) or inspect.getfile(value)
        try:
            _, line = inspect.getsourcelines(value)
        except (OSError, TypeError):
            _, line = inspect.findsource(value)
            line += 1
    except (OSError, TypeError):
        return None
    if not path:
        return None
    return SourceLocation(
        str(Path(path)), line, qualname=qualname or getattr(value, "__qualname__", None)
    )


def finding(
    code: str,
    *,
    severity: Severity,
    title: str,
    explanation: str,
    remediation: str = "",
    source: SourceLocation | None = None,
    context: Mapping[str, Any] | None = None,
) -> EdronDiagnostic:
    return EdronDiagnostic(
        code=code,
        severity=severity,
        title=title,
        explanation=explanation,
        remediation=remediation,
        source=source,
        context=context or {},
    )


__all__ = ["DiagnosticReport", "EdronDiagnostic", "SourceLocation", "finding", "source_location"]
