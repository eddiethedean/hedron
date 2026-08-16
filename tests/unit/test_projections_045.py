"""PROJECTION-045: namespaced providers, disable/uninstall, trusted-only."""

from __future__ import annotations

import pytest
from tests.unit._helpers_045 import make_app, reset_045

from hedron import Text
from hedron_core.catalog import (
    CatalogVersionError,
    SurfaceProjectionProvider,
    compile_interaction_catalog,
    register_projection_provider,
    unregister_projection_provider,
)
from hedron_core.codes import HED_PROJECTION_0001, HED_PROJECTION_0004


def setup_function() -> None:
    reset_045()


def test_surface_provider_attaches_catalog_projection() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    register_projection_provider(
        SurfaceProjectionProvider(
            namespace="hedron.data",
            provider="hedron-data",
            provider_version="0.44.0",
            surface="DataTable",
        )
    )
    catalog = compile_interaction_catalog(app_id=app.hedron_app_id)
    projections = catalog.projections("hedron.data")
    assert len(projections) == 1
    assert projections[0].data["direct_apis"] is True
    assert projections[0].data["exposure"] is False
    unregister_projection_provider("hedron.data")
    catalog2 = compile_interaction_catalog(app_id=app.hedron_app_id)
    assert catalog2.projections("hedron.data") == ()
    assert catalog2.require(status.logical_id).kind == "view"


def test_duplicate_namespace_fails() -> None:
    register_projection_provider(
        SurfaceProjectionProvider(
            namespace="hedron.data",
            provider="a",
            provider_version="1",
            surface="a",
        )
    )
    with pytest.raises(CatalogVersionError) as caught:
        register_projection_provider(
            SurfaceProjectionProvider(
                namespace="hedron.data",
                provider="b",
                provider_version="1",
                surface="b",
            )
        )
    assert caught.value.diagnostic.code == HED_PROJECTION_0001


def test_reserved_namespace_hedron_type_refused() -> None:
    with pytest.raises(CatalogVersionError) as caught:
        register_projection_provider(
            SurfaceProjectionProvider(
                namespace="hedron.type",
                provider="evil",
                provider_version="1",
                surface="nope",
            )
        )
    assert caught.value.diagnostic.code == HED_PROJECTION_0001


def test_untrusted_provider_invocation() -> None:
    provider = SurfaceProjectionProvider(
        namespace="example.kit",
        provider="kit",
        provider_version="1",
        surface="demo",
    )
    with pytest.raises(CatalogVersionError) as caught:
        provider.project((), catalog_fingerprint="0" * 32, trusted=False)
    assert caught.value.diagnostic.code == HED_PROJECTION_0004
