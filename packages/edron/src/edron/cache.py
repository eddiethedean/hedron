from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from functools import wraps
from threading import RLock
from typing import Any, ParamSpec, TypeVar

from edron.errors import BindingError

P = ParamSpec("P")
R = TypeVar("R")


class CachedFunction:
    def __init__(
        self,
        fn: Callable[..., Any],
        *,
        ttl: float | None = None,
        scope: str = "private",
        max_entries: int = 128,
    ) -> None:
        if scope not in {"private", "tenant", "public"}:
            raise BindingError(
                "cache scope must be private, tenant, or public", code="EDRON_CACHE_SCOPE"
            )
        self.fn = fn
        self.ttl = ttl
        self.scope = scope
        self.max_entries = max_entries
        self._values: OrderedDict[Any, Any] = OrderedDict()
        self._lock = RLock()
        wraps(fn)(self)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        key = (args, tuple(sorted(kwargs.items())))
        with self._lock:
            if key in self._values:
                self._values.move_to_end(key)
                return self._values[key]
        value = self.fn(*args, **kwargs)
        with self._lock:
            self._values[key] = value
            self._values.move_to_end(key)
            while len(self._values) > self.max_entries:
                self._values.popitem(last=False)
        return value

    def invalidate(self, *args: Any, **kwargs: Any) -> None:
        with self._lock:
            self._values.pop((args, tuple(sorted(kwargs.items()))), None)

    def invalidate_all(self) -> None:
        with self._lock:
            self._values.clear()


def cache_data(
    *, ttl: float | None = None, scope: str = "private", max_entries: int = 128
) -> Callable[[Callable[P, R]], CachedFunction]:
    return lambda fn: CachedFunction(fn, ttl=ttl, scope=scope, max_entries=max_entries)
