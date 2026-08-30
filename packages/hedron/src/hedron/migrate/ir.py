"""Versioned migration IR (beta; not part of the minimal stable facade)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hedron_core.compat import StrEnum


class Disposition(StrEnum):
    TRANSLATED = "translated"
    SCAFFOLDED = "scaffolded"
    REPORT_ONLY = "report_only"
    UNSUPPORTED = "unsupported"


class Confidence(StrEnum):
    EXACT = "exact"
    BOUNDED = "bounded"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True, slots=True)
class SourceSpan:
    path: str
    start_line: int
    start_column: int = 1
    end_line: int | None = None
    end_column: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "start_line": self.start_line,
            "start_column": self.start_column,
            "end_line": self.end_line or self.start_line,
            "end_column": self.end_column or self.start_column,
        }


@dataclass(frozen=True, slots=True)
class SourceUnit:
    path: str
    content_hash: str
    relative_path: str
    is_entrypoint: bool = False
    is_page: bool = False


@dataclass
class StreamlitCall:
    op_id: str
    symbol: str
    span: SourceSpan
    disposition: Disposition
    confidence: Confidence
    args_summary: dict[str, Any] = field(default_factory=dict[str, Any])
    assigned_to: str | None = None
    in_sidebar: bool = False
    findings: list[str] = field(default_factory=list[str])
    hedron_hint: str | None = None


@dataclass
class StreamlitMigrationPlan:
    schema_version: str
    mapping_catalog_version: str
    streamlit_audit_baseline: str
    source_units: list[SourceUnit]
    calls: list[StreamlitCall]
    page_title: str | None = None
    extras: list[str] = field(default_factory=list[str])
    tool_errors: list[str] = field(default_factory=list[str])

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "mapping_catalog_version": self.mapping_catalog_version,
            "streamlit_audit_baseline": self.streamlit_audit_baseline,
            "source_units": [
                {
                    "path": u.path,
                    "relative_path": u.relative_path,
                    "content_hash": u.content_hash,
                    "is_entrypoint": u.is_entrypoint,
                    "is_page": u.is_page,
                }
                for u in self.source_units
            ],
            "page_title": self.page_title,
            "extras": list(self.extras),
            "calls": [
                {
                    "op_id": c.op_id,
                    "symbol": c.symbol,
                    "span": c.span.to_dict(),
                    "disposition": c.disposition.value,
                    "confidence": c.confidence.value,
                    "args_summary": dict(c.args_summary),
                    "assigned_to": c.assigned_to,
                    "in_sidebar": c.in_sidebar,
                    "findings": list(c.findings),
                    "hedron_hint": c.hedron_hint,
                }
                for c in self.calls
            ],
            "tool_errors": list(self.tool_errors),
        }
