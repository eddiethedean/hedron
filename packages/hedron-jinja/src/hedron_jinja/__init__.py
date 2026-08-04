"""Public API for Hedron's Jinja integration."""

from __future__ import annotations

from hedron_jinja.contracts import (
    HdjContext,
    TemplateCapabilities,
    TemplateDeclaration,
    TemplateKind,
    TemplateSource,
    TemplateSpec,
)
from hedron_jinja.integration import HedronJinja, HedronJinjaExtension, TwoPhaseStream

__version__ = "0.10.0"

__all__ = [
    "HedronJinja",
    "HedronJinjaExtension",
    "HdjContext",
    "TemplateCapabilities",
    "TemplateDeclaration",
    "TemplateKind",
    "TemplateSource",
    "TemplateSpec",
    "TwoPhaseStream",
    "__version__",
]
