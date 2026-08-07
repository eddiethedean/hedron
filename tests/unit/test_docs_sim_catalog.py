"""Catalog / structural tests for every docs ``hedron-sim`` demo."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"


@pytest.fixture(scope="module", autouse=True)
def _docs_on_path() -> None:
    path = str(DOCS)
    if path not in sys.path:
        sys.path.insert(0, path)


def _route_payload(html_out: str) -> dict:
    match = re.search(
        r'<script type="application/json" data-hedron-sim-routes>(.*?)</script>',
        html_out,
        flags=re.DOTALL,
    )
    assert match is not None, "missing route table JSON"
    return json.loads(match.group(1).replace("\\u003c", "<"))


def _contract_ids() -> list[str]:
    from demos.contracts import CONTRACTS

    return [c.id for c in CONTRACTS]


@pytest.mark.usefixtures("_docs_on_path")
def test_every_sim_include_matches_builder_and_contract() -> None:
    from demos.contracts import CONTRACTS, contract_ids

    includes_dir = DOCS / "includes" / "sim"
    includes = {path.stem for path in includes_dir.glob("*.html")}
    ids = contract_ids()
    assert includes == ids, f"missing={sorted(includes - ids)} extra={sorted(ids - includes)}"

    for contract in CONTRACTS:
        built = contract.builder().strip() + "\n"
        on_disk = (includes_dir / f"{contract.id}.html").read_text(encoding="utf-8")
        assert built == on_disk, f"{contract.id}: include out of date vs builder"
        assert len(contract.steps) >= contract.min_steps, contract.id
        if contract.mode_demo:
            assert "data-hedron-sim-modes" in built, contract.id
            continue
        assert "data-hedron-sim=" in built, contract.id
        payload = _route_payload(built)
        assert payload.get("routes"), contract.id
        assert any(route.get("regions") for route in payload["routes"].values()), contract.id


@pytest.mark.usefixtures("_docs_on_path")
@pytest.mark.parametrize("contract_id", _contract_ids())
def test_every_sim_has_runnable_and_demo_code_tabs(contract_id: str) -> None:
    from demos.runnable_code import runnable_path, runnable_source
    from demos.tabs import format_demo_code_tabs

    path = runnable_path(contract_id)
    assert path.is_file(), contract_id
    source = runnable_source(contract_id)
    assert "Hedron" in source or "from hedron" in source or "render(" in source, contract_id
    tabs = format_demo_code_tabs(contract_id)
    assert f"<!-- hedron-sim:{contract_id} -->" in tabs
    assert '=== "Demo"' in tabs
    assert '=== "Code"' in tabs
    assert "```python" in tabs


@pytest.mark.usefixtures("_docs_on_path")
def test_guide_tabs_markers_present_in_markdown() -> None:
    import importlib.util

    from demos.contracts import contract_ids

    path = ROOT / "scripts" / "sync_demo_code_tabs.py"
    spec = importlib.util.spec_from_file_location("sync_demo_code_tabs", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    guide_tabs = mod.GUIDE_TABS

    ids = contract_ids()
    for rel, sim_id, _blurb in guide_tabs:
        assert sim_id in ids, f"GUIDE_TABS references unknown sim {sim_id}"
        text = (DOCS / rel).read_text(encoding="utf-8")
        assert f"<!-- hedron-sim:{sim_id} -->" in text, f"missing marker in {rel}"
        assert '=== "Demo"' in text, rel
        assert '=== "Code"' in text, rel


@pytest.mark.usefixtures("_docs_on_path")
@pytest.mark.parametrize("contract_id", _contract_ids())
def test_contract_click_targets_exist_in_initial_html(contract_id: str) -> None:
    """First interactive step's control must exist in the bootstrapped island."""
    from demos.contracts import CONTRACTS

    contract = next(c for c in CONTRACTS if c.id == contract_id)
    html_out = contract.builder()
    first = next((s for s in contract.steps if s.click and not s.auto), None)
    if first is None:
        return
    click = first.click or ""
    # Playwright selectors → coarse HTML presence checks.
    if "has-text(" in click:
        label = click.split('has-text("', 1)[1].rsplit('")', 1)[0]
        assert label in html_out, f"{contract_id}: missing click label {label!r}"
    elif click.startswith(":text("):
        label = click[len(':text("') : -2]
        assert label in html_out, f"{contract_id}: missing click label {label!r}"
    elif "aria-label=" in click:
        label = click.split('aria-label="', 1)[1].rstrip('"]')
        assert label in html_out or f'aria-label="{label}' in html_out, contract_id
    elif click.startswith("#") or click.startswith("["):
        # Attribute / id selectors — ensure a fragment of the selector appears.
        token = click.split("=")[0].strip("[]#")
        assert token in html_out, f"{contract_id}: missing selector token {token!r}"


@pytest.mark.usefixtures("_docs_on_path")
def test_generate_sim_demos_check_is_clean() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_sim_demos.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


@pytest.mark.usefixtures("_docs_on_path")
def test_sync_demo_code_tabs_check_is_clean() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "sync_demo_code_tabs.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


@pytest.mark.usefixtures("_docs_on_path")
def test_credentials_validate_route_variants_render() -> None:
    from demos.guides import build_auth_login_demo

    payload = _route_payload(build_auth_login_demo())
    route = payload["routes"]["POST /login"]
    assert route["validate"] == "credentials"
    assert route["variants"]["invalid"]["status"] == 401
    assert route["variants"]["valid"]["status"] == 200
    assert "Signed in as ada" in route["variants"]["valid"]["html"]
    assert "Invalid username or password" in route["variants"]["invalid"]["html"]


@pytest.mark.usefixtures("_docs_on_path")
def test_sequence_demos_declare_multi_step_payloads() -> None:
    from demos.guides import (
        build_charts_htmx_demo,
        build_jobs_poll_demo,
        build_live_poll_demo,
    )

    for builder, key, expected_len in (
        (build_live_poll_demo, "GET /jobs/42", 4),
        (build_jobs_poll_demo, "GET /jobs/42", 4),
        (build_charts_htmx_demo, "GET /charts/refresh", 3),
    ):
        payload = _route_payload(builder())
        seq = payload["routes"][key]["sequence"]
        assert len(seq) == expected_len, builder.__name__
