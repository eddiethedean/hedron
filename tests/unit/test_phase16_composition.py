"""Phase 0.16 composition UI."""

from __future__ import annotations

import pytest

from hedron.testing import assert_renders
from hedron_core.diagnostics import HedronError
from hedron_extras.composition import (
    ChoiceCards,
    ChoiceOption,
    FloatingAction,
    FocusScrollRequest,
    KeyboardShortcuts,
    ShortcutBinding,
    SplitPane,
    Steps,
    TreeView,
)
from hedron_extras.recipes import AvatarProfile, BadgeLink, MetricCard, TodoList


def test_choice_cards_and_tree() -> None:
    html = assert_renders(
        ChoiceCards(
            "pick",
            [ChoiceOption(value="a", label="A"), ChoiceOption(value="b", label="B")],
            selected=["a"],
            mark="choices",
        ),
        contains="hedron-choice-cards",
    )
    assert 'type="radio"' in html
    tree_html = assert_renders(
        TreeView(
            [
                {
                    "id": "r",
                    "label": "Root",
                    "children": [{"id": "c", "label": "Child", "children": []}],
                }
            ],
            mark="tree",
        ),
        contains="hedron-tree-view",
    )
    assert 'data-fs-authority="server"' in tree_html


def test_steps_split_fab_shortcuts() -> None:
    steps = assert_renders(Steps(["One", "Two", "Three"], current=1), contains="hedron-steps")
    assert 'method="post"' in steps
    assert_renders(
        SplitPane("left", "right", primary_ratio=0.4, persist_key="main"),
        contains="hedron-split-pane",
    )
    with pytest.raises(ValueError):
        SplitPane("a", "b", min_ratio=0.9, max_ratio=0.1)
    fab = assert_renders(FloatingAction("New", action="create"), contains="hedron-floating-action")
    assert 'method="post"' in fab
    assert_renders(FloatingAction("New", href="/new"), contains="hedron-floating-action")
    assert_renders(
        KeyboardShortcuts([ShortcutBinding(keys="g n", action="new", href="/new")]),
        contains="hedron-keyboard-shortcuts",
    )
    with pytest.raises(ValueError):
        KeyboardShortcuts(
            [
                ShortcutBinding(keys="g n", action="a"),
                ShortcutBinding(keys="G N", action="b"),
            ]
        )
    with pytest.raises(HedronError):
        KeyboardShortcuts([{"keys": "x", "action": "x", "href": "javascript:alert(1)"}])


def test_focus_scroll_rejects_selectors() -> None:
    with pytest.raises(ValueError):
        FocusScrollRequest("#foo")
    assert_renders(FocusScrollRequest("panel-main"), contains="hedron-focus-target")


def test_recipes() -> None:
    assert_renders(AvatarProfile("Ada", caption="Admin"), contains="hedron-avatar-profile")
    assert_renders(BadgeLink("Docs", href="/docs"), contains="hedron-badge-link")
    assert_renders(MetricCard("Users", "12"), contains="hedron-metric-card")
    assert_renders(
        TodoList([{"id": "1", "label": "Ship", "done": False}]),
        contains="hedron-todo-list",
    )
