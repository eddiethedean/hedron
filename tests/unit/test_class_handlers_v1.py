"""Branch and failure-path coverage for canonical class handlers."""

from __future__ import annotations

import inspect

import pytest

from hedron import CommandHandler, RefreshableView, Text
from hedron.type_authoring.classes import (
    class_config_conflict,
    compile_command_class,
    compile_view_class,
)
from hedron_core.diagnostics import HedronError


@pytest.mark.anyio
async def test_view_class_supports_async_load_empty_and_sync_render() -> None:
    class AsyncView(RefreshableView[str, list[str]]):
        empty = Text("empty")

        async def load(self, query: str = "") -> list[str]:
            return [query] if query else []

        def render(self, data: list[str]) -> object:
            return Text(data[0])

    endpoint = compile_view_class(AsyncView)
    assert await endpoint("") is AsyncView.empty
    rendered = await endpoint("ready")
    assert isinstance(rendered, Text)
    assert list(inspect.signature(endpoint).parameters) == ["query"]
    assert endpoint.__hedron_handler_class__ is AsyncView


@pytest.mark.anyio
async def test_view_class_rejects_async_render() -> None:
    class InvalidView(RefreshableView[None, str]):
        def load(self) -> str:
            return "ready"

        async def render(self, data: str) -> object:
            return Text(data)

    with pytest.raises(HedronError, match="render must be deterministic"):
        await compile_view_class(InvalidView)()


@pytest.mark.anyio
async def test_command_class_supports_sync_and_async_execute() -> None:
    class SyncCommand(CommandHandler[str, str]):
        def execute(self, value: str) -> str:
            return value.upper()

    class AsyncCommand(CommandHandler[str, str]):
        async def execute(self, value: str) -> str:
            return value.upper()

    assert await compile_command_class(SyncCommand)("ok") == "OK"
    assert await compile_command_class(AsyncCommand)("ok") == "OK"


@pytest.mark.parametrize(
    "target,compiler,message",
    [
        (RefreshableView(), compile_view_class, "Shared handler instance"),
        (object, compile_view_class, "Not a RefreshableView"),
        (RefreshableView, compile_view_class, "Incomplete RefreshableView"),
        (CommandHandler(), compile_command_class, "Shared handler instance"),
        (object, compile_command_class, "Not a CommandHandler"),
        (CommandHandler, compile_command_class, "Incomplete CommandHandler"),
    ],
)
def test_class_compilers_reject_invalid_targets(
    target: object,
    compiler: object,
    message: str,
) -> None:
    with pytest.raises(HedronError, match=message):
        compiler(target)  # type: ignore[operator]


def test_class_configuration_conflicts_fail_closed() -> None:
    class Configured(CommandHandler[None, object]):
        fallback = "/class"
        path = "/class-action"

        def execute(self) -> object:
            return Text("ok")

    with pytest.raises(HedronError, match="fallback conflict"):
        class_config_conflict(
            Configured,
            decorator_fallback="/decorator",
            decorator_path=None,
        )
    with pytest.raises(HedronError, match="path conflict"):
        class_config_conflict(
            Configured,
            decorator_fallback=None,
            decorator_path="/decorator-action",
        )


@pytest.mark.parametrize("value", [None, "", b"", {}, [], ()])
@pytest.mark.anyio
async def test_view_empty_values_use_declared_empty_surface(value: object) -> None:
    class EmptyView(RefreshableView[None, object]):
        empty = Text("empty")

        def load(self) -> object:
            return value

        def render(self, data: object) -> object:
            return Text(str(data))

    assert await compile_view_class(EmptyView)() is EmptyView.empty
