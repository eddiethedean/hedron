"""Executable browser evidence for the Phase 1.1 presentation additions."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from hedron import FlowStep, ProcessFlow, ToggleSwitch, render
from hedron_core.theme_contract import ComputedStyleAssertion, evaluate_computed_style_assertions

pytestmark = pytest.mark.browser


def test_phase11_presentation_styles_have_browser_evidence() -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip().lower() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    if os.environ.get("HEDRON_BROWSER_ENGINE", "chromium").strip().lower() != "chromium":
        pytest.skip("Chromium-only style evidence")
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    css_path = (
        Path(__file__).resolve().parents[2]
        / "packages/hedron-core/src/hedron_core/static/hedron-default.css"
    )
    css = css_path.read_text(encoding="utf-8")
    markup = "".join(
        (
            render(ToggleSwitch("enabled", "Enabled", checked=True, compact=True)).html,
            render(
                ProcessFlow(
                    FlowStep("Step one", appearance="plain", marker="1"),
                    label="Workflow",
                    appearance="plain",
                )
            ).html,
        )
    )
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 320})
        page.set_content(f"<style>{css}</style>{markup}")
        toggle = page.locator(".hedron-toggle-switch input[type=checkbox]")
        step = page.locator(".hedron-process-flow-step")
        assertions = (
            ComputedStyleAssertion(
                "ToggleSwitch",
                "display",
                "block",
                toggle.evaluate("e => getComputedStyle(e).display"),
            ),
            ComputedStyleAssertion(
                "ProcessFlow",
                "border-style",
                "none",
                step.evaluate("e => getComputedStyle(e).borderStyle"),
            ),
        )
        result = evaluate_computed_style_assertions(
            assertions,
            provenance={"runtime": "playwright", "engine": "chromium", "css": str(css_path)},
        )
        assert result.passed, result.failures()
        browser.close()
