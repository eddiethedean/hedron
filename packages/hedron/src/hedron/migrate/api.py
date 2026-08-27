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


def _iter_files(source: Path, *, include_all: bool = False) -> tuple[Path, tuple[Path, ...]]:
    source = source.resolve()
    if source.is_file():
        return source.parent, (source,)
    if not source.exists():
        raise FileNotFoundError(source)
    files: list[Path] = []
    for path in sorted(source.rglob("*")):
        if not path.is_file() or any(part in _SKIP_DIRS for part in path.relative_to(source).parts):
            continue
        if include_all or path.suffix == ".py" or path.suffix.lower() in _TEXT_SUFFIXES:
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
    replacement: str | None = None,
) -> ApiMigrationFinding:
    return ApiMigrationFinding(
        path=path,
        line=line,
        column=column,
        code=record.code,
        old_path=record.old_path,
        replacement=replacement or record.replacement,
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


# Direct helper imports are less common than method decorators, but they are
# still part of the public 0.67 surface. Keep this deliberately narrow:
# unrelated symbols such as the ``Component`` node class must not be mistaken
# for the transitional ``app.component`` route.
_IMPORTED_API = {
    "fragment": "app.fragment",
    "include_feature": "app.include_feature",
    "screen": "app.screen",
    "refreshable": "app.refreshable",
    "command": "app.command",
    "form_command": "app.form_command",
}


def _import_findings(
    tree: ast.AST,
    *,
    display_path: str,
    records: Mapping[str, FutureWarningRecord],
) -> tuple[ApiMigrationFinding, ...]:
    """Find direct imports of transitional helpers without importing modules."""
    out: list[ApiMigrationFinding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.module not in {"hedron", "hedron.app"}:
            continue
        for alias in node.names:
            if alias.name == "*":
                # A wildcard import can bring any compatibility helper into the
                # application namespace.  Report every registered path as an
                # opaque import instead of pretending the project is clean.
                for record in records.values():
                    out.append(
                        _finding(
                            path=display_path,
                            line=int(getattr(node, "lineno", 1)),
                            column=int(getattr(node, "col_offset", 0)) + 1,
                            record=record,
                            confidence="unknown",
                            automation_status="manual-review",
                            reason=(
                                "A wildcard import may expose transitional helpers; "
                                "the imported names cannot be proven statically."
                            ),
                            kind="import",
                        )
                    )
                continue
            old_path = _IMPORTED_API.get(alias.name)
            record = records.get(old_path or "")
            if record is None or not hasattr(node, "lineno"):
                continue
            # A direct import does not identify the owning application object;
            # e.g. ``include_feature`` is an app method, not a module-level
            # ``include`` function. Report it for review rather than emitting
            # an invalid import rewrite.
            confidence = "unknown"
            automation = "manual-review"
            reason = "A direct helper import has no statically provable application owner."
            out.append(
                _finding(
                    path=display_path,
                    line=int(getattr(node, "lineno", 1)),
                    column=int(getattr(node, "col_offset", 0)) + 1,
                    record=record,
                    confidence=confidence,
                    automation_status=automation,
                    reason=reason,
                    kind="import",
                )
            )
    return tuple(out)


def _python_findings(path: Path, display_path: str, source: str) -> tuple[ApiMigrationFinding, ...]:
    try:
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, ValueError):
        return ()
    out: list[ApiMigrationFinding] = []
    seen: set[tuple[int, int, str]] = set()
    records = {record.old_path: record for record in PUBLIC_FUTURE_WARNINGS.records()}
    # ``hedron_sim.SimApp`` intentionally has its own fragment registration
    # vocabulary and accepts simulator-only route options.  The migration
    # checker must not mistake that package-native API for Hedron's removed
    # application facade.  Keep this inference syntactic so checking remains
    # non-executing; unknown receivers continue to be reported conservatively.
    simulator_receivers: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if not isinstance(value, ast.Call):
            continue
        constructor = _dotted(value.func)
        if constructor is None or constructor.rsplit(".", 1)[-1] != "SimApp":
            continue
        targets = node.targets if isinstance(node, ast.Assign) else (node.target,)
        simulator_receivers.update(target.id for target in targets if isinstance(target, ast.Name))
    out.extend(_import_findings(tree, display_path=display_path, records=records))
    seen.update((item.line, item.column - 1, item.old_path) for item in out)

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
        replacement: str | None = None
        if record.confidence != "complete":
            reason = "The replacement changes the handler contract and needs a human review."
        confidence = record.confidence
        automation = record.automation_status
        if manual:
            reason = "Region-specific arguments need a human review before renaming."
            confidence = "partial"
            automation = "manual-review"
        # A component route that declares an unsafe method is an action task,
        # not a safe view. The registry records the common GET rename; this
        # call-site disposition prevents an unsafe route from being rewritten
        # to a GET-oriented decorator.
        if old_path in {"app.component", "router.component"} and isinstance(node, ast.Call):
            methods: list[str] = []
            for keyword in node.keywords:
                if keyword.arg == "method" and isinstance(keyword.value, ast.Constant):
                    methods.append(str(keyword.value.value))
                elif keyword.arg == "methods" and isinstance(
                    keyword.value, (ast.List, ast.Tuple, ast.Set)
                ):
                    methods.extend(
                        str(item.value)
                        for item in keyword.value.elts
                        if isinstance(item, ast.Constant)
                    )
            if any(method.upper() not in {"GET", "HEAD", "OPTIONS", "TRACE"} for method in methods):
                reason = (
                    "Unsafe component methods are action tasks; choose the action API manually."
                )
                confidence = "partial"
                automation = "manual-review"
                replacement = old_path.replace("component", "action")
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
                replacement=replacement,
            )
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            dotted = _dotted(node.func)
            if dotted not in records:
                continue
            if dotted.startswith("app.") and isinstance(node.func, ast.Attribute):
                receiver = node.func.value
                if isinstance(receiver, ast.Name) and receiver.id in simulator_receivers:
                    continue
            manual = dotted == "app.fragment" and any(
                kw.arg in {"region", "regions", "fragment_regions"} for kw in node.keywords
            )
            add(node, dotted, manual=manual)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                dotted = _dotted(decorator)
                if dotted in records:
                    if dotted.startswith("app.") and isinstance(decorator, ast.Attribute):
                        receiver = decorator.value
                        if isinstance(receiver, ast.Name) and receiver.id in simulator_receivers:
                            continue
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
        r"\b(app|router|flask|blueprint)\.(component|fragment|include_feature|screen|"
        r"refreshable|command|form_command)\b"
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
    r"\b(app|router|flask|blueprint)\.(component|fragment|include_feature|screen|"
    r"refreshable|command|form_command)\b"
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
        end_lineno = node.end_lineno
        end_col_offset = node.end_col_offset
        if end_lineno is None or end_col_offset is None:
            continue
        leaf = dotted.rsplit(".", 1)[-1]
        start = _offset_for_position(source, end_lineno, end_col_offset) - len(leaf)
        end = start + len(leaf)
        replacements.append((start, end, replacement))
    # Replace only the imported identifier, preserving ``as`` aliases. The
    # AST's ImportFrom aliases do not expose reliable end offsets on every
    # supported Python version, so locate the token on the recorded line.
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.module not in {"hedron", "hedron.app"}:
            continue
        for alias in node.names:
            old_path = _IMPORTED_API.get(alias.name)
            if old_path is None:
                continue
            # Import aliases expose their own source span (including multiline
            # parenthesized imports).  Match either the finding's ImportFrom
            # line or the alias line, then replace only the imported token so
            # ``as`` bindings remain intact.
            alias_line = int(getattr(alias, "lineno", 0) or getattr(node, "lineno", 0))
            node_line = int(getattr(node, "lineno", 0))
            replacement = wanted.get((node_line, old_path)) or wanted.get((alias_line, old_path))
            if replacement is None or not hasattr(alias, "col_offset"):
                continue
            start = _offset_for_position(source, alias_line, int(alias.col_offset))
            # The alias span includes ``as name``.  Restrict replacement to the
            # imported identifier at the beginning of that span.
            replacements.append((start, start + len(alias.name), replacement))
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
        "flask.component": "flask.view",
        "blueprint.component": "blueprint.view",
        "blueprint.include_feature": "blueprint.include",
    }
    allowed = {
        item.old_path: item.replacement for item in findings if _replacement_for_finding(item)
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
    # A generated output tree must be a lossless project copy.  The scanner
    # intentionally restricts analysis to known text suffixes, but ``--out``
    # also carries static assets and extensionless files forward unchanged.
    root, files = _iter_files(source_path, include_all=output is not None)
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
        display = original.name if source_path.is_file() else original.relative_to(root).as_posix()
        items = by_path.get(display, ())
        is_text = original.suffix == ".py" or original.suffix.lower() in _TEXT_SUFFIXES
        changed = False
        count = 0
        if is_text:
            try:
                text = original.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if original.suffix == ".py":
                transformed, count = _replace_python(text, original, items)
            else:
                transformed, count = _replace_text(text, items)
            changed = bool(count and transformed != text)
            if output is not None:
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    raise FileExistsError(f"refusing to overwrite {target}")
                # ``--out`` is a complete, reviewable project tree rather than a
                # sparse patch directory.  Preserve files that have no proven
                # replacement so reviewers can run the generated tree directly.
                target.write_text(transformed, encoding="utf-8")
            elif changed:
                target.write_text(transformed, encoding="utf-8")
        else:
            try:
                raw = original.read_bytes()
            except OSError:
                continue
            if output is not None:
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    raise FileExistsError(f"refusing to overwrite {target}")
                target.write_bytes(raw)
        if changed:
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
