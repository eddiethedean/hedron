"""Helpers for phase 0.49 FastAPI/Pydantic tests."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from fastapi.testclient import TestClient
from tests.unit._helpers_044 import csrf_headers as csrf_headers_044
from tests.unit._helpers_044 import make_app, reset_044

from hedron import Hedron

__all__ = ["csrf_headers", "make_app", "reset_044", "reset_049", "with_client"]


def reset_049() -> None:
    reset_044()


def csrf_headers(
    client: TestClient,
    path: str | None = None,
    *,
    htmx: bool = True,
) -> dict[str, str]:
    del path
    return csrf_headers_044(client, htmx=htmx)


@contextmanager
def with_client(app: Hedron) -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client
