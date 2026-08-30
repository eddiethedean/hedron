"""Package metadata and artifact shape for hedron-core releases."""

from __future__ import annotations

import re
import tomllib
import zipfile
from importlib import metadata
from pathlib import Path
from typing import Any

import pytest

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
    train_packages = (
        "hedron",
        "hedron-data",
        "hedron-flask",
        "hedron-django",
        "hedron-jinja",
        "hedron-explorer",
    )
    for name in train_packages:
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
    independent_beta = ("hedron-native",)
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
    edron = tomllib.loads(
        (ROOT / "packages" / "edron" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    assert edron["version"] == "1.0.0"
    for stable_name in ("hedron-charts", "hedron-maps"):
        stable = tomllib.loads(
            (ROOT / "packages" / stable_name / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]
        assert stable["version"] == "1.0.0"
        stable_status = [
            classifier
            for classifier in stable["classifiers"]
            if classifier.startswith("Development Status ::")
        ]
        assert stable_status == ["Development Status :: 5 - Production/Stable"]
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
    assert gradio["version"] == "0.2.3"


def test_public_metadata_fields() -> None:
    project = _project()
    assert project["name"] == "hedron-core"
    assert project["requires-python"] == ">=3.10,<3.15"
    assert project["license"] == "MIT"
    assert project["license-files"] == ["LICENSE"]
    dependencies = project["dependencies"]
    assert isinstance(dependencies, list)
    assert "pydantic>=2.12.0,<2.15" in dependencies
    assert "packaging>=22.0" in dependencies
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


def test_every_publishable_package_supports_python_310() -> None:
    for pyproject in sorted((ROOT / "packages").glob("*/pyproject.toml")):
        project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
        assert project["requires-python"] == ">=3.10,<3.15", project["name"]
        classifiers = project.get("classifiers", [])
        assert "Programming Language :: Python :: 3.10" in classifiers, project["name"]


def test_package_maturity_classifiers() -> None:
    expected = {
        "hedron": "Development Status :: 5 - Production/Stable",
        "hedron-core": "Development Status :: 5 - Production/Stable",
        "hedron-data": "Development Status :: 5 - Production/Stable",
        "hedron-django": "Development Status :: 4 - Beta",
        "hedron-explorer": "Development Status :: 4 - Beta",
        "hedron-flask": "Development Status :: 4 - Beta",
        "hedron-charts": "Development Status :: 5 - Production/Stable",
        "hedron-native": "Development Status :: 4 - Beta",
        "hedron-sample-kit": "Development Status :: 4 - Beta",
        "hedron-sim": "Development Status :: 4 - Beta",
        "hedron-notebook": "Development Status :: 4 - Beta",
        "hedron-jinja": "Development Status :: 4 - Beta",
        "hedron-maps": "Development Status :: 5 - Production/Stable",
        "edron": "Development Status :: 5 - Production/Stable",
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
    assert "pydantic>=2.12.0,<2.15" in project["dependencies"]
    assert "fastapi>=0.121.0,<0.150" in project["dependencies"]
    assert "starlette>=0.40.0,<1.0" in project["dependencies"]


def test_audited_dependency_floors_are_declared() -> None:
    def project(package: str) -> dict[str, Any]:
        return tomllib.loads(
            (ROOT / "packages" / package / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]

    assert "starlette>=0.40.0,<1.0" in project("fastapi-workbench")["dependencies"]
    assert "uvicorn[standard]>=0.32,<1.0" in project("fastapi-workbench")["dependencies"]
    assert "starlette>=0.40.0,<2" in project("hedron-mcp")["dependencies"]
    assert "markupsafe>=2.1.1,<4" in project("hedron-jinja")["dependencies"]

    data_extras = project("hedron-data")["optional-dependencies"]
    assert "narwhals>=1.1" in data_extras["dataframes"]
    assert data_extras["dask"] == ["dask[dataframe]>=2024.5"]

    chart_extras = project("hedron-charts")["optional-dependencies"]
    assert chart_extras["pygal"] == ["pygal>=3.0.4"]
    assert chart_extras["datashader"] == ["datashader>=0.16", "pyarrow>=16.0"]


def test_installed_distribution_metadata() -> None:
    dist = metadata.distribution("hedron-core")
    if dist.version != __version__:
        pytest.skip(
            "installed distribution is not the current source checkout; "
            "run this check after uv sync"
        )
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
