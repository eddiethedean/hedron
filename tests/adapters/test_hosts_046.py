"""ADAPTER-046: Flask/Django portable bundle facts; no FastAPI DI."""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from hedron import Text
from hedron_core.bundles import FeatureBundle, FeatureConflictError, included_bundles
from hedron_core.codes import HED_BUNDLE_0007
from hedron_data import DataWorkspace, DataWorkspacePolicy, InMemoryDataSource
from hedron_django.catalog import HOST_EXCEPTIONS as DJANGO_EXCEPTIONS
from hedron_django.catalog import include_feature as django_include
from hedron_django.catalog import project_bundle_facts as django_bundle
from hedron_flask.catalog import HOST_EXCEPTIONS as FLASK_EXCEPTIONS
from hedron_flask.catalog import include_feature as flask_include
from hedron_flask.catalog import project_bundle_facts as flask_bundle
from tests.unit._helpers_046 import make_app, reset_046


def setup_function() -> None:
    reset_046()


def test_flask_and_django_project_bundle_facts() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    bundle = FeatureBundle(
        logical_id="tests:host",
        provider="tests",
        provider_version="0.46.0",
        views=(status,),
        limitations=("portable",),
    )
    flask_include(bundle, app_id="flask-app")
    flask_facts = flask_bundle("tests:host", app_id="flask-app")
    django_facts = django_bundle("tests:host", app_id="flask-app")
    assert flask_facts["logical_id"] == django_facts["logical_id"] == "tests:host"
    assert flask_facts["fastapi_di"] is False
    assert django_facts["type_schema_production"] is False
    assert FLASK_EXCEPTIONS["csrf"] == DJANGO_EXCEPTIONS["csrf"] == "live_host_authoritative"


def test_node_java_remain_explicit_out() -> None:
    from pathlib import Path

    node = Path("packages/hedron-runtime-node")
    java = Path("packages/hedron-runtime-java")
    assert node.is_dir()
    assert java.is_dir()
    node_src = "\n".join(path.read_text(encoding="utf-8") for path in node.rglob("*.md"))
    assert "FeatureBundle" not in node_src or "explicit-out" in node_src.lower()


class Row(BaseModel):
    id: str
    title: str = "n"


def _workspace() -> DataWorkspace[Row]:
    return DataWorkspace(
        name="notes",
        model=Row,
        source=InMemoryDataSource([{"id": "1", "title": "n"}], key_field="id"),
        policy=DataWorkspacePolicy(can_read=lambda: True),
    )


def test_flask_and_django_refuse_unmaterialized_workspace() -> None:
    flask_ws = _workspace()
    with pytest.raises(FeatureConflictError) as flask_raised:
        flask_include(flask_ws, app_id="flask-app")
    assert flask_raised.value.diagnostic.code == HED_BUNDLE_0007
    assert flask_ws.list_view is None
    assert included_bundles(app_id="flask-app") == ()

    django_ws = _workspace()
    with pytest.raises(FeatureConflictError) as django_raised:
        django_include(django_ws, app_id="django-app")
    assert django_raised.value.diagnostic.code == HED_BUNDLE_0007
    assert django_ws.list_view is None
    assert included_bundles(app_id="django-app") == ()
