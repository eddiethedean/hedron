from collections.abc import Awaitable, Callable, MutableMapping
from typing import TypeAlias

Scope: TypeAlias = MutableMapping[str, object]
Message: TypeAlias = MutableMapping[str, object]
Receive: TypeAlias = Callable[[], Awaitable[Message]]
Send: TypeAlias = Callable[[Message], Awaitable[None]]
ASGIApp: TypeAlias = Callable[[Scope, Receive, Send], Awaitable[None]]
