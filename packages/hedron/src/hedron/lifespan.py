"""Lifespan composition and registry sealing."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from fastapi import FastAPI

from hedron_core.registry import seal_registry

__all__ = ["compose_lifespan"]

Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def compose_lifespan(user_lifespan: Lifespan | None = None) -> Lifespan:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        seal_registry()
        if user_lifespan is not None:
            async with user_lifespan(app):
                yield
        else:
            yield

    return lifespan
