"""Protocol-level deployment matrix for HedronPosit check --matrix."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hedron.mount import cookie_path_for_mount, normalize_mount_path
from hedron_posit.cookies import resolve_cookie_path
from hedron_posit.urls import compose_local_url


@dataclass(frozen=True, slots=True)
class MatrixCase:
    id: str
    label: str
    mount: str
    product: str


DEFAULT_MATRIX: tuple[MatrixCase, ...] = (
    MatrixCase("root", "ordinary root hosting", "/", "hedron"),
    MatrixCase("workbench-direct", "Workbench direct", "/s/abc/p/xyz/", "workbench"),
    MatrixCase("workbench-proxy", "Workbench reverse proxy", "/s/abc/p/xyz/", "workbench"),
    MatrixCase("connect-native", "Connect native", "/content/app1/", "connect"),
    MatrixCase("external-base", "explicit external base", "/apps/demo/", "hedron"),
)


def evaluate_matrix_case(case: MatrixCase) -> dict[str, Any]:
    """Return redacted protocol expectations for one deployment mode."""
    mount = normalize_mount_path(case.mount)
    cookie_path = resolve_cookie_path(mount)
    href = compose_local_url("/profile", mount=mount, query={"tab": "1"}, fragment="main")
    redirect = compose_local_url("/login", mount=mount, query={"next": "/profile"})
    return {
        "id": case.id,
        "label": case.label,
        "product": case.product,
        "mount": mount,
        "cookie_path": cookie_path,
        "href_sample": href,
        "redirect_sample": redirect,
        "path_auto_forbidden": cookie_path.lower() != "auto",
        "cookie_path_matches_mount_helper": cookie_path == cookie_path_for_mount(mount or "/"),
        "ok": cookie_path.lower() != "auto",
    }


def run_deployment_matrix(
    cases: tuple[MatrixCase, ...] = DEFAULT_MATRIX,
) -> dict[str, Any]:
    results = [evaluate_matrix_case(case) for case in cases]
    failed = [row["id"] for row in results if not row["ok"]]
    return {
        "cases": results,
        "failed": failed,
        "ok": not failed,
    }


__all__ = [
    "DEFAULT_MATRIX",
    "MatrixCase",
    "evaluate_matrix_case",
    "run_deployment_matrix",
]
