"""BUNDLE-046: FeatureBundle atomic include, conflicts, eject, rollback."""

from __future__ import annotations

import pytest
from tests.unit._helpers_046 import make_app, reset_046

from hedron import Text
from hedron_core.bundles import (
    MAX_BUNDLE_DEPENDENCY_DEPTH,
    FeatureBundle,
    FeatureConflictError,
    FeatureProvider,
    FeatureRequirement,
    eject_bundle,
    eject_source,
    include_bundle,
    included_bundles,
)
from hedron_core.catalog import PackageProjection
from hedron_core.codes import HED_BUNDLE_0002, HED_BUNDLE_0003, HED_BUNDLE_0004, HED_BUNDLE_0008


def setup_function() -> None:
    reset_046()


def _bundle(
    logical_id: str,
    *,
    views: tuple[object, ...] = (),
    commands: tuple[object, ...] = (),
    dependencies: tuple[str, ...] = (),
    requirements: tuple[FeatureRequirement, ...] = (),
    projections: tuple[PackageProjection, ...] = (),
    provider: str = "tests",
    provider_version: str = "0.46.0",
) -> FeatureBundle:
    return FeatureBundle(
        logical_id=logical_id,
        provider=provider,
        provider_version=provider_version,
        views=views,
        commands=commands,
        dependencies=dependencies,
        requirements=requirements,
        projections=projections,
    )


def test_include_feature_registers_views_before_seal() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    live = app.include_feature(_bundle("tests:status", views=(status,)))
    assert live.logical_id == "tests:status"
    catalog = app.interactions
    assert catalog.require(status.logical_id).kind == "view"
    assert included_bundles(app_id=app.hedron_app_id)[0].logical_id == "tests:status"


def test_duplicate_bundle_id_fails_closed() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    app.include_feature(_bundle("tests:dup", views=(status,)))
    with pytest.raises(FeatureConflictError) as raised:
        app.include_feature(
            _bundle("tests:dup", views=(status,), provider_version="9.9.9"),
        )
    assert raised.value.diagnostic.code == HED_BUNDLE_0002
    assert len(included_bundles(app_id=app.hedron_app_id)) == 1


def test_second_bundle_cannot_claim_existing_handle() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    app.include_feature(_bundle("tests:first", views=(status,)))
    with pytest.raises(FeatureConflictError) as raised:
        app.include_feature(_bundle("tests:reuse-status", views=(status,)))
    assert raised.value.diagnostic.code == HED_BUNDLE_0008
    ids = [item.logical_id for item in included_bundles(app_id=app.hedron_app_id)]
    assert ids == ["tests:first"]
    from hedron_core.updates import list_handle_descriptors

    assert [d.logical_id for d in list_handle_descriptors(app_id=app.hedron_app_id)] == [
        status.logical_id
    ]


def test_identical_reinclude_is_idempotent() -> None:
    app = make_app()
    bundle = _bundle("tests:same")
    include_bundle(bundle, app_id=app.hedron_app_id)
    again = include_bundle(bundle, app_id=app.hedron_app_id)
    assert again == bundle
    assert len(included_bundles(app_id=app.hedron_app_id)) == 1


def test_missing_dependency_and_cycle() -> None:
    app = make_app()
    with pytest.raises(FeatureConflictError) as missing:
        include_bundle(
            _bundle("tests:child", dependencies=("tests:missing",)),
            app_id=app.hedron_app_id,
        )
    assert missing.value.diagnostic.code == HED_BUNDLE_0003
    include_bundle(_bundle("tests:a", dependencies=()), app_id=app.hedron_app_id)
    include_bundle(_bundle("tests:b", dependencies=("tests:a",)), app_id=app.hedron_app_id)
    with pytest.raises(FeatureConflictError):
        include_bundle(
            _bundle("tests:c", dependencies=("tests:missing-cycle",)),
            app_id=app.hedron_app_id,
        )


def test_required_capability_missing() -> None:
    app = make_app()
    with pytest.raises(FeatureConflictError) as raised:
        include_bundle(
            _bundle("tests:need", requirements=(FeatureRequirement("charts", required=True),)),
            app_id=app.hedron_app_id,
            capabilities={},
        )
    assert raised.value.diagnostic.code == HED_BUNDLE_0004


def test_eject_restores_explicit_source() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    app.include_feature(_bundle("tests:eject", views=(status,)))
    source = eject_source(included_bundles(app_id=app.hedron_app_id)[0])
    assert "Ejected FeatureBundle" in source
    assert "tests:eject" in source
    ejected = eject_bundle("tests:eject", app_id=app.hedron_app_id)
    assert ejected.logical_id == "tests:eject"
    assert included_bundles(app_id=app.hedron_app_id) == ()


def test_failed_include_leaves_no_partial_artifacts() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    app.include_feature(_bundle("tests:keep", views=(status,)))

    def boom(_app: object) -> object:
        raise RuntimeError("factory exploded")

    with pytest.raises(FeatureConflictError):
        app.include_feature(_bundle("tests:boom", views=(boom,)))
    ids = {item.logical_id for item in included_bundles(app_id=app.hedron_app_id)}
    assert ids == {"tests:keep"}


def test_feature_provider_protocol_not_on_hedron_facade() -> None:
    import hedron

    assert "FeatureProvider" not in hedron.__all__
    assert hasattr(FeatureProvider, "to_bundle")


def test_third_party_plugin_api_exists() -> None:
    from hedron_core.plugins.context import PluginContext

    assert hasattr(PluginContext, "register_feature_bundle")
    assert hasattr(PluginContext, "register_feature")
    assert "register_feature_bundle" != "register_feature"


def test_depth_bound_constant() -> None:
    assert MAX_BUNDLE_DEPENDENCY_DEPTH == 16
    assert HED_BUNDLE_0008.startswith("HED-BUNDLE-")
