"""Opt-in, syntax-only codemods for Edron-owned API spellings."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CodemodReplacement:
    old: str
    new: str
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class CodemodResult:
    source: str
    changed: bool
    replacements: tuple[CodemodReplacement, ...] = ()
    diagnostics: tuple[str, ...] = ()


_RENAMES = {
    "page_function": "function_page",
    "expose": "inherit",
}


def apply_safe_codemod(source: str) -> CodemodResult:
    """Rename only Edron-owned attributes; never import, execute, or rewrite in place."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return CodemodResult(source, False, diagnostics=(f"syntax error: {exc}",))
    edits: list[tuple[int, int, int, str, str, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute) or node.attr not in _RENAMES:
            continue
        if not isinstance(node.value, ast.Name) or node.value.id not in {"app", "ed", "edron"}:
            continue
        end = int(node.end_col_offset or 0)
        start = end - len(node.attr)
        edits.append(
            (
                node.lineno,
                start,
                end,
                node.attr,
                _RENAMES[node.attr],
                node.col_offset,
            )
        )
    if not edits:
        return CodemodResult(source, False)
    lines = source.splitlines(keepends=True)
    replacements: list[CodemodReplacement] = []
    for line_no, start, end, old, new, _ in sorted(edits, reverse=True):
        line = lines[line_no - 1]
        lines[line_no - 1] = line[:start] + new + line[end:]
        replacements.append(CodemodReplacement(old, new, line_no, start + 1))
    replacements.reverse()
    return CodemodResult("".join(lines), True, tuple(replacements))


def codemod_file(source: Path, out: Path | None = None, *, preview: bool = False) -> CodemodResult:
    text = source.read_text(encoding="utf-8")
    result = apply_safe_codemod(text)
    if not preview and out is not None:
        if out.exists():
            raise FileExistsError(f"Refusing to overwrite {out}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result.source, encoding="utf-8")
    return result
