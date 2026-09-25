"""Narrow typing for the axe-playwright-python surface used by browser hooks."""


class _AxeResults:
    response: object


class Axe:
    def run(self, page: object) -> _AxeResults: ...
