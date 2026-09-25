"""Narrow typing for the graph interface used by hedron-charts."""

from collections.abc import Iterable


class Graph:
    @property
    def nodes(self) -> Iterable[object]: ...

    @property
    def edges(self) -> Iterable[tuple[object, object]]: ...
