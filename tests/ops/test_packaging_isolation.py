"""Packaging metadata checks for the coordinated 0.36 train."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


_BETA_PACKAGES = {
    "hedron",
    "hedron-core",
    "hedron-data",
    "hedron-flask",
    "hedron-django",
    "hedron-jinja",
    "hedron-explorer",
    "hedron-conformance",
    "hedron-extras",
    "hedron-workbench",
    "hedron-posit",
    "hedron-elements",
}
_INDEPENDENT_BETA = {
    "hedron-native",
    "hedron-maps",
}
_INDEPENDENT_BETA_02 = {
    "hedron-mcp",
    "hedron-gradio",
    "hedron-charts",
    "hedron-sample-kit",
    "hedron-sim",
    "hedron-notebook",
}
_INDEPENDENT_BETA_03 = {
    "edron",
}
_INDEPENDENT_MAJOR = {
    "fastapi-workbench",
}
_TRAIN_ALIGNED_ALPHA: set[str] = set()
_ALPHA_INDEPENDENT: set[str] = set()


def test_all_packages_declare_license_and_version() -> None:
    workspace_version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]["version"]
    for pyproject in sorted((ROOT / "packages").glob("*/pyproject.toml")):
        project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
        name = project["name"]
        if name in _BETA_PACKAGES or name in _TRAIN_ALIGNED_ALPHA:
            assert project["version"] == workspace_version, pyproject
        elif name in _INDEPENDENT_BETA_02:
            assert str(project["version"]).startswith("0.2."), pyproject
        elif name in _INDEPENDENT_BETA_03:
            assert str(project["version"]).startswith("0.3."), pyproject
        elif name in _INDEPENDENT_BETA or name in _ALPHA_INDEPENDENT:
            assert str(project["version"]).startswith("0.1."), pyproject
        elif name in _INDEPENDENT_MAJOR:
            assert str(project["version"]).startswith("1."), pyproject
        else:
            raise AssertionError(f"unexpected package {name}")
        assert "license" in project or "license-files" in project, pyproject.name
        assert (pyproject.parent / "LICENSE").is_file()


def test_django_and_flask_wheels_metadata_isolation() -> None:
    for name in ("hedron-flask", "hedron-django"):
        project = tomllib.loads(
            (ROOT / "packages" / name / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]
        deps = " ".join(project.get("dependencies", [])).lower()
        assert "fastapi" not in deps
        assert "starlette" not in deps
        assert "hedron-core" in deps


def test_first_party_plugin_meta_matches_package_version() -> None:
    seen: set[str] = set()
    for pyproject in sorted((ROOT / "packages").glob("*/pyproject.toml")):
        project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
        for module in (pyproject.parent / "src").rglob("*.py"):
            match = re.search(
                r"PLUGIN_META\s*=\s*PluginMeta\(.*?\bversion\s*=\s*[\"']([^\"']+)[\"']",
                module.read_text(encoding="utf-8"),
                re.S,
            )
            if match:
                seen.add(str(project["name"]))
                assert match.group(1) == project["version"], module
    assert seen == {
        "hedron-charts",
        "hedron-data",
        "hedron-elements",
        "hedron-extras",
        "hedron-gradio",
        "hedron-maps",
        "hedron-mcp",
        "hedron-notebook",
        "hedron-sample-kit",
    }


def test_025_satellites_have_installable_patch_floors() -> None:
    """The flagship extras must not resolve to pre-0.38 chart satellite releases."""
    hedron = tomllib.loads(
        (ROOT / "packages" / "hedron" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    extras = tomllib.loads(
        (ROOT / "packages" / "hedron-extras" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]

    charts_pin = "hedron-charts>=0.2.2,<0.3"
    assert hedron["optional-dependencies"]["charts"] == [charts_pin]
    assert charts_pin in extras["optional-dependencies"]["chart_workbench"]
    assert charts_pin in extras["optional-dependencies"]["all"]
    charts = tomllib.loads(
        (ROOT / "packages" / "hedron-charts" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    sample = tomllib.loads(
        (ROOT / "packages" / "hedron-sample-kit" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    # Tip may patch above the floor; pin floor stays >=0.2.2,<0.3.
    assert charts["version"].startswith("0.2.")
    assert tuple(int(p) for p in charts["version"].split(".")) >= (0, 2, 0)
    assert sample["version"] == "0.2.1"


def test_hedron_build_module_is_packaged(tmp_path: Path) -> None:
    """Regression for #32: Hatchling must ship hedron.build despite build/ gitignore traps."""
    import subprocess
    import zipfile

    build_src = ROOT / "packages" / "hedron" / "src" / "hedron" / "build" / "__init__.py"
    assert build_src.is_file()

    ignored = subprocess.run(
        ["git", "check-ignore", "-v", str(build_src)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert ignored.returncode == 1, ignored.stdout or ignored.stderr

    out = tmp_path / "dist"
    out.mkdir()
    subprocess.check_call(
        ["uv", "build", "--package", "hedron", "-o", str(out)],
        cwd=ROOT,
    )
    wheels = sorted(out.glob("hedron-*.whl"))
    assert wheels, "hedron wheel was not produced"
    with zipfile.ZipFile(wheels[-1]) as archive:
        names = set(archive.namelist())
    assert "hedron/build/__init__.py" in names
    assert "hedron/lifespan.py" in names
