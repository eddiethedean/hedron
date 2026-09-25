"""Local typed boundaries for dynamic framework and socket APIs."""

from __future__ import annotations

from typing import Protocol, cast


class _SocketNameReader(Protocol):
    def getsockname(self) -> tuple[object, ...]: ...


def dynamic_attribute(value: object, name: str, default: object = None) -> object:
    try:
        return cast(object, getattr(value, name))
    except AttributeError:
        return default


def bound_socket_port(sock: object) -> int:
    address = cast(_SocketNameReader, sock).getsockname()
    port = address[1]
    if isinstance(port, int) and not isinstance(port, bool):
        return port
    raise OSError("socket did not report an integer port")
