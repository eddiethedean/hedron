"""hedron-elements: Alpha Web Component ABI and first-party elements."""

from __future__ import annotations

from hedron_elements.author import (
    AUTHOR_SURFACES,
    REQUIRED_DIAGNOSTICS_PREFIX_GUIDANCE,
    REQUIRED_ELEMENT_META_KEYS,
    diagnostics_prefix_guidance,
    packaging_checklist,
    validate_element_author_meta,
)
from hedron_elements.example import Example
from hedron_elements.markup import render_element_markup
from hedron_elements.migrate import (
    DISPOSITIONS,
    NON_FITS,
    ReactMigrationMatrix,
    matrix_rows,
)
from hedron_elements.state import (
    OwnershipMode,
    apply_incoming_update,
    validate_field_ownership,
)

__version__ = "0.40.0"

__all__ = [
    "AUTHOR_SURFACES",
    "DISPOSITIONS",
    "Example",
    "NON_FITS",
    "OwnershipMode",
    "REQUIRED_DIAGNOSTICS_PREFIX_GUIDANCE",
    "REQUIRED_ELEMENT_META_KEYS",
    "ReactMigrationMatrix",
    "apply_incoming_update",
    "diagnostics_prefix_guidance",
    "matrix_rows",
    "packaging_checklist",
    "render_element_markup",
    "validate_element_author_meta",
    "validate_field_ownership",
    "__version__",
]
