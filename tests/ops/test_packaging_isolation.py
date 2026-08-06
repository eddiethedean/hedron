"""Packaging metadata checks for the coordinated 0.17 train."""

from __future__ import annotations

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
}
_ALPHA_INDEPENDENT = {
    "hedron-charts",
    "hedron-sample-kit",
    "hedron-native",
    "hedron-notebook",
    "hedron-mcp",
}


def test_all_packages_declare_license_and_version() -> None:
    for pyproject in sorted((ROOT / "packages").glob("*/pyproject.toml")):
        project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
        name = project["name"]
        if name in _BETA_PACKAGES:
            assert project["version"] == "0.17.0", pyproject
        elif name in _ALPHA_INDEPENDENT:
            assert str(project["version"]).startswith("0.1."), pyproject
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
    plugins = {
        "hedron-data": ("hedron_data", "plugin.py"),
        "hedron-charts": ("hedron_charts", "plugin.py"),
        "hedron-sample-kit": ("hedron_sample_kit", "plugin.py"),
        "hedron-extras": ("hedron_extras", "plugin.py"),
    }
    for dist, (pkg, plugin_file) in plugins.items():
        project = tomllib.loads(
            (ROOT / "packages" / dist / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]
        text = (ROOT / "packages" / dist / "src" / pkg / plugin_file).read_text(encoding="utf-8")
        assert f'version="{project["version"]}"' in text, dist


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
