"""DIFF-050 deterministic catalog/manifest/route/schema diffs."""

from __future__ import annotations

from tests.unit._helpers_050 import reset_050

from hedron_core.registry import register_route, reset_registry_for_tests
from hedron_explorer.services.diff import (
    current_baseline,
    diff_baselines,
    explorer_diff_report,
    snapshot_diff_baseline,
)


def setup_function() -> None:
    reset_050()


def test_identity_diff_is_empty() -> None:
    baseline = current_baseline()
    for key in (
        "catalog",
        "manifest",
        "routes",
        "schema",
        "assets",
        "dependencies",
        "capability_maturity",
    ):
        assert key in baseline
    report = diff_baselines(baseline, baseline)
    assert report["authority"] == "explorer-diff-050"
    for change in report["changes"].values():
        assert change["added"] == []
        assert change["removed"] == []
        assert change["changed"] is False


def test_route_diff_detects_added_and_removed() -> None:
    before = {
        "catalog": "a",
        "manifest": "a",
        "routes": ["page:home:/"],
        "schema": ["x"],
        "assets": [],
        "dependencies": [],
        "capability_maturity": [],
    }
    after = {
        "catalog": "a",
        "manifest": "a",
        "routes": ["page:home:/", "page:other:/other"],
        "schema": ["y"],
        "assets": ["asset:css"],
        "dependencies": [],
        "capability_maturity": [],
    }
    report = diff_baselines(before, after)
    assert report["changes"]["routes"]["added"] == ["page:other:/other"]
    assert report["changes"]["schema"]["changed"] is True
    assert report["changes"]["assets"]["added"] == ["asset:css"]


def test_snapshot_diff_detects_added_routes() -> None:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from hedron_explorer.router import explorer_router

    reset_registry_for_tests()
    app = FastAPI()
    app.include_router(explorer_router(), prefix="/hedron-explorer")
    snapshot_diff_baseline(app)
    register_route(
        kind="page",
        logical_id="demo.other",
        name="other",
        path="/other",
        methods=("GET",),
        operation_id="other",
        include_in_schema=True,
        module="demo",
    )
    report = explorer_diff_report(app)
    assert report["changes"]["routes"]["changed"] is True
    assert any("/other" in item for item in report["changes"]["routes"]["added"])
    client = TestClient(app)
    json_body = client.get("/hedron-explorer/api/diff").json()
    assert json_body["changes"]["routes"]["changed"] is True
    html = client.get("/hedron-explorer/settings")
    assert html.status_code == 200
    assert "Catalog diff" in html.text
    assert "routes" in html.text
