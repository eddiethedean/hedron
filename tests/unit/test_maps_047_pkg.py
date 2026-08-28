"""PKG-047 wheel-facing package facts."""

from __future__ import annotations

from pathlib import Path

from hedron_maps import MAPLIBRE_VERSION, SYNTHETIC_ARCHIVE, __version__
from hedron_maps.pins import RUNTIME_PINS, assert_pins_present


def test_package_version_and_pin() -> None:
    assert __version__ == "0.1.4"
    assert MAPLIBRE_VERSION == "5.6.1"
    assert MAPLIBRE_VERSION != "4.5.0"
    assert_pins_present()
    csp = Path("packages/hedron-maps/src/hedron_maps") / RUNTIME_PINS["maplibre-csp"]["path"]
    assert csp.stat().st_size >= 100_000
    license_txt = Path("packages/hedron-maps/src/hedron_maps/assets/maplibre/LICENSE.txt")
    assert license_txt.is_file()
    assert "MapLibre" in license_txt.read_text(encoding="utf-8")
    assert SYNTHETIC_ARCHIVE.is_file()
    pyproject = Path("packages/hedron-maps/pyproject.toml").read_text(encoding="utf-8")
    assert "3.11" in pyproject and "3.14" in pyproject
    assert Path("packages/hedron-maps/LICENSE").is_file()
    assert Path("packages/hedron-maps/CHANGELOG.md").is_file()
