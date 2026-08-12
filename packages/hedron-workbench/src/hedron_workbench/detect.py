"""Workbench environment and scope detection. No trust grants."""

from __future__ import annotations

import os
from collections.abc import Mapping

from fastapi_workbench.detect import (
    is_posit_connect_scope,
    is_workbench_env,
    is_workbench_job,
    is_workbench_scope,
    path_has_encoded_absolute_url,
    rs_server_url,
    truthy,
)

__all__ = [
    "is_posit_connect_scope",
    "is_workbench_env",
    "is_workbench_forced",
    "is_workbench_job",
    "is_workbench_scope",
    "path_has_encoded_absolute_url",
    "rs_server_url",
    "truthy",
]


def is_workbench_forced(environ: Mapping[str, str] | None = None) -> bool:
    env = os.environ if environ is None else environ
    namespaced = env.get("HEDRON_WORKBENCH_FORCE")
    if namespaced is not None and str(namespaced).strip():
        return truthy(str(namespaced))
    return truthy(env.get("WORKBENCH_FORCE"))
