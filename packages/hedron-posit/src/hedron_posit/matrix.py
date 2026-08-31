"""Protocol-level deployment matrix for ``hedron-posit check --matrix``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from hedron.mount import cookie_path_for_mount, normalize_mount_path
from hedron_posit.config import WorkbenchTopology
from hedron_posit.cookies import resolve_cookie_path
from hedron_posit.urls import compose_local_url

MatrixProduct = Literal["hedron", "workbench", "connect"]


@dataclass(frozen=True, slots=True)
class MatrixCase:
    """One independently specified deployment expectation."""

    id: str
    label: str
    mount: str
    product: MatrixProduct
    expected_cookie_path: str
    expected_href: str
    expected_redirect: str
    topology: WorkbenchTopology = WorkbenchTopology.LOCAL
    expected_stickiness: bool = False
    notes: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "topology", WorkbenchTopology.parse(self.topology))


DEFAULT_MATRIX: tuple[MatrixCase, ...] = (
    MatrixCase(
        "root",
        "ordinary root hosting",
        "/",
        "hedron",
        "/",
        "/profile?tab=1#main",
        "/login?next=%2Fprofile",
    ),
    MatrixCase(
        "workbench-direct",
        "Workbench direct",
        "/s/abc/p/xyz/",
        "workbench",
        "/s/abc/p/xyz",
        "/s/abc/p/xyz/profile?tab=1#main",
        "/s/abc/p/xyz/login?next=%2Fprofile",
        notes="session stickiness not required",
    ),
    MatrixCase(
        "workbench-proxy",
        "Workbench reverse proxy",
        "/s/abc/p/xyz/",
        "workbench",
        "/s/abc/p/xyz",
        "/s/abc/p/xyz/profile?tab=1#main",
        "/s/abc/p/xyz/login?next=%2Fprofile",
        topology=WorkbenchTopology.REVERSE_PROXY,
        expected_stickiness=True,
        notes="load-balanced deployments require Workbench session stickiness",
    ),
    MatrixCase(
        "connect-native",
        "Connect native",
        "/content/app1/",
        "connect",
        "/content/app1",
        "/content/app1/profile?tab=1#main",
        "/content/app1/login?next=%2Fprofile",
    ),
    MatrixCase(
        "external-base",
        "explicit external base",
        "/apps/demo/",
        "hedron",
        "/apps/demo",
        "/apps/demo/profile?tab=1#main",
        "/apps/demo/login?next=%2Fprofile",
    ),
)


def evaluate_matrix_case(case: MatrixCase) -> dict[str, Any]:
    """Evaluate every invariant against independent fixture expectations."""
    mount = normalize_mount_path(case.mount)
    if case.mount not in {"", "/"} and not mount:
        return {
            "id": case.id,
            "label": case.label,
            "product": case.product,
            "topology": case.topology.value,
            "notes": case.notes,
            "mount": case.mount,
            "mount_valid": False,
            "cookie_path": "",
            "cookie_path_expected": False,
            "href_sample": "",
            "href_expected": False,
            "redirect_sample": "",
            "redirect_expected": False,
            "path_auto_forbidden": False,
            "cookie_path_matches_mount_helper": False,
            "session_stickiness_required": False,
            "stickiness_expected": False,
            "ok": False,
            "error": "unsafe mount path",
        }
    cookie_path = resolve_cookie_path(mount)
    href = compose_local_url("/profile", mount=mount, query={"tab": "1"}, fragment="main")
    redirect = compose_local_url("/login", mount=mount, query={"next": "/profile"})
    stickiness_required = case.topology is WorkbenchTopology.REVERSE_PROXY
    invariants = {
        "mount_valid": True,
        "path_auto_forbidden": cookie_path.lower() != "auto",
        "cookie_path_expected": cookie_path == case.expected_cookie_path,
        "cookie_path_matches_mount_helper": cookie_path == cookie_path_for_mount(mount or "/"),
        "href_expected": href == case.expected_href,
        "redirect_expected": redirect == case.expected_redirect,
        "stickiness_expected": stickiness_required == case.expected_stickiness,
    }
    return {
        "id": case.id,
        "label": case.label,
        "product": case.product,
        "topology": case.topology.value,
        "notes": case.notes,
        "mount": mount,
        "cookie_path": cookie_path,
        "href_sample": href,
        "redirect_sample": redirect,
        "session_stickiness_required": stickiness_required,
        **invariants,
        "ok": all(invariants.values()),
    }


def run_deployment_matrix(
    cases: tuple[MatrixCase, ...] = DEFAULT_MATRIX,
) -> dict[str, Any]:
    results = [evaluate_matrix_case(case) for case in cases]
    failed = [row["id"] for row in results if not row["ok"]]
    return {"cases": results, "failed": failed, "ok": not failed}


__all__ = [
    "DEFAULT_MATRIX",
    "MatrixCase",
    "MatrixProduct",
    "evaluate_matrix_case",
    "run_deployment_matrix",
]
