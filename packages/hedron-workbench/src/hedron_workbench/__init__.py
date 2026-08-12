"""Posit Workbench / RStudio Server deployment adapter for Hedron.

Importing this package does not wrap applications, register middleware, or
grant trust. ``RS_SERVER_URL`` is discovery-only.
"""

from __future__ import annotations

from hedron_workbench.app import HedronWorkbench
from hedron_workbench.config import ResolvedDeployment, WorkbenchConfig, WorkbenchMode
from hedron_workbench.detect import is_workbench_env, is_workbench_scope
from hedron_workbench.middleware import WorkbenchPathMiddleware, workbenchify
from hedron_workbench.resolve import parse_rserver_url_output, resolve_deployment
from hedron_workbench.runner import export_hedron_state, prepare_app
from hedron_workbench.urls import (
    ExternalBase,
    browser_mount_from_request,
    compose_external_url,
    connect_external_base_from_request,
    local_href,
    mounted_redirect,
    validate_external_base_url,
)

__version__ = "0.29.0"

__all__ = [
    "ResolvedDeployment",
    "ExternalBase",
    "HedronWorkbench",
    "WorkbenchConfig",
    "WorkbenchMode",
    "WorkbenchPathMiddleware",
    "__version__",
    "browser_mount_from_request",
    "compose_external_url",
    "connect_external_base_from_request",
    "export_hedron_state",
    "is_workbench_env",
    "is_workbench_scope",
    "local_href",
    "mounted_redirect",
    "parse_rserver_url_output",
    "prepare_app",
    "resolve_deployment",
    "validate_external_base_url",
    "workbenchify",
]
