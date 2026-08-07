"""Playwright: every docs sim contract + network/POST guards."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright

from hedron import Page, html, swap
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_sim import SimApp, embed_demo
from hedron_sim.assets import css_text, javascript_text

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

# Contracts import demos.*; put docs on path before collection-time parametrize.
if str(DOCS) not in sys.path:
    sys.path.insert(0, str(DOCS))

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("HEDRON_BROWSER") != "1",
        reason="Opt-in: set HEDRON_BROWSER=1 and install Playwright browsers",
    ),
]


@pytest.fixture(scope="module", autouse=True)
def _docs_on_path() -> None:
    path = str(DOCS)
    if path not in sys.path:
        sys.path.insert(0, path)


def _engine() -> str:
    return os.environ.get("HEDRON_BROWSER_ENGINE") or "chromium"


def _launch(pw: object):  # noqa: ANN001
    return getattr(pw, _engine()).launch(headless=True)


_SIM_READY_JS = """() => {
  const el = document.querySelector('[data-hedron-sim]');
  return el && el.dataset.hedronSimReady === 'true';
}"""


def _demo_document(island_html: str) -> str:
    return f"""<!doctype html>
<html lang="en" data-md-color-scheme="default">
<head>
  <meta charset="utf-8" />
  <title>hedron-sim contract</title>
  <style>{css_text()}</style>
</head>
<body>
{island_html}
<script>{javascript_text()}</script>
</body>
</html>
"""


def _write_demo(tmp_path: Path, island_html: str, name: str = "demo.html") -> Path:
    path = tmp_path / name
    path.write_text(_demo_document(island_html), encoding="utf-8")
    return path


def _root_locator(page, mode_demo: bool):  # noqa: ANN001
    if mode_demo:
        return page.locator("[data-hedron-sim-modes]").first
    return page.locator("[data-hedron-sim]").first


def _run_contract(page, contract) -> None:  # noqa: ANN001
    from demos.contracts import Step

    root = _root_locator(page, contract.mode_demo)
    root.wait_for(state="attached", timeout=5000)
    if not contract.mode_demo:
        page.wait_for_function(
            """() => {
              const el = document.querySelector('[data-hedron-sim]');
              return el && el.dataset.hedronSimReady === 'true';
            }"""
        )
        # Forms must never keep a non-hash action after boot.
        for handle in root.locator("form").all():
            action = handle.get_attribute("action")
            assert action in {None, "#", ""}, f"{contract.id} form action={action!r}"

    bad_requests: list[str] = []

    def on_request(req) -> None:  # noqa: ANN001
        url = req.url
        if url.startswith("file:") or url.startswith("data:"):
            return
        # Allow nothing else from a file:// demo page.
        bad_requests.append(f"{req.method} {url}")

    page.on("request", on_request)

    for step in contract.steps:
        assert isinstance(step, Step)
        if step.confirm is not None:
            page.once(
                "dialog",
                lambda dialog, accept=step.confirm: dialog.accept() if accept else dialog.dismiss(),
            )
        for selector, value in step.fill.items():
            root.locator(selector).fill(value)
        if step.click:
            root.locator(step.click).first.click(force=True)
        page.wait_for_timeout(step.wait_ms)
        if step.expect_trace:
            trace = root.locator("[data-hedron-sim-trace]")
            assert step.expect_trace in trace.inner_text(), (
                f"{contract.id}: expected trace {step.expect_trace!r}, got {trace.inner_text()!r}"
            )
        if step.expect_text and step.contains:
            text = root.locator(step.expect_text).inner_text()
            assert step.contains in text, f"{contract.id}: expected {step.contains!r} in {text!r}"

    assert not bad_requests, f"{contract.id} leaked network: {bad_requests}"


def test_hedron_sim_form_post_never_leaves_page(tmp_path: Path) -> None:
    """method=post form without action must not navigate or POST off-page."""
    app = SimApp(demo_id="browser-form-guard")
    listing = app.region("list")

    @app.page("/")
    def home() -> Page:
        return Page(
            html.div("empty", id=listing.id),
            html.form(
                html.input(name="note", id="note", value="x"),
                html.button("Add", type="submit"),
                method="post",
                **{
                    "hx-post": "/notes",
                    "hx-target": "#list",
                    "hx-swap": "outerHTML",
                },
            ),
            title="guard",
        )

    @app.action("/notes", region=listing)
    def add():
        return swap(html.div("added", id=listing.id))

    path = _write_demo(tmp_path, embed_demo(app), "form-guard.html")
    with sync_playwright() as pw:
        browser = _launch(pw)
        page = browser.new_page()
        try:
            navigated: list[str] = []
            page.on(
                "framenavigated",
                lambda frame: navigated.append(frame.url) if frame == page.main_frame else None,
            )
            requests: list[str] = []
            page.on(
                "request",
                lambda req: (
                    requests.append(f"{req.method} {req.url}")
                    if not req.url.startswith("file:")
                    else None
                ),
            )
            page.goto(path.as_uri())
            page.wait_for_function(_SIM_READY_JS)
            assert page.get_attribute("[data-hedron-sim] form", "action") == "#"
            page.click("button[type=submit]")
            page.wait_for_function(
                """() => {
                  const t = document.querySelector('[data-hedron-sim-trace]');
                  return t && !t.hidden && t.textContent.includes('200');
                }"""
            )
            assert page.locator("#list").inner_text() == "added"
            assert page.url.startswith("file:")
            assert not any(r.startswith("POST ") for r in requests)
            # Initial file navigation only.
            assert all(u.startswith("file:") for u in navigated)
        finally:
            browser.close()


def test_hedron_sim_boot_forces_hash_on_progressive_href(tmp_path: Path) -> None:
    app = SimApp(demo_id="browser-href-guard")
    panel = app.region("panel")

    @app.page("/")
    def home() -> Page:
        return Page(
            html.div("home", id=panel.id),
            html.a(
                "Reports",
                href=SafeUrl.parse("/reports", purpose=UrlPurpose.NAVIGATION),
                **{"hx-get": "/reports", "hx-target": "#panel", "hx-swap": "innerHTML"},
            ),
            title="href",
        )

    @app.fragment("/reports", region=panel)
    def reports():
        return swap(html.div("reports-body"))

    path = _write_demo(tmp_path, embed_demo(app), "href-guard.html")
    with sync_playwright() as pw:
        browser = _launch(pw)
        page = browser.new_page()
        try:
            page.goto(path.as_uri())
            page.wait_for_function(_SIM_READY_JS)
            href = page.get_attribute("[data-hedron-sim] a", "href")
            assert href == "#"
            assert page.get_attribute("[data-hedron-sim] a", "data-hedron-sim-href") == "/reports"
            page.click("a:has-text('Reports')")
            page.wait_for_function(
                """() => {
                  const t = document.querySelector('[data-hedron-sim-trace]');
                  return t && !t.hidden && t.textContent.includes('200');
                }"""
            )
            assert "reports-body" in page.locator("#panel").inner_text()
            assert page.url.startswith("file:")
        finally:
            browser.close()


def _contract_ids() -> list[str]:
    from demos.contracts import CONTRACTS

    return [c.id for c in CONTRACTS]


@pytest.mark.parametrize("contract_id", _contract_ids())
def test_docs_sim_contract(contract_id: str, tmp_path: Path) -> None:
    from demos.contracts import CONTRACTS

    contract = next(c for c in CONTRACTS if c.id == contract_id)
    path = _write_demo(tmp_path, contract.builder(), f"{contract_id}.html")
    with sync_playwright() as pw:
        browser = _launch(pw)
        page = browser.new_page()
        try:
            page.goto(path.as_uri())
            _run_contract(page, contract)
        finally:
            browser.close()
