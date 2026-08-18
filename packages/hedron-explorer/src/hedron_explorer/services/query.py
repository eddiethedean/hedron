"""Cursor pagination and truncation diagnostics for Explorer tables."""

from __future__ import annotations

import html as html_lib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar
from urllib.parse import urlencode

from fastapi import Request

from hedron_core.codes import HED_EXPLORER_0001

T = TypeVar("T")

DEFAULT_LIMIT = 50
MAX_LIMIT = 200
COMPONENTS_LIMIT = 200
A11Y_LIMIT = 40
AUDIT_LIMIT = 20
CACHE_LIMIT = 50


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int
    next_cursor: str | None
    truncated: bool
    diagnostic: str | None


def parse_limit(
    request: Request | None, *, default: int = DEFAULT_LIMIT, cap: int = MAX_LIMIT
) -> int:
    if request is None:
        return default
    raw = request.query_params.get("limit")
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(1, min(value, cap))


def parse_cursor(request: Request | None) -> int:
    if request is None:
        return 0
    raw = request.query_params.get("cursor") or request.query_params.get("offset")
    if raw is None:
        return 0
    try:
        return max(0, int(raw))
    except ValueError:
        return 0


def paginate(items: Sequence[T], *, offset: int, limit: int) -> Page[T]:
    total = len(items)
    start = min(offset, total)
    end = min(start + limit, total)
    sliced = list(items[start:end])
    truncated = end < total or start > 0
    next_cursor = str(end) if end < total else None
    diagnostic = HED_EXPLORER_0001 if truncated or total > limit else None
    return Page(
        items=sliced,
        total=total,
        limit=limit,
        offset=start,
        next_cursor=next_cursor,
        truncated=truncated,
        diagnostic=diagnostic,
    )


def search_filter(items: Sequence[T], query: str | None, key: Callable[[T], str]) -> list[T]:
    if not query:
        return list(items)
    needle = query.strip().lower()
    if not needle:
        return list(items)
    return [item for item in items if needle in str(key(item)).lower()]


def _page_href(request: Request, *, cursor: int) -> str:
    params = [(key, value) for key, value in request.query_params.multi_items() if key != "offset"]
    filtered = [(key, value) for key, value in params if key != "cursor"]
    if cursor:
        filtered.append(("cursor", str(cursor)))
    qs = urlencode(filtered)
    path = str(request.url.path)
    return f"{path}?{qs}" if qs else path


def truncation_banner(page: Page[T], *, noun: str, request: Request | None = None) -> str:
    if not page.truncated and page.total <= page.limit:
        return ""
    nxt = f" cursor={page.next_cursor}" if page.next_cursor else ""
    code = page.diagnostic or HED_EXPLORER_0001
    links: list[str] = []
    if request is not None:
        if page.offset > 0:
            prev = max(0, page.offset - page.limit)
            href = html_lib.escape(_page_href(request, cursor=prev), quote=True)
            links.append(f"<a rel='prev' href='{href}'>Previous</a>")
        if page.next_cursor is not None:
            href = html_lib.escape(_page_href(request, cursor=int(page.next_cursor)), quote=True)
            links.append(f"<a rel='next' href='{href}'>Next</a>")
    nav = f" {' '.join(links)}" if links else ""
    return (
        f"<p role='status'><code>{code}</code> Showing {len(page.items)} of {page.total} {noun}"
        f" (limit={page.limit}{nxt}). Use cursor pagination; tables are not unbounded.{nav}</p>"
    )


def envelope(page: Page[T]) -> dict[str, object]:
    return {
        "items": page.items,
        "total": page.total,
        "limit": page.limit,
        "offset": page.offset,
        "next_cursor": page.next_cursor,
        "truncated": page.truncated,
        "diagnostic": page.diagnostic,
    }


def wants_envelope(request: Request | None, page: Page[T] | None = None) -> bool:
    if request is None:
        return False
    if page is not None and (page.truncated or page.total > page.limit or page.diagnostic):
        return True
    return request.query_params.get("envelope") in {"1", "true", "yes"} or (
        request.query_params.get("cursor") is not None
        or request.query_params.get("limit") is not None
    )
