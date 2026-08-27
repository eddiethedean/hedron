"""Edron's reviewable Streamlit migration workflow.

The analyzer is deliberately static: it delegates parsing and discovery to the
audited Hedron migration engine, then presents the result in Edron terms.
"""

from edron.migrate.analyze import (
    MAPPING_CATALOG_VERSION,
    SCHEMA_VERSION,
    STREAMLIT_AUDIT_BASELINE,
    analyze_source,
)
from edron.migrate.generate import generate_project

__all__ = [
    "MAPPING_CATALOG_VERSION",
    "SCHEMA_VERSION",
    "STREAMLIT_AUDIT_BASELINE",
    "analyze_source",
    "generate_project",
]
