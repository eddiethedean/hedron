"""Chat component tests."""

from __future__ import annotations

from hedron import ChatInput, ChatMessage
from hedron.routing.reverse import ComponentRef
from hedron_core.rendering import render


def test_chat_message_roles() -> None:
    html = render(ChatMessage("Hello", role="user", message_id="m1")).html
    assert "hedron-chat-message" in html
    assert 'data-role="user"' in html or "user" in html
    assert 'id="m1"' in html


def test_chat_status_live_region() -> None:
    html = render(ChatMessage("Thinking…", role="status")).html
    assert 'role="status"' in html
    assert "aria-live" in html or "live" in html


def test_chat_input_explicit_submit() -> None:
    html = render(
        ChatInput(action="/chat", target="#transcript", placeholder="Ask", submit_label="Go")
    ).html
    assert "hedron-chat-input" in html
    assert 'hx-post="/chat"' in html
    assert 'hx-target="#transcript"' in html
    assert "Go" in html


def test_chat_input_preserves_existing_query_string() -> None:
    rendered = render(
        ChatInput(
            ref=ComponentRef(
                logical_id="chat",
                path="/chat?room=1",
                method="POST",
                params={"thread": 2},
            )
        )
    ).html

    assert 'hx-post="/chat?room=1&amp;thread=2"' in rendered
    assert "?room=1?thread=2" not in rendered
