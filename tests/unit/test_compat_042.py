"""COMPAT-042: upgrade / rollback / offline / CDN refusal / removal contracts."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-042.md"
INVENTORY = ROOT / "docs" / "acceptance" / "supported-element-inventory-042.toml"
NPM = ROOT / "packages" / "hedron-elements" / "npm"
STATIC = ROOT / "packages" / "hedron-elements" / "src" / "hedron_elements" / "static"
SUPPLY = ROOT / "docs" / "acceptance" / "fleet-supply-042"
BROWSER_MATRIX = ROOT / "tests" / "browser" / "test_browser_matrix.py"
BROWSER_HTMX = ROOT / "tests" / "browser" / "test_htmx_lifecycle.py"


def test_upgrade_fixture_matrix_locked() -> None:
    text = UPGRADE.read_text(encoding="utf-8")
    assert "Baseline Published `v0.41.0`" in text or "baseline Published `v0.41.0`" in text
    assert ">=0.42.0,<0.43" in text
    assert ">=0.41.0,<0.42" in text
    assert "CDN refusal" in text
    assert "offline" in text.lower()
    assert "rollback" in text.lower()
    assert "full-fragment" in text


def test_mixed_version_and_unknown_feature_fail_closed_language() -> None:
    text = UPGRADE.read_text(encoding="utf-8")
    assert "0.36" in text and "0.41" in text
    assert "fail closed" in text.lower() or "fail visibly" in text.lower()
    assert "Experimental" in text


def test_browser_floor_binds_executable_matrix() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    assert data["browser_floor"] == "playwright_chromium_firefox_webkit"
    assert BROWSER_MATRIX.is_file()
    assert BROWSER_HTMX.is_file()
    matrix = BROWSER_MATRIX.read_text(encoding="utf-8")
    htmx = BROWSER_HTMX.read_text(encoding="utf-8")
    assert "pytestmark" in matrix and "browser" in matrix
    assert "def test_htmx_fragment_and_oob_update" in htmx
    assert "def test_unauthorized_target_returns_forbidden" in htmx


def test_cdn_refusal_and_offline_supply_notes() -> None:
    offline = (SUPPLY / "OFFLINE_INSTALL.md").read_text(encoding="utf-8")
    rollback = (SUPPLY / "ROLLBACK.md").read_text(encoding="utf-8")
    assert "CDN refusal" in offline
    assert "hedron-elements" in offline
    assert "Rollback" in rollback or "rollback" in rollback.lower()
    assert "hedron-elements" in rollback


def test_package_removal_preserves_npm_wheel_identity_for_rollback() -> None:
    # Removal of hedron-elements must leave ordinary SSR/form paths; wheel/npm
    # identity keeps rollback installs reproducible.
    for name in (
        "hedron-example.mjs",
        "hedron-field-text.mjs",
        "hedron-disclosure.mjs",
        "hedron-dialog.mjs",
        "hedron-action-async.mjs",
    ):
        assert (STATIC / name).read_bytes() == (NPM / "modules" / name).read_bytes()
