"""Reviewable Streamlit AST migration assistant (RFC-0061 / MIGRATE-031)."""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "0.31.0-beta"
MAPPING_CATALOG_VERSION = "1.60.0-hedron-0.31"
STREAMLIT_AUDIT_BASELINE = "1.60.x"


def run_migrate_streamlit(*args: Any, **kwargs: Any) -> int:
    """Lazy wrapper so ``hedron.migrate`` constants import without pulling the CLI graph."""
    from hedron.migrate.cli import run_migrate_streamlit as _run

    return _run(*args, **kwargs)


def run_migrate_react(*args: Any, **kwargs: Any) -> int:
    """Lazy wrapper for the phase 0.63 React disposition analyzer."""
    from hedron.migrate.cli import run_migrate_react as _run

    return _run(*args, **kwargs)


def run_migrate_api(*args: Any, **kwargs: Any) -> Any:
    """Lazy wrapper for the non-executing 1.0 API migrator."""
    from hedron.migrate.cli import run_migrate_api as _run

    return _run(*args, **kwargs)


__all__ = [
    "MAPPING_CATALOG_VERSION",
    "SCHEMA_VERSION",
    "STREAMLIT_AUDIT_BASELINE",
    "run_migrate_streamlit",
    "run_migrate_react",
    "run_migrate_api",
]
