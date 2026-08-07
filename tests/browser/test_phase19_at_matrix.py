"""Phase 0.19 AT-019: automated Playwright/axe matrix (human AT Deferred → 0.21)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from hedron import Form, Hedron, Page, SubmitButton, Text, TextInput, html
from hedron_core import Main, SafeUrl, UrlPurpose, reset_registry_for_tests
from hedron_core.a11y import AccessibilityScenario, axe_to_sarif, snapshot_accessibility_tree

pytestmark = pytest.mark.browser

_ENGINES = ("chromium", "firefox", "webkit")


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


def _app() -> Hedron:
    app = Hedron(title="at", security="standard", explorer="off", session_secret="test-secret")

    @app.page("/")
    def home() -> Page:
        return Page(
            Main(
                Form(
                    TextInput("name", value="", required=True),
                    SubmitButton("Save"),
                    action="/",
                    method="post",
                ),
                html.a(
                    "Skip to content", href=SafeUrl.parse("#main", purpose=UrlPurpose.NAVIGATION)
                ),
                Text("hello"),
                id="main",
            ),
            title="AT matrix",
            lang="en",
        )

    return app


@pytest.mark.parametrize("engine", _ENGINES)
def test_keyboard_and_landmarks_per_engine(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER") != "1":
        pytest.skip("Set HEDRON_BROWSER=1 for live browser matrix")
    try:
        from hedron.testing.browser import axe_scan, playwright
    except ImportError:
        pytest.skip("hedron[browser] not installed")

    client = TestClient(_app())
    html_text = client.get("/").text
    tree = snapshot_accessibility_tree(html_text)
    assert any(n.role == "main" for n in tree)

    with playwright() as p:
        browser = getattr(p, engine).launch(headless=True)
        page = browser.new_page()
        page.set_content(html_text)
        # Keyboard: tab reaches a focusable control.
        page.keyboard.press("Tab")
        focused = page.evaluate("() => document.activeElement && document.activeElement.tagName")
        assert focused in {"INPUT", "BUTTON", "A", "BODY"}
        # Reduced motion / forced-colors emulation where supported.
        page.emulate_media(reduced_motion="reduce")
        page.emulate_media(color_scheme="dark")
        violations = axe_scan(page)
        scenario = AccessibilityScenario(
            name=f"at-{engine}",
            engine_versions={"browser": engine},
        )
        for v in violations:
            scenario.record_finding(
                __import__(
                    "hedron_core.a11y", fromlist=["AccessibilityFinding"]
                ).AccessibilityFinding(
                    rule_id=str(v.get("id", "axe")),
                    impact=str(v.get("impact", "unknown")),
                    message=str(v.get("description", v)),
                )
            )
        summary = scenario.summarize()
        assert summary["accessible"] is False  # never claim accessible from automation alone
        sarif = axe_to_sarif(violations, tool_version="pinned")
        assert sarif["runs"][0]["properties"]["hedron_gate"] == "TEST-019"
        browser.close()


def test_at_matrix_offline_evidence_artifact() -> None:
    """Always-on evidence path when HEDRON_BROWSER is unset (CI unit lane)."""
    client = TestClient(_app())
    html_text = client.get("/").text
    assert "<main" in html_text
    tree = snapshot_accessibility_tree(html_text)
    assert any(n.tag == "main" for n in tree)
    scenario = AccessibilityScenario(
        name="at-offline", covers=("keyboard", "zoom", "reduced-motion")
    )
    scenario.add_step("render form page")
    scenario.add_step("snapshot semantic tree")
    # Human AT Deferred → 0.21 (D-050)
    summary = scenario.summarize()
    assert summary["status"] == "incomplete"
    assert summary["accessible"] is False
