"""Regression coverage for sync handlers wrapped by Hedron routes."""

from __future__ import annotations

import asyncio
import threading

import httpx
from fastapi import FastAPI

from hedron import Hedron, Text
from hedron.routing.route import HedronRoute


def test_sync_page_handler_runs_off_event_loop() -> None:
    async def scenario() -> None:
        app = Hedron(session_secret="sync-route-test-secret")
        loop_thread = threading.get_ident()
        handler_threads: list[int] = []

        @app.page("/")
        def home() -> Text:
            handler_threads.append(threading.get_ident())
            return Text("ok")

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/")

        assert response.status_code == 200
        assert handler_threads == [handler_threads[0]]
        assert handler_threads[0] != loop_thread

    asyncio.run(scenario())


def test_plain_sync_handler_returning_awaitable_is_awaited() -> None:
    async def scenario() -> None:
        app = FastAPI()
        app.router.route_class = HedronRoute

        async def rendered() -> dict[str, bool]:
            await asyncio.sleep(0)
            return {"awaited": True}

        @app.get("/awaitable")
        def endpoint():
            return rendered()

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/awaitable")

        assert response.status_code == 200
        assert response.json() == {"awaited": True}

    asyncio.run(scenario())
