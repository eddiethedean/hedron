"""PKG-056 evidence."""

from __future__ import annotations

import tomllib
from importlib import metadata
from pathlib import Path

import hedron
import hedron_core
from hedron_core import security_plane


def test_pkg_056_surface_and_inventory() -> None:
    assert hasattr(security_plane, "SecurityContext")
    assert hasattr(security_plane, "RequestBudget")
    assert hasattr(security_plane, "SignedIntent")
    assert Path("docs/api/SECURITY_PLANE.md").is_file()
    assert Path("docs/implementation/SECURITY_056.md").is_file()
    inventory = tomllib.loads(
        Path("docs/acceptance/security-control-inventory-056.toml").read_text(encoding="utf-8")
    )
    assert inventory["phase"] == "0.56"
    for row in inventory["control"]:
        assert row["disposition"] in {"covered", "tightened", "unsupported", "exception"}
        if row["disposition"] == "exception":
            assert row.get("expires")
    # Importable packages expose versions.
    assert metadata.version("hedron")
    assert metadata.version("hedron-core")
    assert hedron.__version__
    assert hedron_core.__version__
