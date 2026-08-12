"""Workbench environment and scope detection. No trust grants."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping

from starlette.types import Scope

from hedron_workbench.config import WorkbenchMode

_PROXY_ROOT = re.compile(r"^/proxy/\d+(?P<rest>/.*)$")
_TRUTHY = frozenset({"1", "true", "yes", "y", "on"})


def truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in _TRUTHY


def is_workbench_forced(environ: Mapping[str, str] | None = None) -> bool:
    env = os.environ if environ is None else environ
    namespaced = env.get("HEDRON_WORKBENCH_FORCE")
    if namespaced is not None and str(namespaced).strip():
        return truthy(str(namespaced))
    return truthy(env.get("WORKBENCH_FORCE"))


def rs_server_url(environ: Mapping[str, str] | None = None) -> str:
    env = os.environ if environ is None else environ
    return str(env.get("RS_SERVER_URL") or "").strip()


def is_workbench_env(environ: Mapping[str, str] | None = None) -> bool:
    """True when discovery *may* run. Does not enable redirect mode or trust."""
    return bool(rs_server_url(environ)) or is_workbench_forced(environ)


def is_workbench_job(environ: Mapping[str, str] | None = None) -> bool:
    """Detect an explicitly marked or audited non-interactive Workbench job."""
    env = os.environ if environ is None else environ
    marker = env.get("HEDRON_WORKBENCH_JOB")
    if marker is not None and str(marker).strip():
        return truthy(str(marker))
    # Posit's audited-job contract exposes this path to job processes.
    return bool(rs_server_url(env) and str(env.get("AUDIT_DETAILS_PATH") or "").strip())


def is_posit_connect_scope(scope: Scope, environ: Mapping[str, str] | None = None) -> bool:
    """Recognize Connect's audited ASGI proxy contract without granting trust."""
    env = os.environ if environ is None else environ
    if str(env.get("POSIT_PRODUCT") or "").strip().upper() != "CONNECT":
        return False
    headers = scope.get("headers") or ()
    base_headers = [
        value for name, value in headers if bytes(name).lower() == b"rstudio-connect-app-base-url"
    ]
    return len(base_headers) == 1 and bool(str(scope.get("root_path") or "").strip())


def path_has_encoded_absolute_url(path: str) -> bool:
    candidate = path.lstrip("/").lower()
    return candidate.startswith(("http%3a", "https%3a", "http://", "https://"))


def is_workbench_scope(scope: Scope) -> bool:
    path = str(scope.get("path") or "")
    if path_has_encoded_absolute_url(path):
        return True
    root_path = str(scope.get("root_path") or "").rstrip("/")
    if not root_path:
        return False
    if path == root_path or path.startswith(root_path + "/"):
        return True
    match = _PROXY_ROOT.match(root_path)
    if match:
        rest = (match.group("rest") or "").rstrip("/")
        if rest and (path == rest or path.startswith(rest + "/")):
            return True
    return False


def should_normalize(*, scope: Scope, mode: WorkbenchMode) -> bool:
    if mode is WorkbenchMode.ON:
        return True
    if mode is WorkbenchMode.OFF:
        return False
    return is_workbench_scope(scope)
