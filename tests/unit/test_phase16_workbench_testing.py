"""Phase 0.16 workbench-flow testing helpers."""

from __future__ import annotations

import pytest

from hedron.testing import (
    AppScenario,
    assert_action_authorized,
    assert_http_fallback_present,
    assert_transform_plan_bounded,
    image_region_fixture,
    json_document_fixture,
    sandbox_budget_fixture,
    transform_plan_fixture,
    tree_document_fixture,
    workbench_action_fixture,
)
from hedron.testing.adapters import AdapterResponse


def test_tree_and_json_fixtures() -> None:
    tree = tree_document_fixture()
    assert tree[0]["id"] == "root"
    doc = json_document_fixture(payload={"ok": True}, schema={"type": "object"})
    assert doc["document"]["ok"] is True
    assert "schema" in doc


def test_image_region_and_sandbox_fixtures() -> None:
    region = image_region_fixture(kind="lasso", points=((0.0, 0.0), (1.0, 1.0)))
    assert region["kind"] == "lasso"
    budget = sandbox_budget_fixture(cpu_ms=1000, packages=("numpy",))
    assert budget.cpu_ms == 1000
    with pytest.raises(ValueError):
        image_region_fixture(points=((2.0, 0.0),))


def test_transform_plan_and_action_asserts() -> None:
    plan = transform_plan_fixture(limit=25)
    assert_transform_plan_bounded(plan, max_rows=100)
    with pytest.raises(AssertionError):
        assert_transform_plan_bounded(plan, max_rows=5)
    action = workbench_action_fixture(authorized=False)
    assert_action_authorized(action, expect=False)


def test_app_scenario_workbench_helpers() -> None:
    def get(path: str, **kwargs: object) -> AdapterResponse:
        return AdapterResponse(
            status_code=200,
            body='<textarea name="code" data-http-fallback="textarea"></textarea>',
            headers={},
            cookies={},
        )

    def post(path: str, **kwargs: object) -> AdapterResponse:
        return AdapterResponse(status_code=200, body="ok", headers={}, cookies={})

    scenario = AppScenario.from_callables(get, post)
    scenario.get("/")
    scenario.assert_http_fallback_present("textarea")
    scenario.assert_transform_plan_bounded(transform_plan_fixture(limit=10), max_rows=50)
    scenario.assert_action_authorized(workbench_action_fixture(authorized=True))
    assert_http_fallback_present(scenario.last_response.body, token="textarea")  # type: ignore[union-attr]
