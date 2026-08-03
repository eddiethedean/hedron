"""Snapshot tests for deterministic HTML output."""

from __future__ import annotations

from hedron_core import (
    Alert,
    Button,
    Card,
    Form,
    FormField,
    Heading,
    Page,
    RenderMode,
    Stack,
    SubmitButton,
    Table,
    Text,
    TextInput,
    render,
)


def test_page_snapshot(snapshot) -> None:
    page = Page(
        Stack(
            Heading("Users", level=1),
            Table(
                headers=["Name", "Email"],
                rows=[["Ada", "ada@example.com"], ["Grace", "grace@example.com"]],
                caption="Team members",
            ),
            Card(
                Form(
                    FormField(
                        name="name",
                        label="Name",
                        control=TextInput("name"),
                        required=True,
                    ),
                    SubmitButton("Create"),
                ),
                title="Create user",
            ),
            Alert("Saved", tone="success"),
            Button("Refresh"),
        ),
        title="Team Admin",
    )
    result = render(page, mode=RenderMode.PAGE)
    assert result.html == snapshot


def test_fragment_snapshot(snapshot) -> None:
    result = render(Card(Text("Hello <world>"), title="Greeting"))
    assert result.html == snapshot
