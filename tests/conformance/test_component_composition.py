from __future__ import annotations

import re

import pytest

from hedron import ComponentRef, Lazy, Poll
from hedron_core import render
from hedron_core.builtins import (
    Card,
    Container,
    Form,
    FormField,
    Grid,
    Heading,
    Inline,
    RadioGroup,
    Stack,
    SubmitButton,
    Tabs,
    Text,
    TextInput,
)
from hedron_core.color_mode import ColorModeToggle


def _attribute_values(html: str, name: str) -> list[str]:
    return re.findall(rf'\b{name}="([^"]+)"', html)


def test_container_components_share_children_id_and_class_conventions() -> None:
    component = Container(
        children=[
            Stack(children=[Text("One"), Text("Two")], id="activity", class_="compact"),
            Inline(children=[Text("Three")], class_="actions"),
            Grid(children=[Card(children=[Text("Four")])], columns=1, class_="cards"),
        ],
        id="workspace",
        class_="wide",
    )

    html = render(component).html

    assert 'id="workspace" class="hedron-container wide"' in html
    assert 'id="activity" class="hedron-stack compact"' in html
    assert 'class="hedron-inline actions"' in html
    assert 'class="hedron-grid cards"' in html
    assert html.index("One") < html.index("Two") < html.index("Three") < html.index("Four")


def test_nested_form_controls_stay_in_renderer_and_get_unique_relationships() -> None:
    component = Form(
        children=[
            FormField(
                name="email",
                label="Primary email",
                control=TextInput("email", type="email"),
                help="Used for receipts.",
                required=True,
            ),
            FormField(
                name="email",
                label="Backup email",
                control=TextInput("email", type="email"),
                error="Use a different address.",
            ),
            SubmitButton("Save"),
        ]
    )

    result = render(component)
    ids = _attribute_values(result.html, "id")

    assert len(ids) == len(set(ids))
    for target in _attribute_values(result.html, "for"):
        assert target in ids
    for described_by in _attribute_values(result.html, "aria-describedby"):
        assert set(described_by.split()).issubset(ids)
    assert sum("TextInput#" in key for key in result.identity_map) == 2
    assert 'aria-required="true"' in result.html
    assert 'aria-invalid="true"' in result.html


def test_tabs_generate_unique_ids_and_resolved_aria_links_when_nested() -> None:
    component = Stack(
        Tabs(("Overview", Text("First")), ("History", Text("Second"))),
        Card(Tabs(panels=[("Overview", Text("Nested")), ("Settings", Text("Preferences"))])),
    )

    html = render(component).html
    ids = _attribute_values(html, "id")

    assert len(ids) == len(set(ids))
    for relationship in ("aria-controls", "aria-labelledby"):
        for target in _attribute_values(html, relationship):
            assert target in ids


def test_tabs_reject_ambiguous_labels_and_unknown_active_panel() -> None:
    with pytest.raises(ValueError, match="must be unique"):
        Tabs(("Same", "One"), ("Same", "Two"))
    with pytest.raises(ValueError, match="Unknown active tab"):
        Tabs(("One", "Content"), active="Missing")


def test_repeated_self_targeting_and_labelled_components_do_not_collide() -> None:
    ref = ComponentRef(logical_id="activity.latest", path="/activity")
    component = Stack(
        ColorModeToggle(),
        ColorModeToggle(),
        RadioGroup("plan", "Primary plan", [("free", "Free"), ("pro", "Pro")]),
        RadioGroup("plan", "Backup plan", [("free", "Free"), ("pro", "Pro")]),
        Lazy(ref=ref),
        Lazy(ref=ref),
        Poll(ref=ref),
        Poll(ref=ref),
    )

    html = render(component).html
    ids = _attribute_values(html, "id")

    assert len(ids) == len(set(ids))
    for target in _attribute_values(html, "for"):
        assert target in ids
    for target in _attribute_values(html, "hx-target"):
        assert target.startswith("#")
        assert target[1:] in ids


def test_generated_form_ids_normalize_unsafe_field_names() -> None:
    html = render(
        FormField(
            name="billing email[]",
            label="Billing email",
            control=TextInput("billing email[]"),
        )
    ).html

    assert 'id="field-billing-email-' in html
    assert "billing email[]" not in " ".join(_attribute_values(html, "id"))


def test_formfield_applies_aria_to_custom_controls_and_preserves_caller_describedby() -> None:
    from hedron_core.component import Component
    from hedron_core.html import html
    from hedron_core.models import Props

    class CustomProps(Props):
        id: str | None = None
        name: str = "x"

    class CustomControl(Component[CustomProps]):
        props_type = CustomProps

        def __init__(self, name: str = "x", **kwargs: object) -> None:
            super().__init__(CustomProps(name=name, **kwargs))  # type: ignore[arg-type]

        def render(self):  # type: ignore[no-untyped-def]
            return html.input(type="text", name=self.props.name, id=self.props.id)

    custom = render(
        FormField(
            name="nick",
            label="Nickname",
            control=CustomControl("nick"),
            help="Visible to teammates.",
            required=True,
        )
    ).html
    assert 'aria-describedby="' in custom
    assert 'aria-required="true"' in custom

    preserved = render(
        FormField(
            name="email",
            label="Email",
            control=TextInput("email", aria_describedby="external-hint"),
        )
    ).html
    assert "external-hint" in preserved


def test_radio_group_sets_root_fieldset_id() -> None:
    html = render(
        RadioGroup("plan", "Plan", [("free", "Free"), ("pro", "Pro")], id="plan-group")
    ).html
    assert 'id="plan-group"' in html


def test_layout_gap_emits_css_variable() -> None:
    html = render(Stack(Text("a"), Text("b"), gap="1.25rem")).html
    assert "--hedron-gap: 1.25rem" in html
    assert 'data-hedron-gap="1.25rem"' in html


def test_representative_application_tree_composes_without_diagnostics() -> None:
    component = Container(
        Stack(
            Heading("Team settings", level=1),
            Grid(
                Card(Text("Current plan: Pro"), title="Account"),
                Card(
                    Form(
                        FormField(
                            name="team_name",
                            label="Team name",
                            control=TextInput("team_name"),
                        ),
                        SubmitButton("Update team"),
                    ),
                    title="Profile",
                ),
                columns=2,
            ),
            Tabs(("Members", Text("12 members")), ("Invites", Text("2 pending"))),
        ),
        id="team-settings",
    )

    result = render(component)

    assert not result.diagnostics
    assert 'id="team-settings"' in result.html
    assert "Team settings" in result.html
    assert "Update team" in result.html
