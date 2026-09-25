from collections.abc import MutableMapping
from typing import Protocol


class _CurrentApplication(Protocol):
    extensions: MutableMapping[str, object]


current_app: _CurrentApplication
