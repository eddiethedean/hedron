"""Posit Workbench compatibility package for Hedron.

Preferred facade is ``hedron_posit.HedronPosit``. This package retains
``HedronWorkbench`` as a thin subclass and re-exports the public 0.32 surface.
"""

from __future__ import annotations

from hedron_posit import (
    ConnectConfig,
    ConnectCookieMode,
    DeploymentCapabilities,
    ExternalBase,
    PositConfig,
    PositProduct,
    PositStatus,
    ResolvedDeployment,
    ResolvedPositDeployment,
    WorkbenchConfig,
    WorkbenchMode,
    WorkbenchPathMiddleware,
    WorkbenchTopology,
    browser_mount_from_request,
    compose_external_url,
    connect_external_base_from_request,
    export_hedron_state,
    is_ephemeral_workbench_mount,
    is_posit_connect_scope,
    is_workbench_env,
    is_workbench_job,
    is_workbench_scope,
    local_href,
    mounted_redirect,
    parse_rserver_url_output,
    prepare_app,
    resolve_deployment,
    resolve_posit_deployment,
    resolve_product,
    validate_external_base_url,
    workbenchify,
)
from hedron_workbench.app import HedronWorkbench

__version__ = "0.50.1"

__all__ = [
    "ConnectConfig",
    "ConnectCookieMode",
    "ResolvedDeployment",
    "ResolvedPositDeployment",
    "DeploymentCapabilities",
    "ExternalBase",
    "HedronWorkbench",
    "PositConfig",
    "PositProduct",
    "PositStatus",
    "WorkbenchConfig",
    "WorkbenchMode",
    "WorkbenchTopology",
    "WorkbenchPathMiddleware",
    "__version__",
    "browser_mount_from_request",
    "compose_external_url",
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
    "resolve_deployment",
    "resolve_posit_deployment",
    "resolve_product",
    "validate_external_base_url",
    "workbenchify",
]
