"""ADAPTER-058 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_progressive_and_styling_host_disposition() -> None:
    progressive = tomllib.loads(
        Path("docs/acceptance/progressive-host-disposition-058.toml").read_text(encoding="utf-8")
    )
    styling = tomllib.loads(
        Path("docs/acceptance/styling-host-disposition-058.toml").read_text(encoding="utf-8")
    )

    assert progressive["fastapi"]["screen"] == "supported"
    assert progressive["fastapi"]["form_command"] == "supported"
    assert progressive["fastapi"]["data_workspace"] == "supported"
    assert progressive["fastapi"]["task_flow"] == "supported"
    assert progressive["fastapi"]["dashboard"] == "supported"
    assert progressive["fastapi"]["session_auth"] == "supported"
    assert progressive["fastapi"]["upload"] == "supported"

    assert progressive["flask"]["screen"] == "explicit_adapter_spelling"
    assert progressive["flask"]["form_command"] == "explicit_adapter_spelling"

    assert styling["fastapi"]["theme_design_object"] == "supported"
    assert styling["flask"]["design_object_constructor"] == "explicit_adapter_spelling"
