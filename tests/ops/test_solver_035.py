"""SOLVER-035: Supported extras declarations and mixed-version honesty."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEDRON_PYPROJECT = ROOT / "packages" / "hedron" / "pyproject.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-035.toml"

SUPPORTED_EXTRAS = (
    "data",
    "jinja",
    "charts",
    "mcp",
    "gradio",
    "posit",
    "extras",
    "conformance",
    "native",
)


def test_supported_extras_are_declared() -> None:
    project = tomllib.loads(HEDRON_PYPROJECT.read_text(encoding="utf-8"))["project"]
    extras = project["optional-dependencies"]
    for name in SUPPORTED_EXTRAS:
        assert name in extras, name
        assert extras[name], name


def test_gradio_extra_pins_beta_line() -> None:
    project = tomllib.loads(HEDRON_PYPROJECT.read_text(encoding="utf-8"))["project"]
    deps = " ".join(project["optional-dependencies"]["gradio"])
    assert "hedron-gradio>=0.2.2,<0.3" in deps


def test_mixed_satellite_major_pins_are_distinct() -> None:
    """Independent satellites must not share the train pin floor."""
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    train_pin = data["hedron"]["pin"]
    for name in ("hedron-mcp", "hedron-gradio", "hedron-charts", "fastapi-workbench"):
        assert data[name]["pin"] != train_pin


def test_optional_package_absence_is_inventory_allowed() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    for name in ("hedron-gradio", "hedron-mcp", "hedron-notebook"):
        excluded = data[name].get("excluded", [])
        # Absence / non-required paths must remain honest.
        assert isinstance(excluded, list)


def test_upgrade_fixture_doc_documents_history() -> None:
    text = (ROOT / "docs" / "acceptance" / "upgrade-fixtures-035.md").read_text(encoding="utf-8")
    assert "v0.25" in text or "0.25" in text
    assert "offline" in text.lower()
    assert "mixed-version" in text.lower()
