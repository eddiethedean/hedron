"""Minimal ``pkg_resources`` shim for Posit Connect 2025.06.

Connect 2025.06's FastAPI worker (``connect_fastapi_runtime.py``) does
``from pkg_resources import parse_version`` before importing user code.
setuptools 82+ removed that module, so a current content environment
crashes at worker start with ``ModuleNotFoundError: pkg_resources``.

This shim provides only ``parse_version`` via ``packaging.version``. Real
setuptools ``<82`` still takes precedence when present.
"""

from __future__ import annotations

from packaging.version import parse as parse_version

__all__ = ["parse_version"]
