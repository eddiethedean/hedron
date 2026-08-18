"""#330: explicit-path class decorators must copy class host/fallback attrs."""

from __future__ import annotations

from tests.unit._helpers_044 import make_app, reset_044

from hedron import CommandHandler, RefreshableView, Text
from hedron_core.hosts import FragmentHost


def setup_function() -> None:
    reset_044()


def test_explicit_path_refreshable_copies_class_attrs() -> None:
    app = make_app()

    @app.refreshable("/status-panel")
    class DecoratedStatus(RefreshableView[None, str]):
        fallback = "/home"
        loading = Text("please wait")
        error = Text("boom")
        host = FragmentHost(tag="section")

        def load(self) -> str:
            return "ok"

        def render(self, data: str):
            return Text(data)

    assert DecoratedStatus.path == "/status-panel"
    assert DecoratedStatus.fallback == "/home"
    assert DecoratedStatus.host.props.tag == "section"
    assert DecoratedStatus.host._loading is not None
    assert DecoratedStatus.host._error is not None


def test_explicit_path_command_copies_class_fallback() -> None:
    app = make_app()

    @app.command("/do-ping")
    class DecoratedPing(CommandHandler[None, object]):
        fallback = "/home"

        def execute(self):
            return Text("pong")

    assert DecoratedPing.fallback == "/home"
    assert DecoratedPing.path == "/do-ping"
