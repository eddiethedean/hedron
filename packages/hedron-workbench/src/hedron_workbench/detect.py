"""Compatibility re-export from hedron_posit.detect."""

from __future__ import annotations

from hedron_posit.detect import (
    is_posit_connect_scope,
    is_workbench_env,
    is_workbench_forced,
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
