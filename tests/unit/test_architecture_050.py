"""ARCH-050 thin router, services map, golden frozen routes."""

from __future__ import annotations

import inspect
import tomllib
from pathlib import Path

from fastapi.routing import APIRoute

from hedron_explorer.router import explorer_router
from hedron_explorer.services import catalog, diff, simulation, traces

ROOT = Path(__file__).resolve().parents[2]
LOCK = tomllib.loads(
    (ROOT / "docs/acceptance/explorer-architecture-050.toml").read_text(encoding="utf-8")
)


def test_router_is_under_line_budget() -> None:
    source = Path(inspect.getfile(explorer_router)).read_text(encoding="utf-8")
    assert source.count("\n") < 200


def test_service_modules_exist() -> None:
    assert catalog.components_json is not None
    assert simulation.simulate is not None
    assert traces.TRACE is not None
    assert diff.diff_baselines is not None
    html = ROOT / "packages/hedron-explorer/src/hedron_explorer/views/html.py"
    assert html.is_file()


def _normalize_path(path: str) -> str:
    return path.replace(":path}", "}").replace(":path", "")


def test_golden_html_and_json_routes() -> None:
    router = explorer_router()
    found: dict[str, set[str]] = {}
    for route in router.routes:
        if not isinstance(route, APIRoute):
            continue
        found.setdefault(_normalize_path(route.path), set()).update(route.methods or ())
    for path, method in LOCK["html_routes"].items():
        assert _normalize_path(path) in found, path
        assert method.upper() in found[_normalize_path(path)], (path, found)
    for path, method in LOCK["json_routes"].items():
        if not str(path).startswith("/"):
            continue
        assert path in found, path
        assert method.upper() in found[path]


def test_frozen_csrf_and_prefix() -> None:
    assert LOCK["mount"]["prefix"] == "/hedron-explorer"
    csrf = LOCK.get("csrf") or LOCK.get("silent_caps") or {}
    cookie = LOCK.get("csrf_cookie") or csrf.get("csrf_cookie") or csrf.get("cookie")
    headers = LOCK.get("csrf_headers") or csrf.get("csrf_headers") or csrf.get("headers")
    assert cookie == "hedron_csrf"
    assert "X-CSRF-Token" in headers
