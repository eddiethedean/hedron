"""Static Hedron 0.67 to 1.0 API migration analysis.

The API migrator is deliberately boring: it parses source, records source
spans, and optionally applies a small set of proven token replacements.  It
never imports the project being inspected.  Runtime warning metadata comes
from :mod:`hedron_core.migration`, so ``check`` and ``migrate`` cannot drift
apart about a removal's replacement or ownership.
"""

from __future__ import annotations

import ast
import difflib
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from hedron_core import DiagnosticSeverity
from hedron_core.diagnostics import Diagnostic, SourceSpan, make_diagnostic
from hedron_core.migration import PUBLIC_FUTURE_WARNINGS, FutureWarningRecord

API_MIGRATION_SCHEMA = "hedron.api-migration/1"
_SKIP_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        "site",
        "site-packages",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }
)
_TEXT_SUFFIXES = frozenset(
    {
        ".cfg",
        ".conf",
        ".env",
        ".ini",
        ".toml",
        ".yaml",
        ".yml",
        ".json",
        ".lock",
        ".hdj",
        ".html",
        ".htm",
        ".jinja",
        ".jinja2",
        ".md",
        ".pyi",
        ".txt",
    }
)


def _dotted(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _dotted(node.value)
        return f"{parent}.{node.attr}" if parent else None
    return None


def _line_col(source: str, offset: int) -> tuple[int, int]:
    before = source[:offset]
    line = before.count("\n") + 1
    last_newline = before.rfind("\n")
    return line, offset - last_newline


def _iter_files(source: Path) -> tuple[Path, tuple[Path, ...]]:
    source = source.resolve()
    if source.is_file():
        return source.parent, (source,)
    if not source.exists():
        raise FileNotFoundError(source)
    files: list[Path] = []
    for path in sorted(source.rglob("*")):
        if not path.is_file() or any(part in _SKIP_DIRS for part in path.relative_to(source).parts):
            continue
        if path.suffix == ".py" or path.suffix.lower() in _TEXT_SUFFIXES:
            files.append(path)
    return source, tuple(files)


def _record_for(path: str) -> FutureWarningRecord | None:
    records = PUBLIC_FUTURE_WARNINGS.for_path(path)
    return records[0] if records else None


@dataclass(frozen=True, slots=True)
class ApiMigrationFinding:
    """One source-mapped compatibility finding."""

    path: str
    line: int
    column: int
    code: str
    old_path: str
    replacement: str
    owner: str
    confidence: str
    automation_status: str
    reason: str
    kind: str = "python"
    first_warning_version: str = "0.67"
    removal_version: str = "1.0"
    documentation: str = ""
    fixture: str = ""

    def __post_init__(self) -> None:
        if self.confidence not in {"complete", "partial", "unknown"}:
            raise ValueError("invalid migration confidence")
        if self.automation_status not in {"automatic", "manual-review", "not-applicable"}:
            raise ValueError("invalid migration automation status")

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "code": self.code,
            "old_path": self.old_path,
            "replacement": self.replacement,
            "owner": self.owner,
            "confidence": self.confidence,
            "automation_status": self.automation_status,
            "reason": self.reason,
            "kind": self.kind,
            "first_warning_version": self.first_warning_version,
            "removal_version": self.removal_version,
            "documentation": self.documentation,
            "fixture": self.fixture,
        }


@dataclass(frozen=True, slots=True)
class ApiMigrationChange:
    """A deterministic source replacement; no source values are retained."""

    path: str
    replacements: int

    def to_dict(self) -> dict[str, object]:
        return {"path": self.path, "replacements": self.replacements}


@dataclass(frozen=True, slots=True)
class ApiMigrationReport:
    """Complete, serializable result of a non-executing API scan."""

    source: str
    files_seen: int
    findings: tuple[ApiMigrationFinding, ...] = ()
    changes: tuple[ApiMigrationChange, ...] = ()

    @property
    def non_executing(self) -> bool:
        return True

    @property
    def requires_review(self) -> bool:
        return any(item.confidence != "complete" for item in self.findings)

    def diagnostics(self) -> tuple[Diagnostic, ...]:
        out: list[Diagnostic] = []
        for finding in self.findings:
            severity = (
                DiagnosticSeverity.WARNING
                if finding.confidence == "complete"
                else DiagnosticSeverity.INFORMATION
            )
            out.append(
                make_diagnostic(
                    finding.code,
                    severity=severity,
                    title="Hedron 1.0 compatibility path",
                    explanation=(
                        f"{finding.path}:{finding.line} uses transitional "
                        f"`{finding.old_path}`; the 1.0 canonical path is "
                        f"`{finding.replacement}`. {finding.reason}"
                    ),
                    remediation=f"Migrate this task to {finding.replacement} before Hedron 1.0.",
                    owner=finding.owner,
                    context={
                        "schema": API_MIGRATION_SCHEMA,
                        "old_path": finding.old_path,
                        "replacement": finding.replacement,
                        "confidence": finding.confidence,
                        "automation_status": finding.automation_status,
                        "kind": finding.kind,
                        "source": finding.path,
                        "first_warning_version": finding.first_warning_version,
                        "removal_version": finding.removal_version,
                        "documentation": finding.documentation,
                        "fixture": finding.fixture,
                    },
                    span=SourceSpan(finding.path, finding.line, finding.column),
                )
            )
        return tuple(out)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": API_MIGRATION_SCHEMA,
            "source": self.source,
            "non_executing": self.non_executing,
            "files_seen": self.files_seen,
            "requires_review": self.requires_review,
            "findings": [item.to_dict() for item in self.findings],
            "changes": [item.to_dict() for item in self.changes],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


def _finding(
    *,
    path: str,
    line: int,
    column: int,
    record: FutureWarningRecord,
    confidence: str,
    automation_status: str,
    reason: str,
    kind: str,
) -> ApiMigrationFinding:
    return ApiMigrationFinding(
        path=path,
        line=line,
        column=column,
        code=record.code,
        old_path=record.old_path,
        replacement=record.replacement,
        owner=record.owner,
        confidence=confidence,
        automation_status=automation_status,
        reason=reason,
        kind=kind,
        first_warning_version=record.first_warning_version,
        removal_version=record.removal_version,
        documentation=record.documentation,
        fixture=record.fixture,
    )


def _python_findings(path: Path, display_path: str, source: str) -> tuple[ApiMigrationFinding, ...]:
    try:
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, ValueError):
        return ()
    out: list[ApiMigrationFinding] = []
    seen: set[tuple[int, int, str]] = set()
    records = {record.old_path: record for record in PUBLIC_FUTURE_WARNINGS.records()}

    def add(node: ast.AST, old_path: str, *, manual: bool = False) -> None:
        record = records.get(old_path)
        if record is None or not hasattr(node, "lineno"):
            return
        key = (
            int(getattr(node, "lineno", 0)),
            int(getattr(node, "col_offset", 0)),
            old_path,
        )
        if key in seen:
            return
        seen.add(key)
        reason = "The replacement is a proven mechanical rename."
        if record.confidence != "complete":
            reason = "The replacement changes the handler contract and needs a human review."
        confidence = record.confidence
        automation = record.automation_status
        if manual:
            reason = "Region-specific arguments need a human review before renaming."
            confidence = "partial"
            automation = "manual-review"
        out.append(
            _finding(
                path=display_path,
                line=int(getattr(node, "lineno", 1)),
                column=int(getattr(node, "col_offset", 0)) + 1,
                record=record,
                confidence=confidence,
                automation_status=automation,
                reason=reason,
                kind="python",
            )
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            dotted = _dotted(node.func)
            if dotted not in records:
                continue
            manual = dotted == "app.fragment" and any(
                kw.arg in {"region", "regions", "fragment_regions"} for kw in node.keywords
            )
            add(node, dotted, manual=manual)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                dotted = _dotted(decorator)
                if dotted in records:
                    add(decorator, dotted)
    # Reflection is intentionally never rewritten.  Report it as unknown so a
    # clean AST result cannot be mistaken for a complete migration proof.
    reflected = re.compile(
        r"\bgetattr\s*\([^,]+,\s*['\"](component|fragment|include_feature|screen|"
        r"refreshable|command|form_command)['\"]"
    )
    for match in reflected.finditer(source):
        old_path = f"app.{match.group(1)}"
        record = records.get(old_path)
        if record is None:
            continue
        line, column = _line_col(source, match.start())
        key = (line, column - 1, old_path)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            _finding(
                path=display_path,
                line=line,
                column=column,
                record=record,
                confidence="unknown",
                automation_status="manual-review",
                reason="Reflection hides the receiver and cannot be safely transformed statically.",
                kind="dynamic",
            )
        )
    # Stringly configuration in Python is another opaque form.  It is not
    # rewritten because the surrounding authority cannot be inferred.
    string_paths = re.compile(
        r"\b(app|router)\.(component|fragment|include_feature|screen|refreshable|command|"
        r"form_command)\b"
    )
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        for match in string_paths.finditer(node.value):
            old_path = f"{match.group(1)}.{match.group(2)}"
            record = records.get(old_path)
            if record is None or not hasattr(node, "lineno"):
                continue
            line = int(getattr(node, "lineno", 1))
            column = int(getattr(node, "col_offset", 0))
            key = (line, column, old_path)
            if key in seen:
                continue
            seen.add(key)
            out.append(
                _finding(
                    path=display_path,
                    line=line,
                    column=column + 1,
                    record=record,
                    confidence="unknown",
                    automation_status="manual-review",
                    reason=(
                        "A stringly API path has no statically provable owner or call semantics."
                    ),
                    kind="dynamic",
                )
            )
    return tuple(sorted(out, key=lambda item: (item.path, item.line, item.column, item.code)))


_TEXT_PATTERN = re.compile(
    r"\b(app|router)\.(component|fragment|include_feature|screen|refreshable|command|form_command)\b"
)


def _text_findings(display_path: str, source: str) -> tuple[ApiMigrationFinding, ...]:
    out: list[ApiMigrationFinding] = []
    records = {record.old_path: record for record in PUBLIC_FUTURE_WARNINGS.records()}
    for match in _TEXT_PATTERN.finditer(source):
        old_path = f"{match.group(1)}.{match.group(2)}"
        record = records.get(old_path)
        if record is None:
            continue
        line, column = _line_col(source, match.start())
        out.append(
            _finding(
                path=display_path,
                line=line,
                column=column,
                record=record,
                confidence="partial",
                automation_status="manual-review",
                reason="Textual or template usage cannot be proven safe by AST analysis.",
                kind="text",
            )
        )
    return tuple(out)


def scan_api(source: str | Path) -> ApiMigrationReport:
    """Scan a file or project directory without importing or executing it."""
    root, files = _iter_files(Path(source))
    findings: list[ApiMigrationFinding] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        display = (
            path.name
            if root == path.parent and len(files) == 1
            else path.relative_to(root).as_posix()
        )
        if path.suffix == ".py":
            findings.extend(_python_findings(path, display, text))
        else:
            findings.extend(_text_findings(display, text))
    findings.sort(key=lambda item: (item.path, item.line, item.column, item.code))
    return ApiMigrationReport(
        source=str(Path(source).resolve()),
        files_seen=len(files),
        findings=tuple(findings),
    )


def _replacement_for_finding(finding: ApiMigrationFinding) -> str | None:
    if finding.confidence != "complete" or finding.automation_status != "automatic":
        return None
    return finding.replacement


def _replace_python(
    source: str,
    path: Path,
    findings: Iterable[ApiMigrationFinding],
) -> tuple[str, int]:
    try:
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, ValueError):
        return source, 0
    wanted = {
        (item.line, item.old_path): item.replacement.rsplit(".", 1)[-1]
        for item in findings
        if _replacement_for_finding(item)
    }
    replacements: list[tuple[int, int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute) or not hasattr(node, "lineno"):
            continue
        dotted = _dotted(node)
        replacement = wanted.get((int(node.lineno), dotted or ""))
        if dotted is None or replacement is None:
            continue
        leaf = dotted.rsplit(".", 1)[-1]
        start = (
            _offset_for_position(source, int(node.end_lineno), int(node.end_col_offset))
            - len(leaf)
        )
        end = start + len(leaf)
        replacements.append((start, end, replacement))
    for start, end, replacement in sorted(set(replacements), reverse=True):
        source = source[:start] + replacement + source[end:]
    return source, len(set(replacements))


def _offset_for_position(source: str, line: int, column: int) -> int:
    lines = source.splitlines(keepends=True)
    return sum(len(item) for item in lines[: line - 1]) + column


def _replace_text(source: str, findings: Iterable[ApiMigrationFinding] = ()) -> tuple[str, int]:
    replacements = {
        "app.component": "app.view",
        "app.fragment": "app.view",
        "app.include_feature": "app.include",
        "app.screen": "app.page",
        "app.refreshable": "app.view",
        "app.command": "app.action",
        "app.form_command": "app.action",
        "router.component": "router.view",
    }
    allowed = {
        item.old_path: item.replacement
        for item in findings
        if _replacement_for_finding(item)
    }
    count = 0
    for old, new in replacements.items():
        if old not in allowed:
            continue
        source, n = re.subn(rf"\b{re.escape(old)}\b", new, source)
        count += n
    return source, count


def transform_api(
    source: str | Path,
    *,
    output: str | Path | None = None,
    apply: bool = False,
) -> ApiMigrationReport:
    """Create a reviewable transform, optionally writing to a new tree or in place.

    ``output`` never overwrites an existing file.  In-place writes require
    ``apply=True`` and are intentionally explicit.
    """
    source_path = Path(source).resolve()
    report = scan_api(source_path)
    if output is None and not apply:
        return report
    if output is not None and apply:
        raise ValueError("choose --out or --apply, not both")
    root, files = _iter_files(source_path)
    destination = Path(output).resolve() if output is not None else root
    if output is not None and source_path.is_file():
        targets = [(source_path, destination)]
    else:
        if output is not None:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.mkdir(parents=True, exist_ok=False)
        targets = [(path, destination / path.relative_to(root)) for path in files]
    changes: list[ApiMigrationChange] = []
    by_path: Mapping[str, tuple[ApiMigrationFinding, ...]] = {
        path: tuple(item for item in report.findings if item.path == path)
        for path in {item.path for item in report.findings}
    }
    for original, target in targets:
        try:
            text = original.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        display = original.name if source_path.is_file() else original.relative_to(root).as_posix()
        items = by_path.get(display, ())
        if original.suffix == ".py":
            transformed, count = _replace_python(text, original, items)
        else:
            transformed, count = _replace_text(text, items)
        if output is not None:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise FileExistsError(f"refusing to overwrite {target}")
            # ``--out`` is a complete, reviewable project tree rather than a
            # sparse patch directory.  Preserve files that have no proven
            # replacement so reviewers can run the generated tree directly.
            target.write_text(transformed, encoding="utf-8")
        elif count and transformed != text:
            target.write_text(transformed, encoding="utf-8")
        if count and transformed != text:
            changes.append(ApiMigrationChange(display, count))
    return ApiMigrationReport(
        source=report.source,
        files_seen=report.files_seen,
        findings=report.findings,
        changes=tuple(sorted(changes, key=lambda item: item.path)),
    )


def unified_diff(source: str | Path) -> str:
    """Return a deterministic diff for mechanically transformable findings."""
    path = Path(source).resolve()
    report = scan_api(path)
    root, files = _iter_files(path)
    chunks: list[str] = []
    for original in files:
        try:
            before = original.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        display = original.name if path.is_file() else original.relative_to(root).as_posix()
        items = tuple(item for item in report.findings if item.path == display)
        if original.suffix == ".py":
            after, count = _replace_python(before, original, items)
        else:
            after, count = _replace_text(before, items)
        if count and after != before:
            chunks.extend(
                difflib.unified_diff(
                    before.splitlines(keepends=True),
                    after.splitlines(keepends=True),
                    fromfile=display,
                    tofile=display,
                )
            )
    return "".join(chunks)


__all__ = [
    "API_MIGRATION_SCHEMA",
    "ApiMigrationChange",
    "ApiMigrationFinding",
    "ApiMigrationReport",
    "scan_api",
    "transform_api",
    "unified_diff",
]
