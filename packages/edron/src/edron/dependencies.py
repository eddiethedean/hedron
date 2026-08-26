from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from fastapi import Depends

T = TypeVar("T")


@dataclass
class Dependency(Generic[T]):
    provider: Callable[..., T] | None = None
    use_cache: bool = True
    name: str | None = None

    def __set_name__(self, owner: type[Any], name: str) -> None:
        if self.name is None:
            self.name = name

    def __get__(self, instance: Any, owner: type[Any] | None = None) -> Any:
        if instance is None:
            return self
        if self.name in instance.__dict__:
            return instance.__dict__[self.name]
        return self

    def native(self) -> Any:
        return Depends(self.provider, use_cache=self.use_cache)


def dependency(
    provider: Callable[..., T] | None = None, *, use_cache: bool = True
) -> Dependency[T]:
    return Dependency(provider, use_cache=use_cache)
