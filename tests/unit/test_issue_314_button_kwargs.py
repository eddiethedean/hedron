"""#314: Refresh and ActionHandle.button must render extra button attrs."""

from __future__ import annotations

import pytest
from tests.unit._helpers_043 import make_app

from hedron import Text
from hedron_core.codes import HED_HOST_0001
from hedron_core.diagnostics import HedronError
from hedron_core.rendering import render


def test_refresh_and_command_button_forward_class() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    @app.command(fallback="/")
    def ping():
        return Text("pong")

    refresh_html = render(status.refresh_button("Go", class_="primary").render()).html
    assert 'class="primary"' in refresh_html
    command_html = render(ping.button("Go", class_="primary")).html
    assert 'class="primary"' in command_html


def test_button_rejects_event_handler_attrs() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    with pytest.raises(HedronError, match=HED_HOST_0001):
        status.refresh_button("Go", onclick="alert(1)").render()
