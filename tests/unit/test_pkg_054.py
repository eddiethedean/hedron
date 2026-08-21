"""Evidence-only: package/release inventory — not product behavior.

PKG-054 evidence.
"""

from __future__ import annotations

import tomllib
from pathlib import Path


def _living_tip() -> str:
    release = tomllib.loads(Path("docs/release.toml").read_text(encoding="utf-8"))["release"]
    return str(release["published_version"])


def test_pkg_054_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.54.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["PKG-054"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0081-AUTHORING-LOOP-AND-CHROME.md").is_file()


def test_upgrade_fixtures_and_verify_script() -> None:
    upgrade = Path("docs/acceptance/upgrade-fixtures-054.md").read_text(encoding="utf-8")
    assert "0.53" in upgrade
    assert Path("scripts/verify_pkg_54.py").is_file()
    assert Path("scripts/verify_pkg_53.py").is_file()


def test_stage1_modules_and_satellite_versions() -> None:
    tip = _living_tip()
    assert (
        tip.startswith("0.54.")
        or tip.startswith("0.55.")
        or tip.startswith("0.56.")
        or tip.startswith("0.57.")
    )
    assert Path("packages/hedron/src/hedron/package_doctor.py").is_file()
    assert Path("packages/hedron-conformance/src/hedron_conformance/authoring_loop.py").is_file()
    assert Path("packages/hedron-sim/src/hedron_sim/manifest.py").is_file()
    assert Path("packages/hedron-notebook/src/hedron_notebook/handles.py").is_file()

    if tip.startswith("0.55.") or tip.startswith("0.56.") or tip.startswith("0.57."):
        # Historical 0.54 packet under later living tip — satellite versions remain 0.2.0.
        sample = tomllib.loads(
            Path("packages/hedron-sample-kit/pyproject.toml").read_text(encoding="utf-8")
        )
        notebook = tomllib.loads(
            Path("packages/hedron-notebook/pyproject.toml").read_text(encoding="utf-8")
        )
        sim = tomllib.loads(Path("packages/hedron-sim/pyproject.toml").read_text(encoding="utf-8"))
        assert sample["project"]["version"] == "0.2.0"
        assert notebook["project"]["version"] == "0.2.0"
        assert sim["project"]["version"] == "0.2.0"
        return

    workspace = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert workspace["project"]["version"] == tip
    hedron_meta = tomllib.loads(Path("packages/hedron/pyproject.toml").read_text(encoding="utf-8"))
    assert hedron_meta["project"]["version"] == tip

    sample = tomllib.loads(
        Path("packages/hedron-sample-kit/pyproject.toml").read_text(encoding="utf-8")
    )
    notebook = tomllib.loads(
        Path("packages/hedron-notebook/pyproject.toml").read_text(encoding="utf-8")
    )
    sim = tomllib.loads(Path("packages/hedron-sim/pyproject.toml").read_text(encoding="utf-8"))
    assert sample["project"]["version"] == "0.2.0"
    assert notebook["project"]["version"] == "0.2.0"
    assert sim["project"]["version"] == "0.2.0"
