"""Public cache_data / cache_component decorators."""

from __future__ import annotations

from hedron.cache.decorators import cache_component as cache_component
from hedron.cache.decorators import cache_data as cache_data
from hedron.cache.policy import htmx_vary_dimensions as htmx_vary_dimensions

__all__ = ["cache_component", "cache_data", "htmx_vary_dimensions"]
