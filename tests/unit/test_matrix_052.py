"""MATRIX-052 evidence."""

from __future__ import annotations

from hedron_posit import DEFAULT_MATRIX, run_deployment_matrix
from hedron_posit.cli import main


def test_deployment_matrix_protocol_cases() -> None:
    report = run_deployment_matrix()
    assert report["ok"] is True
    ids = {case["id"] for case in report["cases"]}
    assert {"root", "workbench-direct", "workbench-proxy", "connect-native", "external-base"} <= ids
    assert len(DEFAULT_MATRIX) >= 4
    for case in report["cases"]:
        assert case["path_auto_forbidden"] is True
        assert case["cookie_path"].lower() != "auto"


def test_cli_check_matrix_exits_zero() -> None:
    assert main(["check", "--matrix", "--format", "json"]) == 0
