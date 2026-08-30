from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any

from edron.errors import PhaseError


@dataclass
class Buffer:
    entries: list[Any] = field(default_factory=lambda: list[Any]())
    closed: bool = False

    def append(self, value: Any) -> None:
        if self.closed:
            raise PhaseError(
                "output was emitted after the request phase closed", code="EDRON_LATE_OUTPUT"
            )
        self.entries.append(value)


@dataclass
class Frame:
    app: Any
    page: Any
    phase: str
    request: Any = None
    buffer: Buffer = field(default_factory=Buffer)
    parent: Frame | None = None


_current_frame: ContextVar[Frame | None] = ContextVar("edron_current_frame", default=None)


def current_frame() -> Frame | None:
    return _current_frame.get()


def require_frame(*phases: str) -> Frame:
    frame = current_frame()
    if frame is None:
        raise PhaseError(
            "this Edron operation is only valid during a request", code="EDRON_NO_REQUEST"
        )
    if phases and frame.phase not in phases:
        expected = ", ".join(phases)
        raise PhaseError(
            f"operation is valid during {expected}, not {frame.phase}",
            code="EDRON_WRONG_PHASE",
        )
    return frame


@contextmanager
def frame_context(frame: Frame) -> Generator[Frame, None, None]:
    token = _current_frame.set(frame)
    try:
        yield frame
    finally:
        frame.buffer.closed = True
        _current_frame.reset(token)


def native_request() -> Any:
    return require_frame().request
