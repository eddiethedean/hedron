"""Analysis bounds for non-executing Streamlit migration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnalysisLimits:
    max_files: int = 200
    max_bytes: int = 5_000_000
    max_ast_nodes: int = 200_000
    max_import_depth: int = 8
    max_seconds: float = 60.0


DEFAULT_LIMITS = AnalysisLimits()
