"""SCENARIO-046: AppScenario covers included bundles; no WorkflowScenario type."""

from __future__ import annotations

import pytest
from pydantic import BaseModel
from tests.unit._helpers_046 import make_app, reset_046

from hedron import Text
from hedron.testing import AppScenario
from hedron_core.bundles import FeatureBundle
from hedron_data import DataWorkspace, DataWorkspacePolicy, InMemoryDataSource


def setup_function() -> None:
    reset_046()


class Item(BaseModel):
    id: str
    title: str = "n"


def test_appscenario_sees_workspace_handles() -> None:
    app = make_app()
    workspace = DataWorkspace(
        name="items",
        model=Item,
        source=InMemoryDataSource([{"id": "1", "title": "n"}], key_field="id"),
        policy=DataWorkspacePolicy(can_read=lambda: True),
    )
    app.include_feature(workspace)
    scenario = AppScenario.from_callables(
        get=lambda path: type("R", (), {"status_code": 200, "text": "ok"})(),
        post=lambda path, **kw: None,
    )
    assert workspace.list_view is not None
    entry = app.interactions.require(workspace.list_view.logical_id)  # type: ignore[union-attr]
    assert entry.kind == "view"
    assert not hasattr(scenario, "workflow")
    import hedron_core.testing as testing

    assert not hasattr(testing, "WorkflowScenario")


def test_generated_scenario_bound() -> None:
    from hedron_core.bundles import MAX_GENERATED_SCENARIOS_PER_BUNDLE, FeatureConflictError

    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    with pytest.raises(FeatureConflictError):
        FeatureBundle(
            logical_id="tests:too-many",
            provider="tests",
            provider_version="0.46.0",
            scenarios=tuple(object() for _ in range(MAX_GENERATED_SCENARIOS_PER_BUNDLE + 1)),
        )
