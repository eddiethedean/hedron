"""Connect 2025.06 compatibility stays scoped to its content environment."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PYPROJECT = ROOT / "packages" / "hedron-posit" / "pyproject.toml"
CONNECT_REQUIREMENTS = ROOT / "examples" / "connect-reference" / "requirements.txt"


def test_pkg_resources_compatibility_does_not_pin_all_users_to_vulnerable_setuptools() -> None:
    text = PYPROJECT.read_text(encoding="utf-8")
    assert '"setuptools' not in text
    assert "setuptools>=78.1.1,<82" in CONNECT_REQUIREMENTS.read_text(encoding="utf-8")
    assert "force-include" not in text
    assert not (
        ROOT / "packages" / "hedron-posit" / "src" / "pkg_resources" / "__init__.py"
    ).exists()
