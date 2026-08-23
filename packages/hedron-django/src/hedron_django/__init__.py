"""Django adapter for Hedron component rendering and HTMX interactions."""

from __future__ import annotations

from hedron_django.app import HedronDjango
from hedron_django.apps import HedronDjangoConfig
from hedron_django.catalog import (
    include_feature,
    project_bundle_facts,
    project_catalog_facts,
    refuse_live_host_authority,
)
from hedron_django.forms import (
    csrf_hidden_input,
    form_to_nodes,
    formset_to_nodes,
    validation_interaction,
)
from hedron_django.live import POLLING_FALLBACK_SUPPORTED, poll_status_response
from hedron_django.middleware import HedronSecurityHeadersMiddleware
from hedron_django.responses import component_response, interaction_response
from hedron_django.routing import DjangoUrlReverser, hedron_view
from hedron_django.static_mount import hedron_static_urlpatterns
from hedron_django.urls import component_path, hedron_paths, include_component_path

__version__ = "0.60.0"

__all__ = [
    "DjangoUrlReverser",
    "HedronDjango",
    "HedronDjangoConfig",
    "HedronSecurityHeadersMiddleware",
    "POLLING_FALLBACK_SUPPORTED",
    "__version__",
    "component_path",
    "component_response",
    "csrf_hidden_input",
    "form_to_nodes",
    "formset_to_nodes",
    "hedron_paths",
    "hedron_static_urlpatterns",
    "hedron_view",
    "include_component_path",
    "include_feature",
    "interaction_response",
    "poll_status_response",
    "project_bundle_facts",
    "project_catalog_facts",
    "refuse_live_host_authority",
    "validation_interaction",
]
