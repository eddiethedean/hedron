"""Completeness guard for the outbound egress inventory in issue #555."""

from __future__ import annotations

import tomllib  # pyright: ignore[reportMissingImports] - stdlib in supported Python
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).parents[2]
INVENTORY = ROOT / "docs/acceptance/egress-inventory-555.toml"


def test_every_inventory_surface_has_an_owned_disposition_and_existing_paths() -> None:
    loads = cast(
        Callable[[str], object],
        tomllib.loads,  # pyright: ignore[reportUnknownMemberType]
    )
    payload = cast(dict[str, Any], loads(INVENTORY.read_text(encoding="utf-8")))
    surfaces = cast(list[dict[str, Any]], payload["surface"])
    assert len(surfaces) >= 10
    assert len({item["id"] for item in surfaces}) == len(surfaces)
    for item in surfaces:
        assert item["owner"]
        assert item["classification"]
        assert item["disposition"] in {"migrated", "exempt"}
        assert item["rationale"]
        assert item["paths"]
        assert all((ROOT / path).is_file() for path in item["paths"])


def test_packages_do_not_silently_construct_unrestricted_http_clients() -> None:
    python_sources = {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in (ROOT / "packages").glob("*/src/**/*.py")
    }
    direct_http_markers = (
        "httpx.AsyncClient(",
        "httpx.Client(",
        "requests.get(",
        "requests.post(",
        "requests.request(",
        "aiohttp.ClientSession(",
        "urllib.request.urlopen(",
        "socket.create_connection(",
        "http.client.HTTPConnection(",
        "http.client.HTTPSConnection(",
        "from gradio_client import Client",
    )
    hits = {
        path
        for path, source in python_sources.items()
        if any(marker in source for marker in direct_http_markers)
    }
    assert hits == {
        "packages/fastapi-workbench/src/fastapi_workbench/cli.py",
        "packages/hedron-core/src/hedron_core/egress_http.py",
        "packages/hedron-posit/src/hedron_posit/cli.py",
    }
    for path in (
        "packages/fastapi-workbench/src/fastapi_workbench/cli.py",
        "packages/hedron-posit/src/hedron_posit/cli.py",
    ):
        assert "transport=httpx.ASGITransport(app=app)" in python_sources[path]
