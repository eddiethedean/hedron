"""Chat accessibility smoke."""

from __future__ import annotations

from hedron import ChatInput, ChatMessage
from hedron_core.rendering import render


def test_chat_input_labels_control() -> None:
    html = render(ChatInput(action="/c")).html
    assert "<label" in html
    assert "<textarea" in html


def test_chat_message_status_announced() -> None:
    html = render(ChatMessage("ok", role="assistant", status="Sent")).html
    assert "hedron-chat-status" in html
    assert 'role="status"' in html
