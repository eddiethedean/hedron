"""Playwright smoke: high-traffic MkDocs pages with Material Demo tabs."""

from __future__ import annotations

import http.server
import os
import socketserver
import subprocess
import sys
import threading
from pathlib import Path

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("HEDRON_BROWSER") != "1",
        reason="Opt-in: set HEDRON_BROWSER=1 and install Playwright browsers",
    ),
]

ROOT = Path(__file__).resolve().parents[2]

# page path (under site/) → (sim root selector, primary click, expect)
_PAGES: tuple[tuple[str, str, str, str], ...] = (
    (
        "examples/crud-tutorial/index.html",
        '[data-hedron-sim="minimal-form"]',
        'button:has-text("Save")',
        "POST /save → 200",
    ),
    (
        "examples/crud-tutorial/index.html",
        '[data-hedron-sim="mutations-htmx"]',
        'button:has-text("Save")',
        "POST /save → 200",
    ),
    (
        "examples/crud-tutorial/index.html",
        '[data-hedron-sim="crud-notes"]',
        'button:has-text("Add note")',
        "POST /notes → 200",
    ),
    (
        "examples/reference-app/index.html",
        '[data-hedron-sim="csrf-guard"]',
        'button:has-text("POST without CSRF")',
        "403",
    ),
    (
        "examples/reference-app/index.html",
        '[data-hedron-sim="crud-notes"]',
        'button:has-text("Add note")',
        "POST /notes → 200",
    ),
    (
        "examples/reference-app/index.html",
        '[data-hedron-sim="charts-htmx"]',
        'button:has-text("Refresh chart panel")',
        "GET /charts/refresh → 200",
    ),
    (
        "examples/session-auth/index.html",
        '[data-hedron-sim="auth-login"]',
        'button:has-text("Sign in")',
        "POST /login → 200 fragment",
    ),
    (
        "examples/notes-sqlalchemy/index.html",
        '[data-hedron-sim="crud-notes"]',
        'button:has-text("Add note")',
        "POST /notes → 200",
    ),
    (
        "examples/file-upload/index.html",
        '[data-hedron-sim="file-upload"]',
        'button:has-text("Upload roster.txt")',
        "POST /upload-ok → 200",
    ),
    (
        "examples/file-upload/index.html",
        '[data-hedron-sim="file-upload"]',
        'button:has-text("Upload malware.exe")',
        "422",
    ),
    (
        "examples/jobs-poll/index.html",
        '[data-hedron-sim="jobs-poll"]',
        'button:has-text("Start job poll")',
        "GET /jobs/42 → 200",
    ),
    (
        "examples/single-file/index.html",
        '[data-hedron-sim^="hello-refresh"]',
        'button:has-text("Refresh status")',
        "GET /status → 200",
    ),
    (
        "examples/showcase/index.html",
        '[data-hedron-sim="showcase-dashboard"]',
        'button:has-text("Refresh pipeline")',
        "GET /pipeline/refresh → 200",
    ),
    (
        "examples/edron-showcase/index.html",
        '[data-hedron-sim="edron-showcase-dashboard"]',
        'button:has-text("Refresh pipeline")',
        "POST /pipeline/refresh → 200",
    ),
    (
        "guides/forms-and-actions/index.html",
        '[data-hedron-sim="forms-invite"]',
        'button:has-text("Send invite")',
        "422",
    ),
    (
        "guides/minimal-form/index.html",
        '[data-hedron-sim="minimal-form"]',
        'button:has-text("Save")',
        "POST /save → 200",
    ),
    (
        "guides/authentication/index.html",
        '[data-hedron-sim="auth-login"]',
        'button:has-text("Open /home anonymously")',
        "GET /home → 200 fragment",
    ),
    (
        "guides/security/index.html",
        '[data-hedron-sim="csrf-guard"]',
        'button:has-text("POST without CSRF")',
        "403",
    ),
    (
        "guides/data-apps/index.html",
        '[data-hedron-sim="data-table-filter"]',
        'button:has-text("Admins")',
        "GET /rows/admin → 200",
    ),
    (
        "guides/jobs-celery-rq/index.html",
        '[data-hedron-sim="jobs-poll"]',
        'button:has-text("Start job poll")',
        "GET /jobs/42 → 200",
    ),
    (
        "guides/multi-tenant/index.html",
        '[data-hedron-sim="tenant-deny"]',
        'button:has-text("Poll (other tenant)")',
        "404",
    ),
)

_SHOWCASE_PAGES: tuple[tuple[str, str], ...] = (
    ("examples/showcase/index.html", '[data-hedron-sim="showcase-dashboard"]'),
    ("examples/edron-showcase/index.html", '[data-hedron-sim="edron-showcase-dashboard"]'),
)


def _engine() -> str:
    return os.environ.get("HEDRON_BROWSER_ENGINE") or "chromium"


def _launch(pw: object):
    return getattr(pw, _engine()).launch(headless=True)


@pytest.fixture(scope="module")
def docs_site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    try:
        import mkdocs  # noqa: F401
    except ImportError:
        pytest.skip("mkdocs not installed — sync with --group docs")

    site = tmp_path_factory.mktemp("mkdocs-site")
    # Use the current interpreter so we do not recreate the project venv
    # (which would strip Playwright's driver binaries mid-suite).
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "-d",
            str(site),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        pytest.skip(f"mkdocs build failed: {proc.stderr[-800:]}")
    assert (site / "index.html").is_file()
    return site


@pytest.fixture(scope="module")
def docs_server(docs_site: Path):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(docs_site), **kwargs)

        def log_message(self, format: str, *args) -> None:
            return

    # Bind an ephemeral port.
    httpd = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    httpd.shutdown()


def _page_case_id(case: tuple[str, str, str, str]) -> str:
    page_path, root_sel, click_sel, _expect = case
    click_bit = click_sel.split("has-text(")[-1].rstrip(")'\"")
    return f"{page_path}|{root_sel}|{click_bit}"


@pytest.mark.parametrize(
    ("page_path", "root_sel", "click_sel", "expect"),
    _PAGES,
    ids=[_page_case_id(p) for p in _PAGES],
)
def test_docs_sim_page_under_material(
    docs_server: str,
    page_path: str,
    root_sel: str,
    click_sel: str,
    expect: str,
) -> None:
    url = f"{docs_server}/{page_path}"
    with sync_playwright() as pw:
        browser = _launch(pw)
        page = browser.new_page()
        try:
            leaked: list[str] = []

            def on_request(req) -> None:
                if req.method in {"POST", "PUT", "PATCH", "DELETE"}:
                    leaked.append(f"{req.method} {req.url}")

            page.on("request", on_request)
            page.goto(url, wait_until="networkidle", timeout=60000)
            root = page.locator(root_sel).first
            root.wait_for(state="attached", timeout=10000)
            # Activate the Demo tab that owns this island (multi-sim pages have many).
            page.evaluate(
                """(sel) => {
                  const el = document.querySelector(sel);
                  if (!el) return;
                  const set = el.closest('.tabbed-set');
                  if (!set) return;
                  const labels = [...set.querySelectorAll('label[for^="__tabbed_"]')];
                  const demo = labels.find((l) => (l.textContent || '').trim() === 'Demo');
                  if (demo) demo.click();
                }""",
                root_sel,
            )
            root.wait_for(state="visible", timeout=10000)
            page.wait_for_function(
                """(sel) => {
                  const el = document.querySelector(sel);
                  return el && el.dataset.hedronSimReady === 'true';
                }""",
                arg=root_sel,
            )
            if "crud-notes" in root_sel:
                root.locator("#crud-note").fill("docs-smoke")
            if "forms-invite" in root_sel:
                # Empty / short email → invalid variant (422).
                root.locator("#invite-email").fill("x")
            if "mutations-htmx" in root_sel:
                note = root.locator("#pe-note")
                if note.count():
                    note.fill("docs-smoke")
            root.locator(click_sel).first.click()
            page.wait_for_timeout(700)
            trace = root.locator("[data-hedron-sim-trace]").inner_text()
            assert expect in trace, f"{page_path}: got {trace!r}"
            assert not leaked, f"{page_path} leaked mutating requests: {leaked}"
        finally:
            browser.close()


@pytest.mark.parametrize("page_path,root_sel", _SHOWCASE_PAGES)
def test_showcases_are_responsive_and_themeable(
    docs_server: str,
    page_path: str,
    root_sel: str,
) -> None:
    """Both showcase islands must stack cleanly and honor light/dark docs modes."""
    with sync_playwright() as pw:
        browser = _launch(pw)
        for color_scheme, expected_scheme in (("light", "light"), ("dark", "dark")):
            page = browser.new_page(
                viewport={"width": 390, "height": 844}, color_scheme=color_scheme
            )
            try:
                page.goto(f"{docs_server}/{page_path}", wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(300)
                values = page.evaluate(
                    """(selector) => {
                      const root = document.querySelector(selector);
                      const shell = root?.querySelector('.showcase-shell');
                      const nav = shell?.querySelector('.showcase-nav');
                      const styles = shell ? getComputedStyle(shell) : null;
                      return {
                        scheme: document.body.dataset.mdColorScheme,
                        columns: styles?.gridTemplateColumns,
                        colorScheme: styles?.colorScheme,
                        navDisplay: nav ? getComputedStyle(nav).display : null,
                        scrollWidth: document.documentElement.scrollWidth,
                        viewportWidth: window.innerWidth,
                      };
                    }""",
                    root_sel,
                )
                assert values["scheme"] == ("default" if expected_scheme == "light" else "slate")
                assert values["colorScheme"] == expected_scheme
                assert values["navDisplay"] == "none"
                assert len(values["columns"].split()) == 1
                assert values["scrollWidth"] <= values["viewportWidth"]
            finally:
                page.close()
        browser.close()
