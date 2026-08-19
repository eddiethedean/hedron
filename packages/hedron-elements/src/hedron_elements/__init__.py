"""hedron-elements: Beta Web Component ABI and first-party elements."""

from __future__ import annotations

from hedron_elements.author import (
    AUTHOR_SURFACES,
    REQUIRED_DIAGNOSTICS_PREFIX_GUIDANCE,
    REQUIRED_ELEMENT_META_KEYS,
    diagnostics_prefix_guidance,
    packaging_checklist,
    validate_element_author_meta,
)
from hedron_elements.composition import BrowserTrace, CompositionEdge, validate_trace_payload
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
from hedron_elements.transfer import DraftTransferEnvelope, subject_fingerprint

__version__ = "0.50.2"

__all__ = [
    "AUTHOR_SURFACES",
    "DISPOSITIONS",
    "BrowserTrace",
    "CompositionEdge",
    "DraftTransferEnvelope",
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
    "validate_trace_payload",
    "subject_fingerprint",
    "__version__",
]
