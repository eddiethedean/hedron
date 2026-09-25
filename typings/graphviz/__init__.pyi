"""Narrow typing for the graphviz source interface used by hedron-charts."""


class Source:
    def __init__(self, source: str, **kwargs: object) -> None: ...

    def pipe(self, *, format: str) -> bytes: ...
