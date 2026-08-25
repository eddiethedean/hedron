"""Evidence-only: package/release inventory — not product behavior.

PKG-055 evidence.
"""

from __future__ import annotations

import tomllib
from pathlib import Path


def _living_tip() -> str:
    release = tomllib.loads(Path("docs/release.toml").read_text(encoding="utf-8"))["release"]
    return str(release["development_version"])


def test_pkg_055_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.55.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["PKG-055"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0082-SECURE-UPGRADEABLE-WORKFLOWS.md").is_file()
    assert Path("examples/workflow-055/app.py").is_file()


def test_upgrade_fixtures_and_verify_script() -> None:
    upgrade = Path("docs/acceptance/upgrade-fixtures-055.md").read_text(encoding="utf-8")
    assert "0.54" in upgrade
    assert Path("scripts/verify_pkg_55.py").is_file()
    assert Path("scripts/verify_pkg_54.py").is_file()


def test_stage1_modules_and_versions() -> None:
    tip = _living_tip()
    if (
        tip.startswith("0.56.")
        or tip.startswith("0.57.")
        or tip.startswith("0.58.")
        or tip.startswith("0.59.")
        or tip.startswith("0.60.")
        or tip.startswith("0.61.")
        or tip.startswith("0.62.")
        or tip.startswith("0.63.")
        or tip.startswith("0.64.")
    ):
        # Historical 0.55 packet under a later living tip.
        assert Path("packages/hedron/src/hedron/workflow.py").is_file()
        assert Path("packages/hedron/src/hedron/capabilities.py").is_file()
        assert Path("packages/hedron/src/hedron/replay.py").is_file()
        assert Path("packages/hedron/src/hedron/upload.py").is_file()
        assert Path("packages/hedron/src/hedron/csp.py").is_file()
        return
    assert tip.startswith("0.55.")
    assert Path("packages/hedron/src/hedron/workflow.py").is_file()
    assert Path("packages/hedron/src/hedron/capabilities.py").is_file()
    assert Path("packages/hedron/src/hedron/replay.py").is_file()
    assert Path("packages/hedron/src/hedron/upload.py").is_file()
    assert Path("packages/hedron/src/hedron/csp.py").is_file()
    workspace = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert workspace["project"]["version"] == tip
    hedron_meta = tomllib.loads(Path("packages/hedron/pyproject.toml").read_text(encoding="utf-8"))
    assert hedron_meta["project"]["version"] == tip
