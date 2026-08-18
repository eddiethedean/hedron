"""PKG-048 pins, dual assets, licenses, train version."""

from __future__ import annotations

from pathlib import Path

from hedron_core import __version__ as core_version
from hedron_core.htmx_extensions import known_extensions


def test_extension_package_data_and_license() -> None:
    assert Path("packages/hedron-core/src/hedron_core/static/ext/sse.js").is_file()
    assert Path("packages/hedron-core/src/hedron_core/static/ext/head-support.js").is_file()
    assert Path("packages/hedron-core/src/hedron_core/static/ext/preload.js").is_file()
    license_txt = Path(
        "packages/hedron-core/src/hedron_core/static/ext/licenses/htmx-ext-preload.LICENSE"
    )
    assert license_txt.is_file()
    assert "BSD" in license_txt.read_text(encoding="utf-8")
    versions = {ext.public_id: ext.version for ext in known_extensions()}
    assert versions["sse"] == "2.2.4"
    assert versions["head-support"] == "2.0.5"
    assert versions["preload"] == "2.1.2"


def test_core_version_is_at_least_048() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{core_version}"' in pyproject
    parts = tuple(int(p) for p in core_version.split(".")[:2])
    assert parts >= (0, 48)
