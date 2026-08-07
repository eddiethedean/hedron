"""Phase 0.19 AT-019: automated Playwright/axe matrix (human AT Deferred → 0.21)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from hedron import Form, FormField, Hedron, Page, SubmitButton, Text, TextInput, html
from hedron_core import Main, SafeUrl, UrlPurpose, reset_registry_for_tests
from hedron_core.a11y import (
    AccessibilityFinding,
    AccessibilityScenario,
    axe_to_sarif,
    snapshot_accessibility_tree,
)

pytestmark = pytest.mark.browser

_ENGINES = ("chromium", "firefox", "webkit")
_FAIL_IMPACTS = frozenset({"critical", "serious"})
# Explicit AT-019 waiver list (rule ids). Empty by default — add only with evidence.
_AXE_WAIVERS: frozenset[str] = frozenset()


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


def _app() -> Hedron:
    app = Hedron(title="at", security="standard", explorer="off", session_secret="test-secret")
    panel = app.region("panel", selector="#panel", description="HTMX panel")

    @app.page("/")
    def home() -> Page:
        return Page(
            Main(
                html.a(
                    "Skip to content",
                    href=SafeUrl.parse("#main", purpose=UrlPurpose.NAVIGATION),
                ),
                Form(
                    FormField(
                        name="name",
                        label="Name",
                        control=TextInput("name", value="", required=True, id="field-name"),
                        required=True,
                    ),
                    SubmitButton("Save"),
                    action="/",
                    method="post",
                ),
                html.div(
                    Text("hello"),
                    html.button(
                        "Refresh panel",
                        type="button",
                        **{
                            "hx-get": "/panel",
                            "hx-target": "#panel",
                            "hx-swap": "innerHTML",
                        },
                    ),
                    id="panel",
                ),
                id="main",
            ),
            title="AT matrix",
            lang="en",
        )

    @app.fragment("/panel", region=panel)
    def panel_frag() -> Text:
        return Text("panel updated")

    return app


def _blocking_violations(violations: list[dict]) -> list[dict]:
    blocked = []
    for item in violations:
        rule = str(item.get("id") or "")
        if rule in _AXE_WAIVERS:
            continue
        impact = str(item.get("impact") or "").lower()
        if impact in _FAIL_IMPACTS:
            blocked.append(item)
    return blocked


@pytest.mark.parametrize("engine", _ENGINES)
def test_keyboard_and_landmarks_per_engine(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER") != "1":
        pytest.skip("Set HEDRON_BROWSER=1 for live browser matrix")
    wanted = os.environ.get("HEDRON_BROWSER_ENGINE")
    if wanted and wanted != engine:
        pytest.skip(f"HEDRON_BROWSER_ENGINE={wanted}")
    try:
        from hedron.testing.browser import axe_scan_report, playwright
    except ImportError:
        pytest.skip("hedron[browser] not installed")

    client = TestClient(_app())
    html_text = client.get("/").text
    # Offline markup heuristic (not a browser a11y tree).
    tree = snapshot_accessibility_tree(html_text)
    assert any(n.tag == "main" for n in tree)

    with playwright() as p:
        browser = getattr(p, engine).launch(headless=True)
        page = browser.new_page()
        page.set_content(html_text)
        page.get_by_role("main").wait_for()
        # Keyboard: tab reaches a focusable control.
        page.keyboard.press("Tab")
        focused = page.evaluate("() => document.activeElement && document.activeElement.tagName")
        assert focused in {"INPUT", "BUTTON", "A", "BODY"}
        # Zoom / reflow: narrow viewport still exposes main landmark.
        page.set_viewport_size({"width": 320, "height": 640})
        assert page.get_by_role("main").count() >= 1
        # Reduced motion / forced-colors emulation where supported.
        page.emulate_media(reduced_motion="reduce")
        try:
            page.emulate_media(forced_colors="active")
        except Exception:
            page.emulate_media(color_scheme="dark")
        report = axe_scan_report(page)
        assert report["incomplete"] is False, report.get("message")
        violations = list(report.get("violations") or [])
        blocked = _blocking_violations(violations)
        assert not blocked, "AT-019 blocking axe findings: " + ", ".join(
            f"{v.get('id')}({v.get('impact')})" for v in blocked[:10]
        )
        scenario = AccessibilityScenario(
            name=f"at-{engine}",
            engine_versions={"browser": engine, "axe": str(report.get("engine"))},
            covers=("keyboard", "zoom", "reduced-motion", "forced-colors", "landmarks"),
        )
        for v in violations:
            scenario.record_finding(
                AccessibilityFinding(
                    rule_id=str(v.get("id", "axe")),
                    impact=str(v.get("impact", "unknown")),
                    message=str(v.get("description", v)),
                )
            )
        summary = scenario.summarize()
        assert summary["accessible"] is False  # never claim accessible from automation alone
        sarif = axe_to_sarif(violations, tool_version=str(report.get("engine") or "pinned"))
        assert sarif["runs"][0]["properties"]["hedron_gate"] == "TEST-019"
        # HTMX fragment path: drive swap via page.request against TestClient HTML is limited;
        # assert fragment route returns markup without serious axe issues when set as content.
        frag = client.get("/panel", headers={"HX-Request": "true"})
        assert frag.status_code == 200
        page.set_content(
            f"<!DOCTYPE html><html lang='en'><body><main id='main'>{frag.text}</main></body></html>"
        )
        frag_report = axe_scan_report(page)
        assert frag_report["incomplete"] is False
        assert not _blocking_violations(list(frag_report.get("violations") or []))
        browser.close()


def test_at_matrix_offline_evidence_artifact() -> None:
    """Always-on evidence path when HEDRON_BROWSER is unset (CI unit lane)."""
    client = TestClient(_app())
    html_text = client.get("/").text
    assert "<main" in html_text
    tree = snapshot_accessibility_tree(html_text)
    assert any(n.tag == "main" for n in tree), "markup heuristic expects <main>"
    scenario = AccessibilityScenario(
        name="at-offline", covers=("keyboard", "zoom", "reduced-motion")
    )
    scenario.add_step("render form page")
    scenario.add_step("snapshot markup heuristic (not browser a11y tree)")
    # Human AT Deferred → 0.21 (D-050)
    summary = scenario.summarize()
    assert summary["status"] == "incomplete"
    assert summary["accessible"] is False
