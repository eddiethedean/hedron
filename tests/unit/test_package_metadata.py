"""Package metadata and artifact shape for hedron-core releases."""

from __future__ import annotations

import re
import tomllib
import zipfile
from importlib import metadata
from pathlib import Path

import hedron_core
from hedron_core import __version__

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "packages" / "hedron-core"
PYPROJECT = PKG / "pyproject.toml"


def _project() -> dict[str, object]:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]


def test_version_is_synchronized() -> None:
    project = _project()
    assert project["version"] == __version__
    changelog = (PKG / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"[{__version__}]" in changelog


def test_public_metadata_fields() -> None:
    project = _project()
    assert project["name"] == "hedron-core"
    assert project["requires-python"] == ">=3.12,<3.15"
    assert project["license"] == "MIT"
    assert project["license-files"] == ["LICENSE"]
    dependencies = project["dependencies"]
    assert isinstance(dependencies, list)
    assert "pydantic>=2.13.4,<2.14" in dependencies
    urls = project["urls"]
    assert isinstance(urls, dict)
    assert "Homepage" in urls
    assert "Changelog" in urls
    assert "Repository" in urls
    classifiers = project["classifiers"]
    assert isinstance(classifiers, list)
    assert "Typing :: Typed" in classifiers
    assert "License :: OSI Approved :: MIT License" in classifiers
    assert (PKG / "src" / "hedron_core" / "py.typed").is_file()
    assert (PKG / "README.md").is_file()
    assert (PKG / "CHANGELOG.md").is_file()
    assert (PKG / "LICENSE").is_file()
    assert (ROOT / "LICENSE").is_file()


def test_installed_distribution_metadata() -> None:
    dist = metadata.distribution("hedron-core")
    assert dist.version == __version__
    assert dist.metadata["Name"] == "hedron-core"
    requires = dist.requires or []
    assert any(req.startswith("pydantic") for req in requires)
    # Typed marker must ship with the install tree used by the workspace.
    assert Path(hedron_core.__file__).with_name("py.typed").is_file()


def test_built_wheel_contains_typed_marker_and_readme(tmp_path: Path) -> None:
    """Inspect an already-built wheel when present; otherwise skip quietly.

    CI builds before pytest packaging is not ordered that way, so this test
    prefers dist artifacts when a contributor or release job left them behind.
    """
    wheels = sorted((ROOT / "dist").glob(f"hedron_core-{__version__}-*.whl"))
    if not wheels:
        return
    with zipfile.ZipFile(wheels[-1]) as archive:
        names = set(archive.namelist())
        assert "hedron_core/py.typed" in names
        assert "hedron_core/__init__.py" in names
        meta = archive.read(f"hedron_core-{__version__}.dist-info/METADATA").decode("utf-8")
        assert "Name: hedron-core" in meta
        assert f"Version: {__version__}" in meta
        assert "Description-Content-Type: text/markdown" in meta
        assert re.search(r"^Summary: ", meta, re.M)
