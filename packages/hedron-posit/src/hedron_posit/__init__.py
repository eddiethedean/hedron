"""Posit Workbench / RStudio Server deployment adapter for Hedron.

Importing this package does not wrap applications, register middleware, or
grant trust. ``RS_SERVER_URL`` is discovery-only.
"""

from __future__ import annotations

from hedron_posit.app import HedronPosit, PositContext
from hedron_posit.config import (
    ConnectConfig,
    DeploymentCapabilities,
    PositConfig,
    PositStatus,
    ResolvedDeployment,
    ResolvedPositDeployment,
    WorkbenchConfig,
    WorkbenchMode,
    WorkbenchTopology,
    resolve_posit_config,
    resolve_posit_deployment,
)
from hedron_posit.cookies import ConnectCookieMode, CookieRegistry, CookieSpec, resolve_cookie_path
from hedron_posit.detect import (
    is_posit_connect_scope,
    is_workbench_env,
    is_workbench_job,
    is_workbench_scope,
)
from hedron_posit.diagnostics import PositDiagnostic
from hedron_posit.interactions import validate_deployed_interactions
from hedron_posit.matrix import DEFAULT_MATRIX, MatrixCase, run_deployment_matrix
from hedron_posit.middleware import WorkbenchPathMiddleware, workbenchify
from hedron_posit.products import PositProduct, resolve_product
from hedron_posit.resolve import parse_rserver_url_output, resolve_deployment
from hedron_posit.runner import export_hedron_state, prepare_app
from hedron_posit.urls import (
    ExternalBase,
    browser_mount_from_request,
    compose_external_url,
    compose_local_url,
    connect_external_base_from_request,
    is_ephemeral_workbench_mount,
    local_href,
    mounted_redirect,
    validate_external_base_url,
)

__version__ = "1.0.9"

__all__ = [
    "ConnectConfig",
    "ConnectCookieMode",
    "CookieRegistry",
    "CookieSpec",
    "DEFAULT_MATRIX",
    "DeploymentCapabilities",
    "ExternalBase",
    "HedronPosit",
    "MatrixCase",
    "PositConfig",
    "PositContext",
    "PositDiagnostic",
    "PositProduct",
    "PositStatus",
    "ResolvedDeployment",
    "ResolvedPositDeployment",
    "WorkbenchConfig",
    "WorkbenchMode",
    "WorkbenchTopology",
    "WorkbenchPathMiddleware",
    "__version__",
    "browser_mount_from_request",
    "compose_external_url",
    "compose_local_url",
    "connect_external_base_from_request",
    "is_ephemeral_workbench_mount",
    "is_posit_connect_scope",
    "export_hedron_state",
    "is_workbench_env",
    "is_workbench_job",
    "is_workbench_scope",
    "local_href",
    "mounted_redirect",
    "parse_rserver_url_output",
    "prepare_app",
    "resolve_cookie_path",
    "resolve_deployment",
    "resolve_posit_deployment",
    "resolve_posit_config",
    "resolve_product",
    "run_deployment_matrix",
    "validate_deployed_interactions",
    "validate_external_base_url",
    "workbenchify",
]
