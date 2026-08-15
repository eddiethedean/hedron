"""Semantic HTMX HTML status responses vs framework-native JSON."""

from __future__ import annotations

from hedron.responses.handlers import (
    install_interaction_handlers as install_interaction_handlers,
)
from hedron.responses.handlers import (
    semantic_error_fragment as semantic_error_fragment,
)
from hedron.responses.handlers import (
    validation_error_fragment as validation_error_fragment,
)

__all__ = [
    "install_interaction_handlers",
    "semantic_error_fragment",
    "validation_error_fragment",
]
