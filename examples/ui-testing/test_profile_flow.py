"""An ordinary pytest test using native Playwright and Hedron's managed host."""

from __future__ import annotations

import os
from urllib.request import urlopen

import pytest
from playwright.sync_api import expect

from hedron.testing._ui_testing.host import ManagedASGIHost
from hedron.testing.browser_scenario import (
    AmbiguousSettleError,
    BrowserScenarioFactory,
    ManagedHostError,
)

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("HEDRON_BROWSER") != "1",
        reason="Opt-in browser evidence: set HEDRON_BROWSER=1 and install Chromium",
    ),
]


def test_profile_validation_and_save(hedron_ui: BrowserScenarioFactory) -> None:
    with hedron_ui.from_app(
        "hedron.testing.examples.profile_app:create_app",
        config={"title": "Profile settings", "root_path": "/account"},
        root_path="/account",
    ) as ui:
        ui.page.goto(ui.url)
        name = ui.page.get_by_label("Display Name")
        expect(ui.page.get_by_role("heading", name="Profile settings")).to_be_visible()
        expect(ui.page.get_by_role("button", name="Save profile")).to_be_visible()

        cursor = ui.checkpoint()
        with ui.expect_http(method="POST", path="/account/profile", status=422, since=cursor):
            name.fill("Al")
            name.press("Enter")
            result = ui.settle(since=cursor, target="hedron-errors")
        assert result.status == 422
        expect(ui.page.locator("#hedron-validation-errors")).to_contain_text(
            "Please correct the highlighted fields"
        )
        expect(name).to_be_focused()

        cursor = ui.checkpoint()
        with ui.expect_http(method="POST", path="/account/profile", status=200, since=cursor):
            name.fill("Ada Lovelace")
            name.press("Enter")
            result = ui.settle(since=cursor, target="hedron-errors")
        assert result.status == 200
        expect(ui.region("hedron-errors")).to_have_text("Saved Ada Lovelace")


def test_profile_factory_rejects_live_values(hedron_ui: BrowserScenarioFactory) -> None:
    with pytest.raises(ManagedHostError, match=r"startup failed \(ValueError\)"):
        hedron_ui.from_app(
            "hedron.testing.examples.profile_app:create_app",
            config={"title": ""},
        ).__enter__()


def test_external_loopback_scenario_leaves_server_owned_by_caller(
    hedron_ui: BrowserScenarioFactory,
) -> None:
    host = ManagedASGIHost(
        "hedron.testing.examples.profile_app:create_app",
        config={"title": "Caller-owned profile"},
    )
    base_url = host.start()
    try:
        with hedron_ui.from_url(base_url) as ui:
            assert ui.capabilities["server_exception_channel"] == "unavailable"
            ui.page.goto(ui.url)
            expect(ui.page.get_by_role("heading", name="Caller-owned profile")).to_be_visible()

        with urlopen(f"{base_url}/_ui-testing/ready", timeout=5) as response:
            assert response.status == 200
    finally:
        host.close()


@pytest.mark.browser_context_args(java_script_enabled=False)
def test_native_form_submission_works_without_javascript(hedron_ui: BrowserScenarioFactory) -> None:
    with hedron_ui.from_app("hedron.testing.examples.profile_app:create_app") as ui:
        ui.page.goto(ui.url)
        ui.page.get_by_label("Display Name").fill("Ada Lovelace")
        ui.page.get_by_role("button", name="Save profile").click()
        expect(ui.page.get_by_text("Saved Ada Lovelace")).to_be_visible()


def test_settle_ignores_background_poll_before_user_action(
    hedron_ui: BrowserScenarioFactory,
) -> None:
    with hedron_ui.from_app("hedron.testing.examples.profile_app:create_app") as ui:
        ui.page.goto(ui.url)
        ui.page.evaluate(
            """() => {
              const region = document.createElement('div');
              region.id = 'settle-region';
              region.textContent = 'Initial';
              document.body.append(region);
              const poll = document.createElement('button');
              poll.id = 'settle-poll';
              poll.textContent = 'Poll';
              poll.setAttribute('hx-get', '/account/poll');
              poll.setAttribute('hx-trigger', 'poll-now');
              poll.setAttribute('hx-target', '#settle-region');
              document.body.append(poll);
              const action = document.createElement('button');
              action.textContent = 'Save action';
              action.setAttribute('hx-get', '/account/action');
              action.setAttribute('hx-trigger', 'click');
              action.setAttribute('hx-target', '#settle-region');
              document.body.append(action);
              htmx.process(region);
              htmx.process(poll);
              htmx.process(action);
            }"""
        )
        ui.page.route("**/account/poll", lambda route: route.fulfill(status=204))
        ui.page.route(
            "**/account/action",
            lambda route: route.fulfill(
                status=200,
                content_type="text/html",
                body="<span>Saved from the user action</span>",
            ),
        )

        cursor = ui.checkpoint()
        with ui.page.expect_response("**/account/poll"):
            ui.page.evaluate("htmx.trigger(document.querySelector('#settle-poll'), 'poll-now')")
        with ui.page.expect_response("**/account/action"):
            ui.page.get_by_role("button", name="Save action").click()

        result = ui.settle(since=cursor, target="settle-region")

        assert result.status == 200
        assert result.swapped is True
        expect(ui.region("settle-region")).to_contain_text("Saved from the user action")


def test_settle_requires_generation_for_overlapping_same_target_actions(
    hedron_ui: BrowserScenarioFactory,
) -> None:
    with hedron_ui.from_app("hedron.testing.examples.profile_app:create_app") as ui:
        ui.page.goto(ui.url)
        ui.page.evaluate(
            """() => {
              const region = document.createElement('div');
              region.id = 'overlap-region';
              document.body.append(region);
              for (const generation of [1, 2]) {
                const button = document.createElement('button');
                button.id = `overlap-${generation}`;
                button.textContent = `Action ${generation}`;
                button.setAttribute('hx-get', `/account/action-${generation}`);
                button.setAttribute('hx-trigger', 'click');
                button.setAttribute('hx-target', '#overlap-region');
                button.setAttribute('data-hedron-action-generation', String(generation));
                document.body.append(button);
                htmx.process(button);
              }
              htmx.process(region);
            }"""
        )
        ui.page.route(
            "**/account/action-*",
            lambda route: route.fulfill(status=204),
        )

        cursor = ui.checkpoint()
        with ui.page.expect_response("**/account/action-1"):
            ui.page.get_by_role("button", name="Action 1").click()
        with ui.page.expect_response("**/account/action-2"):
            ui.page.get_by_role("button", name="Action 2").click()

        with pytest.raises(AmbiguousSettleError, match="pass generation"):
            ui.settle(since=cursor, target="overlap-region")
        result = ui.settle(since=cursor, target="overlap-region", generation=2)

        assert result.generation == 2
        assert result.status == 204
