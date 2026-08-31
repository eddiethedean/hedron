"""MATRIX-052 evidence."""

from __future__ import annotations

from dataclasses import replace

import pytest

from hedron_posit import DEFAULT_MATRIX, WorkbenchTopology, run_deployment_matrix
from hedron_posit.cli import main
from hedron_posit.matrix import evaluate_matrix_case


def test_deployment_matrix_protocol_cases() -> None:
    report = run_deployment_matrix()
    assert report["ok"] is True
    ids = {case["id"] for case in report["cases"]}
    assert {"root", "workbench-direct", "workbench-proxy", "connect-native", "external-base"} <= ids
    assert len(DEFAULT_MATRIX) >= 4
    for case in report["cases"]:
        assert case["path_auto_forbidden"] is True
        assert case["cookie_path"].lower() != "auto"
        assert case["cookie_path_expected"] is True
        assert case["cookie_path_matches_mount_helper"] is True
        assert case["href_expected"] is True
        assert case["redirect_expected"] is True
        assert case["stickiness_expected"] is True


def test_matrix_uses_canonical_public_topology_spelling() -> None:
    proxy = next(case for case in DEFAULT_MATRIX if case.id == "workbench-proxy")
    assert proxy.topology is WorkbenchTopology.REVERSE_PROXY
    assert evaluate_matrix_case(proxy)["topology"] == "reverse-proxy"


@pytest.mark.parametrize(
    ("field", "wrong_value", "failed_invariant"),
    [
        ("expected_cookie_path", "/wrong", "cookie_path_expected"),
        ("expected_href", "/wrong", "href_expected"),
        ("expected_redirect", "/wrong", "redirect_expected"),
        ("expected_stickiness", True, "stickiness_expected"),
    ],
)
def test_matrix_independent_expectations_fail_gate(
    field: str, wrong_value: object, failed_invariant: str
) -> None:
    case = replace(DEFAULT_MATRIX[0], id=f"bad-{field}", **{field: wrong_value})
    row = evaluate_matrix_case(case)
    assert row[failed_invariant] is False
    report = run_deployment_matrix((case,))
    assert report["ok"] is False
    assert report["failed"] == [case.id]


def test_matrix_unsafe_mount_fails_gate() -> None:
    case = replace(DEFAULT_MATRIX[0], id="bad-mount", mount="/safe/../escape")
    assert run_deployment_matrix((case,))["ok"] is False


def test_matrix_literal_auto_fails_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    def literal_auto(_mount: str) -> str:
        return "auto"

    monkeypatch.setattr("hedron_posit.matrix.resolve_cookie_path", literal_auto)
    row = evaluate_matrix_case(DEFAULT_MATRIX[0])
    assert row["path_auto_forbidden"] is False
    assert row["ok"] is False


def test_matrix_helper_drift_fails_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    def wrong_path(_mount: str) -> str:
        return "/wrong"

    monkeypatch.setattr("hedron_posit.matrix.cookie_path_for_mount", wrong_path)
    row = evaluate_matrix_case(DEFAULT_MATRIX[0])
    assert row["cookie_path_matches_mount_helper"] is False
    assert row["ok"] is False


def test_cli_check_matrix_exits_zero() -> None:
    assert main(["check", "--matrix", "--format", "json"]) == 0
