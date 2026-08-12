"""Bounded AST parsing without executing application code."""

from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass
from pathlib import Path

from hedron.migrate.ir import SourceUnit
from hedron.migrate.limits import DEFAULT_LIMITS, AnalysisLimits

_FEATURE_BY_VERSION: dict[str, int] = {
    "3.11": 11,
    "3.12": 12,
    "3.13": 13,
    "3.14": 14,
}


@dataclass(frozen=True, slots=True)
class ParsedUnit:
    unit: SourceUnit
    tree: ast.AST
    source: str
    node_count: int


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def count_ast_nodes(tree: ast.AST) -> int:
    return sum(1 for _ in ast.walk(tree))


def parse_file(
    path: Path,
    *,
    project_root: Path,
    python_version: str = "3.12",
    is_entrypoint: bool = False,
    is_page: bool = False,
    limits: AnalysisLimits = DEFAULT_LIMITS,
    bytes_so_far: int = 0,
    nodes_so_far: int = 0,
) -> ParsedUnit:
    raw = path.read_bytes()
    if len(raw) + bytes_so_far > limits.max_bytes:
        raise ValueError(
            f"byte limit exceeded while reading {path} "
            f"({len(raw) + bytes_so_far} > {limits.max_bytes})"
        )
    text = raw.decode("utf-8")
    feature = _FEATURE_BY_VERSION.get(python_version)
    if feature is None:
        raise ValueError(f"unsupported --python-version {python_version!r}")
    try:
        tree = ast.parse(text, filename=str(path), feature_version=feature)
    except SyntaxError as exc:
        raise ValueError(f"syntax error in {path}: {exc}") from exc
    nodes = count_ast_nodes(tree)
    if nodes + nodes_so_far > limits.max_ast_nodes:
        raise ValueError(
            f"AST node limit exceeded in {path} ({nodes + nodes_so_far} > {limits.max_ast_nodes})"
        )
    rel = str(path.resolve().relative_to(project_root.resolve()))
    unit = SourceUnit(
        path=str(path.resolve()),
        content_hash=content_hash(text),
        relative_path=rel,
        is_entrypoint=is_entrypoint,
        is_page=is_page,
    )
    return ParsedUnit(unit=unit, tree=tree, source=text, node_count=nodes)
