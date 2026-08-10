"""Optional Playwright coverage for hedron-sim.js docs runtime."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright

from hedron import InteractionResult, OobHost, OobUpdate, Page, html, swap
from hedron_core.interaction import InteractionPolicy
from hedron_sim import SimApp, embed_demo, sim_form, sim_utc
from hedron_sim.assets import css_text, javascript_text

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("HEDRON_BROWSER") != "1",
        reason="Opt-in: set HEDRON_BROWSER=1 and install Playwright browsers",
    ),
]

ROOT = Path(__file__).resolve().parents[2]


def _engine() -> str:
    """Honor CI matrix engine; default to Chromium locally."""
    return os.environ.get("HEDRON_BROWSER_ENGINE") or "chromium"


def _launch(pw: object):
    return getattr(pw, _engine()).launch(headless=True)


def _demo_document(island_html: str) -> str:
    return f"""<!doctype html>
<html lang="en" data-md-color-scheme="default">
<head>
  <meta charset="utf-8" />
  <title>hedron-sim browser</title>
  <style>{css_text()}</style>
</head>
<body>
{island_html}
<script>{javascript_text()}</script>
</body>
</html>
"""


def _write_demo(tmp_path: Path, island_html: str) -> Path:
    path = tmp_path / "demo.html"
    path.write_text(_demo_document(island_html), encoding="utf-8")
    return path


def test_hedron_sim_js_swaps_fragment_and_tokens(tmp_path: Path) -> None:
    app = SimApp(demo_id="browser-swap")
    status = app.region("service-status")

    def panel():
        return html.div(
            html.strong("healthy"),
            html.span(f"at {sim_utc()}"),
            id=status.id,
            role="status",
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            panel(),
            html.button(
                "Refresh",
                type="button",
                id="refresh",
                **{
                    "hx-get": "/status",
                    "hx-target": "#service-status",
                    "hx-swap": "outerHTML",
                },
            ),
            title="swap",
        )

    @app.fragment("/status", region=status)
    def refresh():
        return swap(panel())

    path = _write_demo(tmp_path, embed_demo(app))
    with sync_playwright() as pw:
        browser = _launch(pw)
        page = browser.new_page()
        try:
            page.goto(path.as_uri())
            page.wait_for_function("() => window.HedronSim")
            before = page.locator("#service-status span").inner_text()
            assert "__HEDRON_SIM_UTC__" not in before
            page.click("#refresh")
            page.wait_for_function(
                """() => {
                  const t = document.querySelector('[data-hedron-sim-trace]');
                  return t && !t.hidden && t.textContent.includes('200');
                }"""
            )
            trace = page.locator("[data-hedron-sim-trace]").inner_text()
            assert "GET /status → 200" in trace
            after = page.locator("#service-status span").inner_text()
            assert "__HEDRON_SIM_UTC__" not in after
            assert "UTC" in after
        finally:
            browser.close()


def test_hedron_sim_js_allowlist_denies_wrong_target(tmp_path: Path) -> None:
    app = SimApp(demo_id="browser-allow")
    probe = app.region("probe")

    @app.page("/")
    def home() -> Page:
        return Page(
            html.div("ok", id=probe.id),
            html.button(
                "Bad",
                type="button",
                id="bad",
                **{"hx-get": "/probe", "hx-target": "#evil", "hx-swap": "outerHTML"},
            ),
            title="allow",
        )

    @app.fragment("/probe", region=probe)
    def probe_frag():
        return swap(html.div("updated", id=probe.id))

    path = _write_demo(tmp_path, embed_demo(app))
    with sync_playwright() as pw:
        browser = _launch(pw)
        page = browser.new_page()
        try:
            page.goto(path.as_uri())
            page.click("#bad")
            page.wait_for_function(
                """() => {
                  const t = document.querySelector('[data-hedron-sim-trace]');
                  return t && !t.hidden && t.textContent.includes('403');
                }"""
            )
            assert page.locator("#probe").inner_text() == "ok"
        finally:
            browser.close()


def test_hedron_sim_js_confirm_cancel_skips_swap(tmp_path: Path) -> None:
    app = SimApp(demo_id="browser-confirm")
    row = app.region("row")

    @app.page("/")
    def home() -> Page:
        return Page(
            html.div("present", id=row.id),
            html.button(
                "Delete",
                type="button",
                id="delete",
                **{
                    "hx-confirm": "Delete?",
                    "hx-delete": "/items/1",
                    "hx-target": "#row",
                    "hx-swap": "innerHTML",
                },
            ),
            title="confirm",
        )

    @app.fragment("/items/1", region=row, method="DELETE")
    def delete():
        return swap(html.div("gone"))

    path = _write_demo(tmp_path, embed_demo(app))
    with sync_playwright() as pw:
        browser = _launch(pw)
        page = browser.new_page()
        try:
            page.goto(path.as_uri())
            page.once("dialog", lambda dialog: dialog.dismiss())
            page.click("#delete")
            page.wait_for_function(
                """() => {
                  const t = document.querySelector('[data-hedron-sim-trace]');
                  return t && !t.hidden && t.textContent.includes('cancelled');
                }"""
            )
            assert page.locator("#row").inner_text() == "present"
        finally:
            browser.close()


def test_hedron_sim_js_form_variant_and_oob(tmp_path: Path) -> None:
    app = SimApp(demo_id="browser-form")
    form_region = app.region("form-region")
    host = app.region("toast-host")

    def form_body(*, ok: bool = False):
        if ok:
            return html.div(
                html.strong("Queued"),
                html.span(sim_form("email")),
                id=form_region.id,
            )
        return html.div(
            html.form(
                html.input(name="email", type="email", id="email"),
                html.button("Send", type="submit"),
                **{
                    "hx-post": "/invite",
                    "hx-target": "#form-region",
                    "hx-swap": "outerHTML",
                },
            ),
            id=form_region.id,
        )

    @app.page("/")
    def home() -> Page:
        return Page(form_body(), OobHost(id=host.id), title="form")

    def invalid():
        return InteractionResult(content=form_body(ok=False), status_code=422)

    def valid():
        return InteractionResult(
            content=form_body(ok=True),
            oob=(
                OobUpdate(
                    content=html.span("toast-ok"),
                    element_id=host.id,
                ),
            ),
            policy=InteractionPolicy(declared_regions=(form_region, host)),
            status_code=200,
        )

    @app.action(
        "/invite",
        regions=(form_region, host),
        validate="email",
        variants={"invalid": invalid, "valid": valid},
    )
    def invite():
        return invalid()

    path = _write_demo(tmp_path, embed_demo(app))
    with sync_playwright() as pw:
        browser = _launch(pw)
        page = browser.new_page()
        try:
            page.goto(path.as_uri())
            page.fill("#email", "ada@example.com")
            page.click("button[type=submit]")
            page.wait_for_function(
                """() => {
                  const t = document.querySelector('[data-hedron-sim-trace]');
                  return t && !t.hidden && t.textContent.includes('200');
                }"""
            )
            assert "Queued" in page.locator("#form-region").inner_text()
            assert "ada@example.com" in page.locator("#form-region").inner_text()
            assert page.locator("#toast-host").count() == 1
            assert "toast-ok" in page.locator("#toast-host").inner_text()
        finally:
            browser.close()


def test_hedron_sim_js_credentials_validate(tmp_path: Path) -> None:
    app = SimApp(demo_id="browser-creds")
    panel = app.region("panel")

    def form(*, err: str = ""):
        kids = []
        if err:
            kids.append(html.p(err))
        kids.extend(
            [
                html.input(name="username", id="user", value="ada"),
                html.input(name="password", id="pass", type="password"),
                html.button("Sign in", type="submit"),
            ]
        )
        return html.div(
            html.form(
                *kids,
                **{
                    "hx-post": "/login",
                    "hx-target": "#panel",
                    "hx-swap": "outerHTML",
                },
            ),
            id=panel.id,
        )

    @app.page("/")
    def home() -> Page:
        return Page(form(), title="creds")

    def invalid():
        return InteractionResult(
            content=form(err="bad credentials"),
            status_code=401,
            region_id=panel.id,
        )

    def valid():
        return InteractionResult(
            content=html.div("welcome ada", id=panel.id),
            status_code=200,
            region_id=panel.id,
        )

    @app.action(
        "/login",
        region=panel,
        validate="credentials",
        variants={"invalid": invalid, "valid": valid},
    )
    def login():
        return invalid()

    path = _write_demo(tmp_path, embed_demo(app))
    with sync_playwright() as pw:
        browser = _launch(pw)
        page = browser.new_page()
        try:
            page.goto(path.as_uri())
            page.fill("#pass", "wrong")
            page.click("button[type=submit]")
            page.wait_for_function(
                """() => {
                  const t = document.querySelector('[data-hedron-sim-trace]');
                  return t && !t.hidden && t.textContent.includes('401');
                }"""
            )
            assert "bad credentials" in page.locator("#panel").inner_text()
            page.fill("#pass", "correct-horse")
            page.click("button[type=submit]")
            page.wait_for_function(
                """() => {
                  const t = document.querySelector('[data-hedron-sim-trace]');
                  return t && !t.hidden && t.textContent.includes('200');
                }"""
            )
            assert "welcome ada" in page.locator("#panel").inner_text()
        finally:
            browser.close()


def test_component_demos_theme_sync_from_docs_scheme(tmp_path: Path) -> None:
    demos_js = (ROOT / "docs" / "javascript" / "component-demos.js").read_text(encoding="utf-8")
    demos_css = (ROOT / "docs" / "stylesheets" / "component-demos.css").read_text(encoding="utf-8")
    html_doc = f"""<!doctype html>
<html lang="en" data-md-color-scheme="default">
<head><meta charset="utf-8" /><style>{demos_css}</style></head>
<body>
<section class="hedron-component-demo" data-hedron-component-demo="ColorModeToggle">
  <div class="hdc-stage">
    <form class="hdc-form hdc-theme-control" data-hdc-theme-form>
      <label>Color mode
        <select data-hdc-theme>
          <option>Light</option>
          <option>Dark</option>
          <option>System</option>
        </select>
      </label>
      <button class="hdc-button" type="submit">Apply</button>
    </form>
    <div class="hdc-theme-swatch" data-hdc-theme-swatch>Preview surface</div>
    <p role="status" data-hdc-status></p>
  </div>
</section>
<script>{demos_js}</script>
</body>
</html>
"""
    path = tmp_path / "theme.html"
    path.write_text(html_doc, encoding="utf-8")
    with sync_playwright() as pw:
        browser = _launch(pw)
        page = browser.new_page()
        try:
            page.goto(path.as_uri())
            assert page.locator("[data-hdc-theme]").input_value() == "Light"
            preview = page.locator("[data-hdc-theme-swatch]").get_attribute("data-preview-theme")
            assert preview == "light"
            page.evaluate('document.documentElement.setAttribute("data-md-color-scheme", "slate")')
            page.wait_for_function(
                """() => {
                  const select = document.querySelector('[data-hdc-theme]');
                  const swatch = document.querySelector('[data-hdc-theme-swatch]');
                  return select && select.value === 'Dark'
                    && swatch && swatch.dataset.previewTheme === 'dark';
                }"""
            )
            page.select_option("[data-hdc-theme]", "System")
            page.click("button[type=submit]")
            page.evaluate(
                'document.documentElement.setAttribute("data-md-color-scheme", "default")'
            )
            page.wait_for_timeout(80)
            # Local override should stick after Apply.
            assert page.locator("[data-hdc-theme]").input_value() == "System"
        finally:
            browser.close()


def test_hedron_sim_routes_survive_material_script_stripping(tmp_path: Path) -> None:
    """Material instant nav removes <script> from fetched HTML; templates must remain."""
    app = SimApp(demo_id="instant-safe")
    panel = app.region("panel")

    @app.page("/")
    def home() -> Page:
        return Page(
            html.div("idle", id=panel.id),
            html.button(
                "Go",
                type="button",
                **{"hx-get": "/x", "hx-target": "#panel", "hx-swap": "innerHTML"},
            ),
            title="Home",
        )

    @app.fragment("/x", region=panel)
    def refresh():
        return swap(html.div("swapped", id=panel.id))

    island = embed_demo(app)
    assert "<template data-hedron-sim-routes>" in island
    assert '<script type="application/json" data-hedron-sim-routes>' not in island

    # Simulate Material: parse HTML and drop every <script>.
    stripped_doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>{css_text()}</style></head>
<body>
<div id="host">{island}</div>
<script>
(function () {{
  var host = document.getElementById("host");
  var parsed = new DOMParser().parseFromString(host.innerHTML, "text/html");
  parsed.querySelectorAll("script").forEach(function (node) {{ node.remove(); }});
  host.replaceChildren(...parsed.body.childNodes);
}})();
</script>
<script>{javascript_text()}</script>
</body></html>
"""
    path = tmp_path / "instant.html"
    path.write_text(stripped_doc, encoding="utf-8")
    with sync_playwright() as pw:
        browser = _launch(pw)
        page = browser.new_page()
        try:
            page.goto(path.as_uri())
            state = page.evaluate(
                """() => {
                  const el = document.querySelector('[data-hedron-sim]');
                  const node = el && el.querySelector('[data-hedron-sim-routes]');
                  let raw = '';
                  if (node && node.content) raw = node.content.textContent || '';
                  if (!String(raw).trim() && node) raw = node.textContent || '';
                  return {
                    ready: el && el.dataset.hedronSimReady,
                    routesLen: String(raw).trim().length,
                    hasTable: !!(el && el._hedronSimTable),
                    tag: node && node.tagName,
                  };
                }"""
            )
            assert state["routesLen"] > 0, state
            assert state["ready"] == "true", state
            assert state["hasTable"] is True, state
            page.click('button:has-text("Go")')
            page.wait_for_function(
                """() => (document.querySelector('#panel') || {}).textContent === 'swapped'"""
            )
            trace = page.locator("[data-hedron-sim-trace]").inner_text()
            assert "200" in trace
        finally:
            browser.close()
