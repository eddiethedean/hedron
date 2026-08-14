"""hedron-elements: Alpha Web Component ABI and first-party elements."""

from __future__ import annotations

from hedron_elements.example import Example
from hedron_elements.markup import render_element_markup
from hedron_elements.state import (
    OwnershipMode,
    apply_incoming_update,
    validate_field_ownership,
)

__version__ = "0.39.0"

__all__ = [
    "Example",
    "OwnershipMode",
    "apply_incoming_update",
    "render_element_markup",
    "validate_field_ownership",
    "__version__",
]
