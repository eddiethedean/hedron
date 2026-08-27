"""Phase 0.6 Edron composition, navigation, promotion, and evidence contracts."""

from __future__ import annotations

import pytest

import edron as ed
import hedron_core
from hedron_core.registry import AssetMeta, reset_registry_for_tests


def _app() -> ed.App:
    reset_registry_for_tests()
    hedron_core._register_builtins()  # type: ignore[attr-defined]
    return ed.App(title="phase06", security="development", session_secret="test-secret")


def test_package_registration_is_native_and_manifest_is_bounded() -> None:
    app = _app()
    package = ed.feature_package(
        "acme.dashboard",
        "0.1.0",
        assets=(
            AssetMeta(
                logical_id="acme:dashboard-css",
                kind="css",
                path="/assets/dashboard.css",
                digest="sha256-dashboard",
                content_type="text/css",
            ),
        ),
    )
    assert app.include_package(package) is package
    assert app.include_package(package) is package
    manifest = app.manifest()
    assert manifest["schema"] == "edron.application-manifest/1"
    assert manifest["packages"][0]["name"] == "acme.dashboard"
    assert "path" not in manifest["assets"][0]
    assert app.conformance()["ok"] is True


def test_package_asset_collision_rolls_back_native_registry() -> None:
    app = _app()
    first = ed.FeaturePackage(
        "acme.first",
        "1.0",
        assets=(AssetMeta("acme:shared", "css", "/a.css", "sha256-a", "text/css"),),
    )
    second = ed.FeaturePackage(
        "acme.second",
        "1.0",
        assets=(AssetMeta("acme:shared", "css", "/b.css", "sha256-b", "text/css"),),
    )
    app.include_package(first)
    with pytest.raises(ed.PackageConflictError):
        app.include_package(second)
    assert [item["name"] for item in app.manifest()["packages"]] == ["acme.first"]


def test_typed_navigation_rejects_unregistered_targets() -> None:
    app = _app()

    @app.page("/home", title="Home")
    class Home(ed.Page):
        def render(self) -> None:
            self.text("home")

    target = app.navigation_target(Home)
    assert target.path == "/home"
    assert "/home" in hedron_core.render(target.link()).html
    with pytest.raises(ed.NavigationError):
        app.navigation_target("/missing")


def test_layout_lowers_to_native_and_promotion_is_lazy() -> None:
    app = _app()
    spec = ed.layout("grid", columns=2, gap="md")
    node = spec.compose((hedron_core.Text("a"), hedron_core.Text("b")))
    assert type(node).__name__ == "Grid"
    promotion = app.promote_capability("charts")
    assert promotion.native == "hedron_charts"
    assert promotion.inspect()["status"] == "available"
    assert app.manifest()["promotions"][0]["name"] == "charts"
