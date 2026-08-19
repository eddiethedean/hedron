"""SUPPLY-051 extras isolation and local assets."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_extras_optional_all_does_not_include_experimental_ui() -> None:
    data = tomllib.loads(Path("packages/hedron-extras/pyproject.toml").read_text(encoding="utf-8"))
    extras = data["project"]["optional-dependencies"]
    assert "experimental-ui" in extras
    joined = " ".join(extras.get("all") or [])
    assert "experimental-ui" not in joined
    eps = data["project"]["entry-points"]["hedron.plugins"]
    assert "hedron_extras_sandbox" in eps
    assert eps["hedron_extras"] == "hedron_extras.plugin:register"
