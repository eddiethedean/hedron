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
        "index.html",
        '[data-hedron-sim^="hello-refresh"]',
        'button:has-text("Refresh status")',
        "GET /status → 200",
    ),
    (
        "getting-started/quickstart/index.html",
        '[data-hedron-sim^="hello-refresh"]',
        'button:has-text("Refresh status")',
        "GET /status → 200",
    ),
    (
        "examples/crud-tutorial/index.html",
        '[data-hedron-sim="crud-notes"]',
        'button:has-text("Add note")',
        "POST /notes → 200",
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
        "401",
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


def _engine() -> str:
    return os.environ.get("HEDRON_BROWSER_ENGINE") or "chromium"


def _launch(pw: object):  # noqa: ANN001
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
        def __init__(self, *args, **kwargs):  # noqa: ANN002, ANN003
            super().__init__(*args, directory=str(docs_site), **kwargs)

        def log_message(self, format: str, *args) -> None:  # noqa: A003, ANN002
            return

    # Bind an ephemeral port.
    httpd = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    httpd.shutdown()


@pytest.mark.parametrize(
    ("page_path", "root_sel", "click_sel", "expect"),
    _PAGES,
    ids=[p[0] for p in _PAGES],
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

            def on_request(req) -> None:  # noqa: ANN001
                if req.method in {"POST", "PUT", "PATCH", "DELETE"}:
                    leaked.append(f"{req.method} {req.url}")

            page.on("request", on_request)
            page.goto(url, wait_until="networkidle", timeout=60000)
            # Prefer Demo tab when Material tabbed content is present.
            demo_label = page.locator('label[for^="__tabbed_"]', has_text="Demo").first
            if demo_label.count():
                demo_label.click()
            root = page.locator(root_sel).first
            root.wait_for(state="visible", timeout=10000)
            page.wait_for_function(
                """(sel) => {
                  const el = document.querySelector(sel);
                  return el && el.dataset.hedronSimReady === 'true';
                }""",
                arg=root_sel,
            )
            if "crud-notes" in root_sel:
                page.fill("#crud-note", "docs-smoke")
            if "forms-invite" in root_sel:
                # Empty / short email → invalid variant (422).
                page.fill("#invite-email", "x")
            root.locator(click_sel).first.click()
            page.wait_for_timeout(700)
            trace = root.locator("[data-hedron-sim-trace]").inner_text()
            assert expect in trace, f"{page_path}: got {trace!r}"
            assert not leaked, f"{page_path} leaked mutating requests: {leaked}"
        finally:
            browser.close()
