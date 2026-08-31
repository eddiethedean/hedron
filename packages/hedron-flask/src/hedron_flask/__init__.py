"""Flask adapter for Hedron component rendering and HTMX interactions."""

from __future__ import annotations

from hedron_flask.app import HedronFlask
from hedron_flask.blueprint import HedronBlueprint, wrap_hedron_view
from hedron_flask.catalog import (
    include_feature,
    project_bundle_facts,
    project_catalog_facts,
    refuse_live_host_authority,
)
from hedron_flask.live import POLLING_FALLBACK_SUPPORTED, poll_status_response
from hedron_flask.responses import component_response, interaction_response
from hedron_flask.routing import FlaskUrlReverser, hedron_route
from hedron_flask.static_mount import mount_hedron_static

__version__ = "1.0.3"

__all__ = [
    "FlaskUrlReverser",
    "HedronBlueprint",
    "HedronFlask",
    "POLLING_FALLBACK_SUPPORTED",
    "__version__",
    "component_response",
    "hedron_route",
    "include_feature",
    "interaction_response",
    "mount_hedron_static",
    "poll_status_response",
    "project_bundle_facts",
    "project_catalog_facts",
    "refuse_live_host_authority",
    "wrap_hedron_view",
]
