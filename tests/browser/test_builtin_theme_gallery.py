"""Real browser coverage for the built-in themes as a composed design system."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from tests.integration.test_theme_gallery import load_gallery

from hedron_core import (
    Button,
    IconButton,
    Inline,
    Stack,
    aurora_theme,
    classic_theme,
    compile_style_bundle,
    default_theme,
    emit_theme_css,
    folio_theme,
    render,
)

pytestmark = pytest.mark.browser
ROOT = Path(__file__).resolve().parents[2]
ROUTES = (
    "/",
    "/settings",
    "/orders",
    "/support",
    "/components",
    "/forms",
    "/surfaces",
    "/content",
    "/media",
)

# Check rendered colors, including translucent surfaces. Disabled controls and
# decorative/status text with deliberate opacity are excluded. Background
# images are inspected visually; this checks each surface's fallback color.
TEXT_CONTRAST = r"""() => {
  const rgba = value => {
    const numbers = value.match(/[\d.]+/g)?.map(Number) || [0, 0, 0, 0];
    if (value.startsWith('color(srgb')) {
      return [...numbers.slice(0, 3).map(n => n * 255), numbers[3] ?? 1];
    }
    return [...numbers.slice(0, 3), numbers[3] ?? 1];
  };
  const blend = (front, back) => [
    ...front.slice(0, 3).map((v, i) => v * front[3] + back[i] * (1 - front[3])), 1
  ];
  const luminance = rgb => rgb.slice(0, 3).map(v => {
    v /= 255;
    return v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4;
  }).reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
  const failures = [];
  for (const element of document.querySelectorAll('body *')) {
    if (!element.getClientRects().length ||
        element.closest(':disabled, [aria-disabled="true"]')) continue;
    if (!Array.from(element.childNodes).some(n =>
        n.nodeType === 3 && n.textContent.trim())) continue;
    const ancestry = [];
    let skip = false;
    for (let node = element; node; node = node.parentElement) {
      const style = getComputedStyle(node);
      if (Number(style.opacity) < 1 || style.visibility === 'hidden') skip = true;
      ancestry.unshift(style);
    }
    if (skip) continue;
    let background = [255, 255, 255, 1];
    for (const style of ancestry) background = blend(rgba(style.backgroundColor), background);
    const style = getComputedStyle(element);
    const foreground = blend(rgba(style.color), background);
    const [dark, light] = [luminance(foreground), luminance(background)].sort((a, b) => a - b);
    const ratio = (light + .05) / (dark + .05);
    const large = parseFloat(style.fontSize) >= 24 ||
      (parseFloat(style.fontSize) >= 18.66 && Number(style.fontWeight) >= 700);
    if (ratio + .01 < (large ? 3 : 4.5)) failures.push({
      text: element.textContent.trim().slice(0, 70), ratio: +ratio.toFixed(2),
      color: style.color, background: style.backgroundColor
    });
  }
  return failures;
}"""


def _browser_engine(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    pytest.importorskip("playwright")


@pytest.mark.parametrize("engine", ("chromium", "firefox", "webkit"))
def test_gallery_compositions_have_readable_text_and_no_page_overflow(engine: str) -> None:
    _browser_engine(engine)
    from playwright.sync_api import Route, sync_playwright

    with TestClient(load_gallery().app) as client, sync_playwright() as pw:
        browser = getattr(pw, engine).launch(headless=True)
        page = browser.new_page()

        def serve(route: Route) -> None:
            url = urlsplit(route.request.url)
            response: Response = client.get(url.path + (f"?{url.query}" if url.query else ""))
            route.fulfill(
                status=response.status_code, headers=dict(response.headers), body=response.content
            )

        page.route("http://hedron.test/**", serve)
        for theme in ("folio", "classic", "aurora"):
            for mode in ("light", "dark"):
                # Explicit preference must win over the opposite OS palette.
                page.emulate_media(color_scheme="dark" if mode == "light" else "light")
                for width in (1440, 390):
                    page.set_viewport_size({"width": width, "height": 1000})
                    for path in ROUTES:
                        response = page.goto(f"http://hedron.test{path}?theme={theme}&mode={mode}")
                        assert response is not None and response.status == 200
                        label = f"{engine} {theme} {mode} {width} {path}"
                        assert page.evaluate(
                            "document.documentElement.scrollWidth <= innerWidth + 1"
                        ), label
                        assert page.evaluate(TEXT_CONTRAST) == [], label
                        if path == "/":
                            assert page.locator("hedron-chart").evaluate(
                                "e => e.querySelector('svg').hasAttribute('viewBox') && "
                                "getComputedStyle(e.querySelector('svg rect')).fill === "
                                "getComputedStyle(e).backgroundColor"
                            ), label
                        if path == "/media":
                            page.wait_for_function(
                                "() => Array.from(document.images).every(image => "
                                "image.complete && image.naturalWidth > 0)"
                            )
                            assert page.locator("img").evaluate_all(
                                "images => images.every(image => "
                                "image.complete && image.naturalWidth > 0)"
                            ), label
        browser.close()


@pytest.mark.parametrize("engine", ("chromium", "firefox", "webkit"))
def test_gallery_overlays_focus_and_control_layout(engine: str) -> None:
    _browser_engine(engine)
    from playwright.sync_api import Route, sync_playwright

    with TestClient(load_gallery().app) as client, sync_playwright() as pw:
        browser = getattr(pw, engine).launch(headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 844})

        def serve(route: Route) -> None:
            url = urlsplit(route.request.url)
            response: Response = client.get(url.path + (f"?{url.query}" if url.query else ""))
            route.fulfill(
                status=response.status_code, headers=dict(response.headers), body=response.content
            )

        page.route("http://hedron.test/**", serve)
        for theme in ("folio", "classic", "aurora"):
            for mode in ("light", "dark"):
                page.goto(f"http://hedron.test/components?theme={theme}&mode={mode}")
                page.get_by_role("button", name="Review changes", exact=True).click()
                dialog = page.locator("#gallery-dialog")
                assert dialog.is_visible()
                assert dialog.evaluate("e => e.contains(document.activeElement)")
                assert page.evaluate(TEXT_CONTRAST) == []
                bounds = dialog.bounding_box()
                assert bounds is not None and bounds["x"] >= 0
                assert bounds["x"] + bounds["width"] <= 391
                page.keyboard.press("Escape")
                assert not dialog.is_visible()
                assert not dialog.evaluate("e => e.matches(':modal')")
                page.get_by_role("button", name="Native popover", exact=True).click()
                assert page.locator(".hedron-popover-panel:popover-open").is_visible()
                assert page.evaluate(TEXT_CONTRAST) == []
                page.keyboard.press("Escape")
                page.goto(f"http://hedron.test/forms?theme={theme}&mode={mode}")
                search = page.get_by_label("Search", exact=True)
                search.focus()
                assert search.evaluate("e => getComputedStyle(e).outlineStyle") == "solid"
                assert (
                    search.locator("..").evaluate("e => getComputedStyle(e).outlineStyle") == "none"
                )
                page.locator("html").evaluate(
                    "e => e.style.setProperty('--hedron-control-focus', '#f59e0b')"
                )
                assert (
                    search.evaluate("e => getComputedStyle(e).outlineColor") == "rgb(245, 158, 11)"
                )
                page.locator("html").evaluate(
                    "e => e.style.removeProperty('--hedron-control-focus')"
                )
                switch = page.locator('.hedron-toggle-switch input[name="enabled"]')
                before = switch.evaluate("e => getComputedStyle(e, '::before').transform")
                page.locator("html").evaluate("e => e.dir = 'rtl'")
                page.emulate_media(reduced_motion="reduce")
                page.wait_for_timeout(200)
                after = switch.evaluate("e => getComputedStyle(e, '::before').transform")
                assert float(before.removeprefix("matrix(").removesuffix(")").split(",")[4]) > 0
                assert float(after.removeprefix("matrix(").removesuffix(")").split(",")[4]) < 0
        browser.close()


@pytest.mark.parametrize("engine", ("chromium", "firefox", "webkit"))
def test_button_appearances_preserve_emphasis_sizes_and_disabled_states(engine: str) -> None:
    _browser_engine(engine)
    from playwright.sync_api import sync_playwright

    css = (ROOT / "packages/hedron-core/src/hedron_core/static/hedron-default.css").read_text()
    markup = render(
        Stack(
            *(
                Inline(
                    Button(
                        f"{emphasis} {appearance}",
                        emphasis=emphasis,
                        appearance=appearance,
                        id=f"{emphasis}-{appearance}",
                    ),
                    Button(
                        "Disabled",
                        emphasis=emphasis,
                        appearance=appearance,
                        disabled=True,
                        id=f"disabled-{emphasis}-{appearance}",
                    ),
                )
                for emphasis in ("primary", "secondary", "danger", "neutral")
                for appearance in ("solid", "outline", "soft", "ghost", "plain", "raised")
            ),
            Button("Small", size="sm", id="small"),
            Button("Large", size="lg", id="large"),
            IconButton("Settings", icon="⚙", appearance="outline", id="icon"),
        )
    ).html
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch(headless=True)
        page = browser.new_page(viewport={"width": 1200, "height": 1600})
        page.emulate_media(reduced_motion="reduce")
        for theme in (folio_theme(), classic_theme(), default_theme(), aurora_theme()):
            for mode in ("light", "dark"):
                for source in ("static", "emitted", "bundle"):
                    styles = css if source == "static" else css + emit_theme_css(theme)
                    if source == "bundle":
                        styles = compile_style_bundle(theme=theme, components=("button",)).css
                    page.set_content(
                        f'<html data-theme="{mode}" data-hedron-theme="{theme.name}">'
                        f"<style>{styles}</style><body>{markup}</body></html>"
                    )
                    label = f"{theme.name} {mode} {source}"
                    assert page.evaluate(TEXT_CONTRAST) == [], label
                    for emphasis in ("primary", "secondary", "danger", "neutral"):
                        for appearance in ("solid", "outline", "soft", "ghost", "plain", "raised"):
                            button = page.locator(f"#{emphasis}-{appearance}")
                            button.hover()
                            page.wait_for_timeout(20)
                            assert page.evaluate(TEXT_CONTRAST) == [], (
                                f"{label} {emphasis} {appearance} hover"
                            )
                            disabled = page.locator(f"#disabled-{emphasis}-{appearance}")
                            before = disabled.evaluate(
                                "e => { const s = getComputedStyle(e); "
                                "return [s.color, s.backgroundColor, s.borderColor]; }"
                            )
                            disabled.hover(force=True)
                            page.wait_for_timeout(20)
                            assert (
                                disabled.evaluate(
                                    "e => { const s = getComputedStyle(e); "
                                    "return [s.color, s.backgroundColor, s.borderColor]; }"
                                )
                                == before
                            )
                    assert (
                        page.locator("#large").bounding_box()["height"]
                        > page.locator("#small").bounding_box()["height"]
                    )
                    assert page.locator("#icon").evaluate(
                        "e => getComputedStyle(e).color"
                    ) == page.locator("#primary-outline").evaluate("e => getComputedStyle(e).color")
        browser.close()
