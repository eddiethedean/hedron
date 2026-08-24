"""Sample Hedron plugin package."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hedron_conformance.authoring_loop import AuthoringLoopFixture

__version__ = "0.2.1"

__all__ = ["__version__", "authoring_fixture", "list_variants"]


def list_variants() -> tuple[str, ...]:
    """Return the ids of the modular variants present in this installation."""
    from hedron_sample_kit.variants import list_variants as _list_variants

    return _list_variants()


def authoring_fixture() -> AuthoringLoopFixture:
    """Return the shared authoring-loop fixture for this kit."""
    from hedron_sample_kit.authoring import authoring_fixture as _authoring_fixture

    return _authoring_fixture()
