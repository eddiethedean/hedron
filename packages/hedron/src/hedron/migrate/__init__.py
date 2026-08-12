"""Reviewable Streamlit AST migration assistant (RFC-0061 / MIGRATE-031)."""

from __future__ import annotations

SCHEMA_VERSION = "0.31.0-beta"
MAPPING_CATALOG_VERSION = "1.60.0-hedron-0.31"
STREAMLIT_AUDIT_BASELINE = "1.60.x"

__all__ = [
    "MAPPING_CATALOG_VERSION",
    "SCHEMA_VERSION",
    "STREAMLIT_AUDIT_BASELINE",
    "run_migrate_streamlit",
]


def __getattr__(name: str):
    if name == "run_migrate_streamlit":
        from hedron.migrate.cli import run_migrate_streamlit

        return run_migrate_streamlit
    raise AttributeError(name)
