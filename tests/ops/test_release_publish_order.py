"""Dependency-aware publication ordering regression coverage."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import release_publish_order as publish_order  # noqa: E402


def test_configured_publish_order_respects_required_workspace_dependencies() -> None:
    data = tomllib.loads((ROOT / "release" / "publish-order.toml").read_text(encoding="utf-8"))
    errors = publish_order.dependency_order_errors(
        data["order"], data["excluded"], publish_order.workspace_projects()
    )
    assert errors == []


def test_dependency_order_rejects_dependent_before_requirement() -> None:
    projects = {
        "foundation": ("foundation", ()),
        "dependent": ("dependent", ("foundation",)),
    }
    assert publish_order.dependency_order_errors(["dependent", "foundation"], [], projects) == [
        "dependent: required workspace dependency foundation must be published first"
    ]


def test_dependency_order_rejects_excluded_requirement() -> None:
    projects = {
        "foundation": ("foundation", ()),
        "dependent": ("dependent", ("foundation",)),
    }
    assert publish_order.dependency_order_errors(["dependent"], ["foundation"], projects) == [
        "dependent: required workspace dependency foundation is excluded"
    ]
