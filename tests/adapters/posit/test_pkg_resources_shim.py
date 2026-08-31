"""Connect runtime compatibility is supplied by the setuptools dependency."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PYPROJECT = ROOT / "packages" / "hedron-posit" / "pyproject.toml"


def test_pkg_resources_compatibility_uses_setuptools_dependency() -> None:
    text = PYPROJECT.read_text(encoding="utf-8")
    assert '"setuptools<82"' in text
    assert "force-include" not in text
    assert not (
        ROOT / "packages" / "hedron-posit" / "src" / "pkg_resources" / "__init__.py"
    ).exists()
