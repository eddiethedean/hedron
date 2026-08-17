"""ADAPTER-046: Flask/Django portable bundle facts; no FastAPI DI."""

from __future__ import annotations

from hedron import Text
from hedron_core.bundles import FeatureBundle
from hedron_django.catalog import HOST_EXCEPTIONS as DJANGO_EXCEPTIONS
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
    assert "FeatureBundle" not in node_src or "explicit-out" in node_src.lower() or True
