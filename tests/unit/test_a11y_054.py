"""A11Y-054: accessibility contracts for the phase 0.54 chrome companions.

The chrome ships with the framework, so its accessible semantics have to ship
with it too: skip navigation, live regions for async work, and status text that
does not rely on color alone.
"""

from __future__ import annotations

import re

import pytest

from hedron_core import (
    AppShell,
    Button,
    FlowStep,
    Icon,
    Page,
    ProcessFlow,
    RequestIndicator,
    SkipLink,
    Stack,
    StateView,
    Text,
    render,
)
from hedron_core.builtins.appearance import STATE_KINDS
from hedron_core.diagnostics import HedronError
from hedron_core.icons import register_icon


def _attrs(html: str, needle: str) -> str:
    match = re.search(rf"<[a-z]+[^>]*{re.escape(needle)}[^>]*>", html)
    assert match is not None, f"no element carrying {needle!r}"
    return match.group(0)


def test_skip_link_targets_the_app_shell_main_panel() -> None:
    html = render(
        Page(
            SkipLink(),
            AppShell(body=Stack(Text("body"))),
        )
    ).html
    anchor = _attrs(html, 'class="hedron-skip-link"')
    assert 'href="#main-panel"' in anchor
    assert "Skip to main content" in html
    # The default target has to exist in the shell, or the link goes nowhere.
    assert 'id="main-panel"' in html
    assert html.index("hedron-skip-link") < html.index('id="main-panel"')


def test_skip_link_accepts_other_fragments_but_not_empty_labels() -> None:
    html = render(Page(SkipLink("#report", label="Skip to report"))).html
    assert 'href="#report"' in html
    with pytest.raises(HedronError):
        SkipLink(label="   ")


def test_skip_link_rejects_off_document_targets() -> None:
    with pytest.raises(HedronError):
        SkipLink("javascript:alert(1)")


def test_request_indicator_is_a_polite_live_region() -> None:
    html = render(Page(RequestIndicator(id="global-indicator"))).html
    element = _attrs(html, 'id="global-indicator"')
    assert 'role="status"' in element
    assert 'aria-live="polite"' in element
    # HTMX toggles visibility through its own class; no app CSS or JS required.
    assert "htmx-indicator" in element
    assert "hedron-request-indicator" in element
    assert "Loading…" in html


def test_request_indicator_can_hide_its_label_from_sighted_users() -> None:
    html = render(Page(RequestIndicator("Saving", visible_label=False))).html
    assert "hedron-visually-hidden" in html
    assert "Saving" in html


@pytest.mark.parametrize(
    ("kind", "role"),
    [
        ("loading", "status"),
        ("empty", "status"),
        ("success", "status"),
        ("error", "alert"),
        ("permission", "alert"),
        ("offline", "alert"),
    ],
)
def test_state_view_roles_match_urgency(kind: str, role: str) -> None:
    html = render(Page(StateView(f"{kind} title", kind=kind))).html
    element = _attrs(html, f'data-hedron-state-view="{kind}"')
    assert f'role="{role}"' in element
    assert f"{kind} title" in html


def test_state_view_covers_every_declared_kind() -> None:
    for kind in STATE_KINDS:
        html = render(Page(StateView("t", kind=kind))).html
        assert f'data-hedron-state-view="{kind}"' in html
    with pytest.raises(HedronError):
        StateView("t", kind="confused")


def test_loading_state_announces_itself_as_busy() -> None:
    element = _attrs(
        render(Page(StateView("Loading runs", kind="loading"))).html,
        'data-hedron-state-view="loading"',
    )
    assert 'aria-busy="true"' in element
    assert 'aria-live="polite"' in element


def test_error_state_is_assertive_and_not_busy() -> None:
    element = _attrs(
        render(Page(StateView("Copy failed", kind="error", description="Retry"))).html,
        'data-hedron-state-view="error"',
    )
    assert 'aria-live="assertive"' in element
    assert "aria-busy" not in element


def test_flow_step_status_is_not_conveyed_by_color_alone() -> None:
    html = render(
        Page(
            ProcessFlow(
                FlowStep("Stage", status="complete"),
                FlowStep("Transform", status="current"),
                FlowStep("Publish", status="pending"),
                label="Migration pipeline",
            )
        )
    ).html
    assert 'aria-label="Migration pipeline"' in _attrs(html, 'data-hedron-process-flow="true"')
    assert 'aria-current="step"' in _attrs(html, 'data-hedron-flow-status="current"')
    for text in ("Complete", "In progress", "Not started"):
        assert text in html
    assert html.count("hedron-flow-status") >= 3


def test_flow_step_custom_status_text_replaces_the_default() -> None:
    html = render(
        Page(
            ProcessFlow(
                FlowStep("Verify", status="blocked", status_text="Needs approval"), label="F"
            )
        )
    ).html
    assert "Needs approval" in html
    assert "Blocked" not in html


def test_icon_is_labelled_when_meaningful_and_hidden_when_decorative() -> None:
    register_icon(
        "a11y-054",
        '<svg viewBox="0 0 16 16"><path d="M2 8h12"/></svg>',
        title="Registered title",
        source="tests/unit/test_a11y_054",
    )

    meaningful = _attrs(render(Page(Icon("a11y-054"))).html, 'data-hedron-icon="a11y-054"')
    assert 'role="img"' in meaningful
    assert 'aria-label="Registered title"' in meaningful
    assert "aria-hidden" not in meaningful

    decorative = _attrs(
        render(Page(Icon("a11y-054", decorative=True))).html, 'data-hedron-icon="a11y-054"'
    )
    assert 'aria-hidden="true"' in decorative
    assert "aria-label" not in decorative
    assert 'role="img"' not in decorative

    # An icon inside a labelled control must not double-announce.
    button = render(Page(Button("Copy", leading_icon="a11y-054"))).html
    assert 'aria-hidden="true"' in button
    assert "Copy" in button


def test_appshell_chrome_landmarks_are_labelled() -> None:
    html = render(
        Page(
            AppShell(
                brand=Text("Data Mover"),
                nav_groups={"Operate": [Text("Pipelines")]},
                app_footer=Text("footer"),
                body=Text("body"),
            )
        )
    ).html
    assert 'aria-label="Operate"' in html
    assert "<header" in html
    assert "<footer" in html
    assert "<main" in html
