"""Browser suite note: module-scoped app fixtures reset the registry themselves.

Function-scoped autouse reset in ``tests/conftest.py`` runs *after* module fixtures
are created, so each browser module fixture must call ``reset_registry_for_tests``
before constructing ``Hedron()``.
"""
