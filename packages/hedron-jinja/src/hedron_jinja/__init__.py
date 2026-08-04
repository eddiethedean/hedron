"""Public API for Hedron's Jinja integration."""

from __future__ import annotations

from hedron_jinja.contracts import TemplateSource, TemplateSpec
from hedron_jinja.integration import HedronJinja, HedronJinjaExtension

__version__ = "0.9.0"

__all__ = [
    "HedronJinja",
    "HedronJinjaExtension",
    "TemplateSource",
    "TemplateSpec",
    "__version__",
]
