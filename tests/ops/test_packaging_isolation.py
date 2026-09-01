"""Packaging metadata checks for the coordinated 1.0 train and satellites."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


_TRAIN_ALIGNED_PACKAGES = {
    "hedron",
    "hedron-core",
    "hedron-data",
    "hedron-flask",
    "hedron-django",
    "hedron-jinja",
    "hedron-explorer",
    "hedron-conformance",
    "hedron-extras",
    "hedron-elements",
}
_INDEPENDENT_BETA = {
    "hedron-docs",
    "hedron-native",
    "edron-sim",
}
_INDEPENDENT_BETA_02 = {
    "hedron-mcp",
    "hedron-gradio",
    "hedron-sample-kit",
    "hedron-sim",
    "hedron-notebook",
}
_INDEPENDENT_BETA_05 = {
    "edron",
}
_STABLE_INDEPENDENT = {
    "hedron-charts",
    "hedron-maps",
}
_INDEPENDENT_MAJOR = {
    "fastapi-workbench",
    "hedron-posit",
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
        if name in _TRAIN_ALIGNED_PACKAGES or name in _TRAIN_ALIGNED_ALPHA:
            assert project["version"] == workspace_version, pyproject
        elif name in _INDEPENDENT_BETA_02:
            assert str(project["version"]).startswith("0.2."), pyproject
        elif name in _STABLE_INDEPENDENT or name == "edron":
            assert project["version"] == workspace_version, pyproject
        elif name in _INDEPENDENT_BETA_05:
            assert str(project["version"]).startswith("0.5."), pyproject
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
            source = module.read_text(encoding="utf-8")
            match = re.search(
                r"PLUGIN_META\s*=\s*PluginMeta\(.*?\bversion\s*=\s*(?:[\"']([^\"']+)[\"']|([A-Za-z_]\w*))",
                source,
                re.S,
            )
            if match:
                seen.add(str(project["name"]))
                plugin_version = match.group(1)
                if plugin_version is None:
                    version_module = module.with_name("_version.py")
                    assert version_module.is_file(), module
                    name = re.escape(str(match.group(2)))
                    constant = re.search(
                        rf'^{name}\s*=\s*["\']([^"\']+)["\']',
                        version_module.read_text(encoding="utf-8"),
                        re.M,
                    )
                    assert constant is not None, module
                    plugin_version = constant.group(1)
                assert plugin_version == project["version"], module
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

    charts_pin = "hedron-charts>=1.0.0,<2.0"
    assert hedron["optional-dependencies"]["charts"] == [charts_pin]
    assert charts_pin in extras["optional-dependencies"]["chart_workbench"]
    assert charts_pin in extras["optional-dependencies"]["all"]
    charts = tomllib.loads(
        (ROOT / "packages" / "hedron-charts" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    sample = tomllib.loads(
        (ROOT / "packages" / "hedron-sample-kit" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    # Tip may patch above the floor; the 1.0 plugin contract starts at these patches.
    workspace = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert charts["version"] == workspace["version"]
    assert sample["version"] == "0.2.3"


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
