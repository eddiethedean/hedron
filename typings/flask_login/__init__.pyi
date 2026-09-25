"""Typed subset of Flask-Login used by Hedron's optional Flask adapter."""

from typing import Protocol


class _CurrentUser(Protocol):
    @property
    def is_authenticated(self) -> bool: ...

    def get_id(self) -> str | None: ...


current_user: _CurrentUser
