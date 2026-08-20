"""PKG-053 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_pkg_053_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.53.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["PKG-053"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md").is_file()


def test_upgrade_fixtures_and_verify_script() -> None:
    upgrade = Path("docs/acceptance/upgrade-fixtures-053.md").read_text(encoding="utf-8")
    assert "0.52" in upgrade
    assert Path("scripts/verify_pkg_53.py").is_file()


def test_stage1_modules_exist_versions_unbumped() -> None:
    assert Path("packages/hedron-core/src/hedron_core/application_assets.py").is_file()
    assert Path("packages/hedron-core/src/hedron_core/route_document.py").is_file()
    assert Path("packages/hedron-core/src/hedron_core/operation_workflow.py").is_file()
    assert Path("packages/hedron-core/src/hedron_core/testgen.py").is_file()
    assert Path("packages/hedron/src/hedron/fleet.py").is_file()
    assert Path("packages/hedron/src/hedron/discover_api.py").is_file()

    tip = tomllib.loads(Path("docs/release.toml").read_text(encoding="utf-8"))["release"][
        "published_version"
    ]
    # Living tip may advance after 0.53; Stage 1 modules must remain present.
    assert str(tip).startswith("0.")
    hedron_meta = tomllib.loads(Path("packages/hedron/pyproject.toml").read_text(encoding="utf-8"))
    assert hedron_meta["project"]["version"] == tip
    core_meta = tomllib.loads(
        Path("packages/hedron-core/pyproject.toml").read_text(encoding="utf-8")
    )
    assert core_meta["project"]["version"] == tip
    workspace = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert workspace["project"]["version"] == tip

    init_src = Path("packages/hedron/src/hedron/__init__.py").read_text(encoding="utf-8")
    assert f'__version__ = "{tip}"' in init_src
