"""Posit Workbench / RStudio Server deployment adapter for FastAPI ASGI apps.

Importing this package does not wrap applications, register middleware, or
grant trust. ``RS_SERVER_URL`` is discovery-only.
"""

from __future__ import annotations

from fastapi_workbench.config import (
    DeploymentCapabilities,
    ResolvedDeployment,
    WorkbenchConfig,
    WorkbenchMode,
    WorkbenchTopology,
)
from fastapi_workbench.detect import (
    is_posit_connect_scope,
    is_workbench_env,
    is_workbench_job,
    is_workbench_scope,
)
from fastapi_workbench.middleware import WorkbenchPathMiddleware, workbenchify
from fastapi_workbench.resolve import (
    RESOLVED_MODE_ENV,
    RESOLVED_MOUNT_ENV,
    RESOLVED_PUBLIC_BASE_ENV,
    RESOLVED_SOURCE_ENV,
    ROOT_PATH_ENV,
    parse_rserver_url_output,
    resolve_deployment,
)
from fastapi_workbench.runner import export_workbench_state, prepare_app
from fastapi_workbench.urls import is_ephemeral_workbench_mount, normalize_http_origin

__version__ = "1.0.10"

__all__ = [
    "ROOT_PATH_ENV",
    "RESOLVED_MOUNT_ENV",
    "RESOLVED_PUBLIC_BASE_ENV",
    "RESOLVED_MODE_ENV",
    "RESOLVED_SOURCE_ENV",
    "ResolvedDeployment",
    "DeploymentCapabilities",
    "WorkbenchConfig",
    "WorkbenchMode",
    "WorkbenchTopology",
    "WorkbenchPathMiddleware",
    "__version__",
    "export_workbench_state",
    "is_ephemeral_workbench_mount",
    "is_posit_connect_scope",
    "is_workbench_env",
    "is_workbench_job",
    "is_workbench_scope",
    "normalize_http_origin",
    "parse_rserver_url_output",
    "prepare_app",
    "resolve_deployment",
    "workbenchify",
]
