"""Stable, actionable diagnostics raised by the documentation compiler."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    message: str
    source: str | None = None
    line: int | None = None
    column: int | None = None
    title: str = "Documentation compiler error"
    explanation: str = ""
    remediation: str = ""
    end_line: int | None = None
    end_column: int | None = None

    def format(self) -> str:
        location = ""
        if self.source:
            location = self.source
            if self.line is not None:
                location += f":{self.line}"
            if self.column is not None:
                location += f":{self.column}"
            location += ": "
        result = f"{location}{self.code} {self.title}: {self.message}"
        if self.remediation:
            result += f" Remediation: {self.remediation}"
        return result

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "code": self.code,
            "title": self.title,
            "message": self.message,
            "explanation": self.explanation,
            "remediation": self.remediation,
        }
        for name in ("source", "line", "column", "end_line", "end_column"):
            value = getattr(self, name)
            if value is not None:
                result[name] = value
        return result


_DETAILS: dict[str, tuple[str, str, str]] = {
    "HED-DOCS-0100": (
        "Raw HTML is not supported",
        "Raw HTML bypasses typed lowering.",
        "Use supported Markdown or add a reviewed typed node.",
    ),
    "HED-DOCS-0101": (
        "Document node budget exceeded",
        "The AST exceeds its node budget.",
        "Split the page or raise build.max_nodes after review.",
    ),
    "HED-DOCS-0102": (
        "Document source budget exceeded",
        "The UTF-8 source is too large.",
        "Split the page or raise build.max_source_bytes after review.",
    ),
    "HED-DOCS-0103": (
        "Document nesting budget exceeded",
        "The AST is nested too deeply.",
        "Flatten the content or raise build.max_depth after review.",
    ),
    "HED-DOCS-0104": (
        "Table budget exceeded",
        "The document has too many table cells.",
        "Split the table or raise build.max_table_cells after review.",
    ),
    "HED-DOCS-0105": (
        "Code block budget exceeded",
        "Code count or bytes exceed policy.",
        "Split examples or raise the reviewed code-block budget.",
    ),
    "HED-DOCS-0106": (
        "Directive budget exceeded",
        "Too many directives require generation.",
        "Split the page or raise build.max_directives after review.",
    ),
    "HED-DOCS-0107": (
        "Unsupported Markdown syntax",
        "No typed node owns this syntax.",
        "Rewrite it or add an explicit reviewed node and tests.",
    ),
    "HED-DOCS-0108": (
        "Malformed Markdown extension",
        "The extension is incomplete or unsafe.",
        "Correct the marker, identifier, and required indented body.",
    ),
}


class DocsError(ValueError):
    """A user-actionable documentation build failure."""

    def __init__(self, diagnostic: Diagnostic | str) -> None:
        self.diagnostic = (
            diagnostic
            if isinstance(diagnostic, Diagnostic)
            else Diagnostic("HED-DOCS-0001", str(diagnostic))
        )
        super().__init__(self.diagnostic.format())


def source_error(
    code: str,
    message: str,
    source: Path | str | None = None,
    *,
    line: int | None = None,
    column: int | None = None,
    end_line: int | None = None,
    end_column: int | None = None,
    title: str | None = None,
    explanation: str | None = None,
    remediation: str | None = None,
) -> DocsError:
    default_title, default_explanation, default_remediation = _DETAILS.get(
        code, ("Documentation compiler error", "", "")
    )
    return DocsError(
        Diagnostic(
            code=code,
            message=message,
            source=str(source) if source else None,
            line=line,
            column=column,
            title=title or default_title,
            explanation=explanation if explanation is not None else default_explanation,
            remediation=remediation if remediation is not None else default_remediation,
            end_line=end_line,
            end_column=end_column,
        )
    )
