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


def _launch(pw: object):
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


def _root_locator(page, mode_demo: bool):
    if mode_demo:
        return page.locator("[data-hedron-sim-modes]").first
    return page.locator("[data-hedron-sim]").first


def _root_selector(mode_demo: bool) -> str:
    return "[data-hedron-sim-modes]" if mode_demo else "[data-hedron-sim]"


def _assert_boot_invariants(root, contract_id: str) -> None:
    for handle in root.locator("form").all():
        action = handle.get_attribute("action")
        assert action in {None, "#", ""}, f"{contract_id} form action={action!r}"
    for handle in root.locator("a[href]").all():
        href = handle.get_attribute("href") or ""
        assert href in {"", "#"} or href.startswith("#"), (
            f"{contract_id} progressive href left as {href!r}"
        )


def _wait_for_trace(page, root_sel: str, needle: str, timeout_ms: int) -> None:
    page.wait_for_function(
        """([sel, needle]) => {
          const root = document.querySelector(sel);
          if (!root) return false;
          const t = root.querySelector('[data-hedron-sim-trace]');
          return t && !t.hidden && (t.textContent || '').includes(needle);
        }""",
        arg=[root_sel, needle],
        timeout=timeout_ms,
    )


def _wait_for_contains(
    page,
    root_sel: str,
    target_sel: str | None,
    needles: tuple[str, ...],
    timeout_ms: int,
) -> None:
    page.wait_for_function(
        """([rootSel, targetSel, needles]) => {
          const root = document.querySelector(rootSel);
          if (!root) return false;
          const el = targetSel ? root.querySelector(targetSel) : root;
          if (!el) return false;
          const text = el.innerText || '';
          return needles.every((n) => text.includes(n));
        }""",
        arg=[root_sel, target_sel, list(needles)],
        timeout=timeout_ms,
    )


def _run_contract(page, contract) -> None:
    from demos.contracts import Step

    assert len(contract.steps) >= contract.min_steps, (
        f"{contract.id}: expected >= {contract.min_steps} steps, got {len(contract.steps)}"
    )

    root_sel = _root_selector(contract.mode_demo)
    root = _root_locator(page, contract.mode_demo)
    root.wait_for(state="attached", timeout=5000)
    if not contract.mode_demo:
        page.wait_for_function(_SIM_READY_JS)
        _assert_boot_invariants(root, contract.id)

    bad_requests: list[str] = []

    def on_request(req) -> None:
        url = req.url
        if url.startswith("file:") or url.startswith("data:"):
            return
        bad_requests.append(f"{req.method} {url}")

    page.on("request", on_request)

    for index, step in enumerate(contract.steps):
        assert isinstance(step, Step)
        label = f"{contract.id} step[{index}]"
        if step.confirm is not None:
            page.once(
                "dialog",
                lambda dialog, accept=step.confirm: dialog.accept() if accept else dialog.dismiss(),
            )
        for selector, value in step.fill.items():
            field = root.locator(selector)
            field.wait_for(state="visible", timeout=5000)
            field.fill(value)
        if step.click:
            control = root.locator(step.click).first
            control.wait_for(state="visible", timeout=5000)
            control.click(force=True)

        timeout = max(step.wait_ms, 5000)
        needles = tuple(n for n in (step.contains, *step.contains_all) if n)
        # Prefer content waits for auto/boot demos — a bare "200" trace can match too early.
        if step.auto and needles:
            _wait_for_contains(page, root_sel, step.expect_text, needles, timeout)
        elif step.expect_trace and not contract.mode_demo:
            _wait_for_trace(page, root_sel, step.expect_trace, timeout)
        else:
            page.wait_for_timeout(step.wait_ms)

        if step.expect_trace and not contract.mode_demo:
            trace = root.locator("[data-hedron-sim-trace]").inner_text()
            assert step.expect_trace in trace, (
                f"{label}: expected trace {step.expect_trace!r}, got {trace!r}"
            )

        # ``[data-hedron-sim]`` / modes root is the island itself — don't nest-query it.
        if step.expect_text in {None, root_sel, "[data-hedron-sim]", "[data-hedron-sim-modes]"}:
            target = root
        else:
            target = root.locator(step.expect_text)
        if needles or step.not_contains:
            text = target.inner_text()
            for needle in needles:
                assert needle in text, f"{label}: expected {needle!r} in {text!r}"
            if step.not_contains:
                assert step.not_contains not in text, (
                    f"{label}: unexpected {step.not_contains!r} in {text!r}"
                )

    assert not bad_requests, f"{contract.id} leaked network: {bad_requests}"
    assert page.url.startswith("file:"), f"{contract.id} navigated away to {page.url!r}"


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
