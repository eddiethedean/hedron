"""SURFACE-045: current-surface projections; direct APIs remain usable without catalog."""

from __future__ import annotations

from tests.unit._helpers_045 import make_app, reset_045

from hedron import Text
from hedron_core.catalog import (
    SurfaceProjectionProvider,
    compile_interaction_catalog,
    register_projection_provider,
)


def setup_function() -> None:
    reset_045()


def test_current_surfaces_describe_existing_apis_only() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    for namespace, provider, surface in (
        ("hedron.data", "hedron-data", "DataTable"),
        ("hedron.charts", "hedron-charts", "Chart"),
        ("hedron.elements", "hedron-elements", "web_component_abi"),
        ("hedron.extras", "hedron-extras", "curated extras"),
    ):
        register_projection_provider(
            SurfaceProjectionProvider(
                namespace=namespace,
                provider=provider,
                provider_version="0",
                surface=surface,
                limitations=("no 0.46 factories",),
            )
        )
    catalog = compile_interaction_catalog(app_id=app.hedron_app_id)
    for namespace in ("hedron.data", "hedron.charts", "hedron.elements", "hedron.extras"):
        projection = catalog.projections(namespace)[0]
        assert projection.data["catalog_required"] is False
        assert "DataWorkspace" not in str(projection.data)
        assert "FeatureBundle" not in str(projection.data)
        assert "McpExposure" not in str(projection.data)
    from hedron_data.table import DataTable

    assert DataTable is not None
