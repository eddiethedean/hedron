"""#278: notebook preview must signal started only after the server is listening."""

from __future__ import annotations

import sys
import time
import types

from hedron_notebook.preview import _UvicornThreadServer


def test_preview_server_sets_started_after_listen(monkeypatch) -> None:
    order: list[str] = []

    class FakeConfig:
        def __init__(self, *args: object, **kwargs: object) -> None:
            del args, kwargs

    class FakeServer:
        def __init__(self, config: object) -> None:
            del config
            self.started = False
            self.should_exit = False

        def run(self) -> None:
            order.append("run")
            self.started = True
            while not self.should_exit:
                time.sleep(0.01)

    monkeypatch.setitem(
        sys.modules,
        "uvicorn",
        types.SimpleNamespace(Config=FakeConfig, Server=FakeServer),
    )
    server = _UvicornThreadServer(app=object(), host="127.0.0.1", port=8765)
    server.start()
    try:
        assert order == ["run"]
        assert server._started.is_set()
        assert getattr(server._server, "started", False) is True
    finally:
        server.shutdown()
