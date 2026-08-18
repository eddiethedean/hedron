"""DIFF-050 deterministic catalog/manifest/route/schema diffs."""

from __future__ import annotations

from tests.unit._helpers_050 import reset_050

from hedron_explorer.services.diff import current_baseline, diff_baselines


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
