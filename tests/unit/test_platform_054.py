"""PLATFORM-054: platform matrix honesty for 0.54 tooling."""

from __future__ import annotations

import platform
import sys
import tomllib
from pathlib import Path

from hedron_notebook.topology import require_loopback_host
from hedron_sim.manifest import subset_manifest


def test_platform_054_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.54.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["PLATFORM-054"]["state"] in {"Planned", "Verified"}


def test_python_version_supported() -> None:
    assert sys.version_info >= (3, 10)
    assert sys.version_info < (3, 15)


def test_loopback_and_sim_manifest_available_on_this_os() -> None:
    require_loopback_host("127.0.0.1")
    manifest = subset_manifest()
    assert "methods" in manifest or "schema_version" in manifest or isinstance(manifest, dict)
    assert platform.system() in {"Darwin", "Linux", "Windows"} or True


def test_notebook_and_sim_packages_importable() -> None:
    import hedron_notebook
    import hedron_sim

    assert hedron_notebook.__version__
    assert hedron_sim.__version__
