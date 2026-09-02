"""Deterministic bounded manifest search."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .manifest import SiteManifest


@dataclass(frozen=True, slots=True)
class SearchResult:
    path: str
    title: str
    description: str
    score: int


def search(
    manifest: SiteManifest, query: str, *, limit: int = 20, max_length: int = 200
) -> tuple[SearchResult, ...]:
    if type(limit) is not int or limit < 0:
        raise ValueError("search result limit must be a non-negative integer")
    if type(max_length) is not int or max_length < 1:
        raise ValueError("search query length must be a positive integer")
    query = query.strip()
    if not query:
        return ()
    if len(query) > max_length:
        raise ValueError(f"search query exceeds {max_length} characters")
    terms = tuple(term for term in re.findall(r"[\w-]+", query.casefold()) if term)
    if not terms:
        return ()
    results: list[SearchResult] = []
    for page in manifest.pages:
        title = page.title.casefold()
        haystack = page.search_text.casefold()
        score = sum((8 if term in title else 0) + (2 if term in haystack else 0) for term in terms)
        if score:
            results.append(SearchResult(page.path, page.title, page.description, score))
    return tuple(
        sorted(results, key=lambda item: (-item.score, item.title.casefold(), item.path))[:limit]
    )
