"""DEPLOY-045: Posit mount-aware production manifest validation."""

from __future__ import annotations

from pathlib import Path

from tests.unit._helpers_045 import make_app, reset_045

from hedron import Text
from hedron_core.catalog import compile_interaction_catalog
from hedron_posit import validate_deployed_interactions


def setup_function() -> None:
    reset_045()


def test_mount_aware_production_validation(tmp_path: Path) -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    catalog = compile_interaction_catalog(app_id=app.hedron_app_id)
    catalog.to_manifest(profile="production").write_json(tmp_path / "interactions.json")
    payload = validate_deployed_interactions(
        catalog=catalog,
        build_dir=tmp_path,
        mount="/rstudio/p/session/app",
    )
    assert payload["ok"] is True
    assert payload["interactions_url"].startswith("/rstudio/p/session/app/")
    assert payload["catalog_fingerprint"] == catalog.fingerprint


def test_fastapi_workbench_does_not_import_hedron_catalog() -> None:
    import fastapi_workbench

    assert "hedron.interactions" not in dir(fastapi_workbench)
    assert not hasattr(fastapi_workbench, "InteractionCatalog")
