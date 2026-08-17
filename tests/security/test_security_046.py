"""SECURITY-046: bundle ids are not capabilities; MCP/Gradio opt-in; no inferred authz."""

from __future__ import annotations

from tests.unit._helpers_046 import make_app, reset_046

from hedron import Text
from hedron_core.bundles import FeatureBundle, included_bundles
from hedron_mcp import McpProjection


def setup_function() -> None:
    reset_046()


def test_bundle_id_is_not_a_capability() -> None:
    app = make_app()

    @app.refreshable
    def secret_card():
        return Text("ok")

    app.include_feature(
        FeatureBundle(
            logical_id="tests:secret",
            provider="tests",
            provider_version="0.46.0",
            views=(secret_card,),
        )
    )
    bundle = included_bundles(app_id=app.hedron_app_id)[0]
    assert bundle.logical_id == "tests:secret"
    mapping = app.interactions.require(secret_card.logical_id).as_mapping()
    assert "authorize" not in mapping
    assert "capability" not in str(mapping.get("projections") or {})


def test_catalog_consume_does_not_enable_mcp() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    projection = McpProjection(enabled=False)
    projection.consume_catalog(app.interactions)
    assert projection.enabled is False
    assert projection.tools == ()
