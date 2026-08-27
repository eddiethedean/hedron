"""ADAPTER-047 FastAPI/Flask/Django/Posit/Workbench portable facts."""

from __future__ import annotations

from tests.unit._helpers_046 import make_app, reset_046

from hedron_django.catalog import HOST_EXCEPTIONS as DJANGO_EXCEPTIONS
from hedron_django.catalog import project_bundle_facts as django_bundle
from hedron_flask.catalog import HOST_EXCEPTIONS as FLASK_EXCEPTIONS
from hedron_flask.catalog import include_feature as flask_include
from hedron_flask.catalog import project_bundle_facts as flask_bundle
from hedron_maps import SYNTHETIC_ARCHIVE
from hedron_maps.mbtiles import MBTilesArchive


def setup_function() -> None:
    reset_046()


def test_fastapi_include_feature_mbtiles() -> None:
    app = make_app()
    archive = MBTilesArchive(archive_id="synthetic", path=SYNTHETIC_ARCHIVE)
    live = app.include_feature(archive)
    paths = [getattr(route, "path", "") for route in app.routes]
    assert any("hedron-maps/mbtiles/synthetic" in path for path in paths)
    assert live.provider == "hedron-maps"


def test_flask_and_django_are_projection_adapters() -> None:
    archive = MBTilesArchive(archive_id="synthetic", path=SYNTHETIC_ARCHIVE)
    live = archive.to_bundle()
    portable = type(live)(
        logical_id=live.logical_id,
        provider=live.provider,
        provider_version=live.provider_version,
        projections=live.projections,
        limitations=live.limitations,
        requirements=live.requirements,
    )
    flask_include(portable, app_id="flask-app")
    facts = flask_bundle(portable.logical_id, app_id="flask-app")
    django_facts = django_bundle(portable.logical_id, app_id="flask-app")
    assert facts["fastapi_di"] is False
    assert django_facts["fastapi_di"] is False
    assert facts["disposition"] == "projection_adapter"
    assert FLASK_EXCEPTIONS["csrf"] == DJANGO_EXCEPTIONS["csrf"] == "live_host_authoritative"


def test_posit_workbench_packages_present() -> None:
    from pathlib import Path

    assert Path("packages/hedron-posit").is_dir()
    posit = Path("packages/hedron-posit/src/hedron_posit/app.py").read_text(encoding="utf-8")
    assert "root_path" in posit
    workbench = Path("packages/hedron-posit").joinpath("src")
    assert workbench.is_dir()
