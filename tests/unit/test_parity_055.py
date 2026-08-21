"""PARITY-055 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_parity_055_adapter_matrix() -> None:
    data = tomllib.loads(
        Path("docs/acceptance/workflow-parity-055.toml").read_text(encoding="utf-8")
    )
    adapters = {row["name"]: row for row in data["adapter"]}
    assert adapters["fastapi"]["upload_streaming"] == "supported"
    assert adapters["flask"]["upload_streaming"] == "degraded"
    assert adapters["django"]["upload_streaming"] == "degraded"
    for name in ("fastapi", "flask", "django"):
        assert adapters[name]["layout"] == "supported"
        assert adapters[name]["capabilities"] == "supported"
        assert adapters[name]["replay"] == "supported"
