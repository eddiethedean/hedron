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
    beta_packages = (
        "hedron",
        "hedron-data",
        "hedron-flask",
        "hedron-django",
        "hedron-jinja",
        "hedron-explorer",
    )
    for name in beta_packages:
        other = tomllib.loads(
            (ROOT / "packages" / name / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]
        assert other["version"] == __version__, name
    alpha_packages: tuple[str, ...] = ()
    for name in alpha_packages:
        other = tomllib.loads(
            (ROOT / "packages" / name / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]
        development_status = [
            classifier
            for classifier in other["classifiers"]
            if classifier.startswith("Development Status ::")
        ]
        assert development_status == ["Development Status :: 3 - Alpha"], name
        # Alpha packages may version independently of the Beta train.
    independent_beta_02 = (
        "hedron-mcp",
        "hedron-gradio",
        "hedron-charts",
        "hedron-sample-kit",
        "hedron-sim",
        "hedron-notebook",
    )
    for name in independent_beta_02:
        other = tomllib.loads(
            (ROOT / "packages" / name / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]
        development_status = [
            classifier
            for classifier in other["classifiers"]
            if classifier.startswith("Development Status ::")
        ]
        assert development_status == ["Development Status :: 4 - Beta"], name
        assert str(other["version"]).startswith("0.2."), name
    independent_beta = (
        "hedron-native",
        "hedron-maps",
    )
    for name in independent_beta:
        other = tomllib.loads(
            (ROOT / "packages" / name / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]
        development_status = [
            classifier
            for classifier in other["classifiers"]
            if classifier.startswith("Development Status ::")
        ]
        assert development_status == ["Development Status :: 4 - Beta"], name
        assert str(other["version"]).startswith("0.1."), name
    mcp = tomllib.loads(
        (ROOT / "packages" / "hedron-mcp" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    mcp_status = [
        classifier
        for classifier in mcp["classifiers"]
        if classifier.startswith("Development Status ::")
    ]
    assert mcp_status == ["Development Status :: 4 - Beta"]
    assert mcp["version"].startswith("0.2.")
    gradio = tomllib.loads(
        (ROOT / "packages" / "hedron-gradio" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    gradio_status = [
        classifier
        for classifier in gradio["classifiers"]
        if classifier.startswith("Development Status ::")
    ]
    assert gradio_status == ["Development Status :: 4 - Beta"]
    assert gradio["version"] == "0.2.1"


def test_public_metadata_fields() -> None:
    project = _project()
    assert project["name"] == "hedron-core"
    assert project["requires-python"] == ">=3.11,<3.15"
    assert project["license"] == "MIT"
    assert project["license-files"] == ["LICENSE"]
    dependencies = project["dependencies"]
    assert isinstance(dependencies, list)
    assert "pydantic>=2.13.4,<2.15" in dependencies
    assert "packaging>=24.0" in dependencies
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


def test_package_maturity_classifiers() -> None:
    expected = {
        "hedron": "Development Status :: 4 - Beta",
        "hedron-core": "Development Status :: 4 - Beta",
        "hedron-data": "Development Status :: 4 - Beta",
        "hedron-django": "Development Status :: 4 - Beta",
        "hedron-explorer": "Development Status :: 4 - Beta",
        "hedron-flask": "Development Status :: 4 - Beta",
        "hedron-charts": "Development Status :: 4 - Beta",
        "hedron-native": "Development Status :: 4 - Beta",
        "hedron-sample-kit": "Development Status :: 4 - Beta",
        "hedron-sim": "Development Status :: 4 - Beta",
        "hedron-notebook": "Development Status :: 4 - Beta",
        "hedron-jinja": "Development Status :: 4 - Beta",
    }
    for package, maturity in expected.items():
        project = tomllib.loads(
            (ROOT / "packages" / package / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]
        development_status = [
            classifier
            for classifier in project["classifiers"]
            if classifier.startswith("Development Status ::")
        ]
        assert development_status == [maturity], package


def test_flagship_declares_direct_pydantic_dependency() -> None:
    project = tomllib.loads(
        (ROOT / "packages" / "hedron" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    assert "pydantic>=2.13.4,<2.15" in project["dependencies"]
    assert "fastapi>=0.141.1,<0.150" in project["dependencies"]


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
        import pytest

        pytest.skip("no hedron_core wheel in dist/; run after build")
    with zipfile.ZipFile(wheels[-1]) as archive:
        names = set(archive.namelist())
        assert "hedron_core/py.typed" in names
        assert "hedron_core/__init__.py" in names
        meta = archive.read(f"hedron_core-{__version__}.dist-info/METADATA").decode("utf-8")
        assert "Name: hedron-core" in meta
        assert f"Version: {__version__}" in meta
        assert "Description-Content-Type: text/markdown" in meta
        assert re.search(r"^Summary: ", meta, re.M)
